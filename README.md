# Feast Demo: Credit Card Fraud Detection

A simple, end-to-end demo showing how to use **Feast** (a Feature Store) for credit card fraud detection.

## 📋 Overview

This use case simulates a realistic ML workflow with Feast:

1. **Offline Store** – Stores historical features for model training
2. **Online Store** – Serves fresh, low-latency features for real-time prediction
3. **Feature Registry** – Centralizes feature metadata and versioning

**Dataset:** [Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) (284,807 transactions, 492 frauds)

---

## 🏗️ Project Structure

```
feast-fraud-detection/
├── data/                           # Raw & processed data
│   ├── creditcard.csv             # Raw Kaggle CSV
│   └── processed_data.parquet     # Cleaned data with timestamp + ID
│
├── feature_repo/                   # Feast Feature Repository
│   ├── feature_store.yaml         # Feast config (registry, online store)
│   ├── fraud_features.py          # Entities, Feature Views, sources
│   └── data/                      # Feast internal state
│       ├── registry.db            # Feature Registry (SQLite)
│       └── online_store.db        # Online Store (SQLite)
│
├── download_data.py               # [1] Download dataset from Kaggle
├── prepare_data.py                # [2] Add event_timestamp & transaction_id
├── train_model.py                 # [3] Train with historical features
├── predict_online.py              # [4] Predict with online features
├── requirements.txt               # Dependencies
└── README.md                      # You are here
```

---

## 🚀 Quickstart

### Step 0 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 1 — Download & Prepare Data

```bash
# Download from Kaggle
python download_data.py

# Create event_timestamp & transaction_id; save to Parquet
python prepare_data.py
```

Output: `data/processed_data.parquet`

### Step 2 — Initialize the Feature Store

```bash
cd feature_repo
feast apply
cd ..
```

This will:

* Parse `fraud_features.py` and register your feature definitions
* Create the Feature Registry at `feature_repo/data/registry.db`
* Validate `feature_store.yaml`

### Step 3 — Train the Model

```bash
python train_model.py
```

What it does:

1. Pulls **historical features** via `get_historical_features()` (point-in-time correct)
2. Trains a Logistic Regression model
3. Saves the model to `fraud_model.pkl`

### Step 4 — Materialize Features (to Online Store)

```bash
cd feature_repo
feast materialize-incremental $(date -u +"%Y-%m-%dT%H:%M:%S")
cd ..
```

**IMPORTANT:** This loads features from the Offline Store (Parquet) into the Online Store (SQLite) so that real-time serving works.

**Alternative (if your shell doesn’t support the date command):**

```bash
cd feature_repo
feast materialize 2020-01-01T00:00:00 2025-12-31T23:59:59
cd ..
```

### Step 5 — Online Prediction

```bash
python predict_online.py
```

What it does:

1. Fetches **online features** via `get_online_features()`
2. Runs inference to flag suspected fraudulent transactions

---

## 📚 Feast Concepts Used in This Demo

### 1 Entity (`fraud_features.py`)

```python
transaction = Entity(
    name="transaction_id",
    value_type=ValueType.STRING,
    description="ID of a credit card transaction",
)
```

* An **Entity** is the primary key for features (here, `transaction_id`).

### 2 Feature View (`fraud_features.py`)

```python
transaction_features_v1 = FeatureView(
    name="transaction_features_v1",
    entities=[transaction],
    schema=[Field(name=f"V{i}", dtype=Float32) for i in range(1, 29)] +
           [Field(name="Amount", dtype=Float32)],
    source=fraud_data_source,
    online=True,  # Enable online serving
    ttl=timedelta(days=365),
)
```

* Groups related features (`V1`–`V28`, `Amount`)
* `online=True` enables serving from the Online Store
* `ttl` controls time-to-live for online features

### 3 File Source (`fraud_features.py`)

```python
fraud_data_source = FileSource(
    path="../data/processed_data.parquet",
    timestamp_field="event_timestamp",
)
```

* Defines the Offline Store (historical training data)

### 4 Feature Store Config (`feature_store.yaml`)

```yaml
project: fraud_detection_demo
registry: data/registry.db        # SQLite registry
provider: local
online_store:
    type: sqlite                   # SQLite online store
    path: data/online_store.db
```

---

## 🔄 Detailed Workflow

### Training Flow (Offline)

```
processed_data.parquet (Offline Store)
    ↓
get_historical_features()  ← entity_df (transaction_ids + timestamps)
    ↓
Training DataFrame (V1–V28, Amount)
    ↓
Train Model → fraud_model.pkl
```

### Serving Flow (Online)

```
processed_data.parquet
    ↓  feast materialize
Online Store (SQLite) — keyed by transaction_id
    ↓
get_online_features()  ← entity_rows (transaction_ids)
    ↓
Real-time Features
    ↓
Prediction
```