import os
import shutil
import kagglehub
os.makedirs("data", exist_ok=True)
os.environ["KAGGLEHUB_CACHE"] = "data"

path = kagglehub.dataset_download("mlg-ulb/creditcardfraud")

csv_path = None
for root, dirs, files in os.walk(path):
    for file in files:
        if file.endswith(".csv"):
            src = os.path.join(root, file)
            dst = os.path.join("data", file)
            shutil.move(src, dst)
            csv_path = dst

for item in os.listdir("data"):
    if item != os.path.basename(csv_path):
        item_path = os.path.join("data", item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)
print(f"Dữ liệu đã được lưu tại: {csv_path}")