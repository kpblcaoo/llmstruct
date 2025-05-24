import json
from pathlib import Path

def load_json_files(base_dir: Path) -> dict:
    result = {}
    for path in sorted(base_dir.rglob("*.json")):
        rel = path.relative_to(base_dir)
        parts = rel.parts

        # Спускаемся по частям пути
        current = result
        for part in parts[:-1]:
            current = current.setdefault(part, {})

        # Последняя часть — файл
        with path.open("r", encoding="utf-8") as f:
            current[parts[-1]] = json.load(f)
    return result

# Пример использования
base = Path.cwd()  # или путь к твоему проекту
merged = {
    "data": load_json_files(base / "data"),
    "schema": load_json_files(base / "schema")
}

# Сохраняем или выводим
with open("merged.json", "w", encoding="utf-8") as f:
    json.dump(merged, f, indent=2, ensure_ascii=False)
