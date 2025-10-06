from feast import FeatureStore
import pandas as pd
import joblib

# 1. TẢI MODEL VÀ KẾT NỐI STORE
model = joblib.load('fraud_model.pkl')
store = FeatureStore(repo_path="feature_repo")

# 2. LẤY FEATURE ONLINE TỪ FEAST VỚI CÁC ID GIAO DỊCH MỚI
new_transaction_ids = ["284802", "284803", "284804", "284805", "284806"]
entity_rows = [{"transaction_id": tid} for tid in new_transaction_ids]

feature_names = [f"transaction_features_v1:V{i}" for i in range(1, 29)]
feature_names.append("transaction_features_v1:Amount")

print(f"Lấy online features cho các transaction IDs: {new_transaction_ids}...")
online_features = store.get_online_features(
    features=feature_names,
    entity_rows=entity_rows
).to_dict()

# 3. CHUẨN BỊ DỮ LIỆU VÀ DỰ ĐOÁN
features_df = pd.DataFrame.from_dict(online_features)
feature_order = [f.split(":")[1] for f in feature_names]
X_predict = features_df[feature_order]
predictions = model.predict(X_predict)

# 4. HIỂN THỊ KẾT QUẢ
for i, tid in enumerate(new_transaction_ids):
    prediction_label = "GIAN LẬN" if predictions[i] == 1 else "Hợp lệ"
    print(f"Giao dịch ID {tid}: {prediction_label}")