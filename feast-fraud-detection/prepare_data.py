import pandas as pd
from datetime import datetime, timedelta

df = pd.read_csv('data/creditcard.csv')

print("Tạo dữ liệu timestamp giả lập...")
now = datetime.now()
df['event_timestamp'] = df['Time'].apply(lambda x: now - timedelta(seconds=x))
df['transaction_id'] = df.index.astype(str)

print("Định dạng lại các cột...")
df.rename(columns={'Class': 'is_fraud'}, inplace=True)
final_df = df[[
    'event_timestamp', 'transaction_id',
    'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10',
    'V11', 'V12', 'V13', 'V14', 'V15', 'V16', 'V17', 'V18', 'V19', 'V20',
    'V21', 'V22', 'V23', 'V24', 'V25', 'V26', 'V27', 'V28',
    'Amount', 'is_fraud'
]]

print(f"Lưu trữ dữ liệu đã xử lý vào 'data/processed_data.parquet'...")
final_df.to_parquet('data/processed_data.parquet', index=False)