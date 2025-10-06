from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource, ValueType
from feast.types import Float32

# 1. Định nghĩa nguồn dữ liệu offline
fraud_data_source = FileSource(
    path="../data/processed_data.parquet",
    timestamp_field="event_timestamp",
)

# 2. Định nghĩa thực thể (Entity)
transaction = Entity(
    name="transaction_id",
    value_type=ValueType.STRING,
    description="ID of a credit card transaction",
)

# 3. Định nghĩa Feature View để nhóm các đặc trưng
transaction_features_v1 = FeatureView(
    name="transaction_features_v1",
    entities=[transaction],
    ttl=timedelta(days=365),
    schema=[
        Field(name=f"V{i}", dtype=Float32) for i in range(1, 29)
    ] + [
        Field(name="Amount", dtype=Float32),
    ],
    source=fraud_data_source,
    online=True,
    description="Anonymized transaction features and transaction amount",
    tags={"owner": "fraud_detection_team", "version": "1"},
)