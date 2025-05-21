import json
import os
from glob import glob
from collections import defaultdict

folder = "clean"
seen = set()
merged = []

def normalize(record):
    # Нормализуем ID и структуру
    id = record.get("id") or record.get("ID") or record.get("name")
    content = record.get("description") or record.get("text") or ""
    return {
        "id": id.strip() if isinstance(id, str) else str(id),
        "description": content.strip(),
        "tags": record.get("tags", []),
        "type": record.get("type") or "idea"
    }

for path in glob(os.path.join(folder, "*.json")):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):  # Иногда файл — словарь
                data = [data]
            for entry in data:
                norm = normalize(entry)
                key = (norm["id"], norm["description"])
                if key not in seen:
                    seen.add(key)
                    merged.append(norm)
    except Exception as e:
        print(f"⚠️ Failed to load {path}: {e}")

# Сохраняем результат
with open("merged.json", "w", encoding="utf-8") as out:
    json.dump(merged, out, indent=2, ensure_ascii=False)
print(f"✅ Merged {len(merged)} entries into merged.json")
