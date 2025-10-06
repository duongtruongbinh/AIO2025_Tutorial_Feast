import pandas as pd
from feast import FeatureStore
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib

# 1. LẤY DỮ LIỆU TRAINING TỪ OFFLINE STORE CỦA FEAST
store = FeatureStore(repo_path="feature_repo")

# entity_df chứa danh sách các thực thể và timestamp của sự kiện
entity_df_source = pd.read_parquet("data/processed_data.parquet")
entity_df = entity_df_source[['event_timestamp', 'transaction_id', 'is_fraud']]

# Định nghĩa các feature cần lấy
feature_names = [f"transaction_features_v1:V{i}" for i in range(1, 29)]
feature_names.append("transaction_features_v1:Amount")

print("Lấy dữ liệu training từ Offline Store...")
training_data = store.get_historical_features(
    entity_df=entity_df,
    features=feature_names,
).to_df()

# 2. HUẤN LUYỆN MÔ HÌNH
print("\nBắt đầu huấn luyện mô hình...")
y = training_data['is_fraud']
X = training_data.drop(columns=['event_timestamp', 'transaction_id', 'is_fraud'], axis=1)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
model = LogisticRegression(max_iter=1000).fit(X_train, y_train)

print("\n--- Kết quả đánh giá mô hình ---")
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred, target_names=['Hợp lệ', 'Gian lận']))

# 3. LƯU MODEL
print("\nLưu model vào file 'fraud_model.pkl'...")
joblib.dump(model, 'fraud_model.pkl')