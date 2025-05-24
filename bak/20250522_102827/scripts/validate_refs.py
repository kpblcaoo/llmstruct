import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def validate_references():
    try:
        refs = json.load(Path("data/references.json").open())
        ideas = json.load(Path("data/ideas.json").open())
        conversions = {idea["id"]: idea.get("converted_to") for idea in ideas["ideas"] if idea.get("converted_to")}
        broken_links = []
        updated_refs = refs["references"].copy()
        
        for i, ref in enumerate(refs["references"]):
            source_id = ref["source"]["id"]
            target_id = ref["target"]["id"]
            source_file = Path(ref["source"]["file"])
            target_file = Path(ref["target"]["file"])
            
            if not source_file.exists() or not target_file.exists():
                broken_links.append((source_id, target_id))
                continue
                
            if source_id in conversions:
                logger.info(f"Redirecting {source_id} to {conversions[source_id]}")
                updated_refs[i]["source"]["id"] = conversions[source_id]
            
        if broken_links:
            logger.warning(f"Broken links found: {broken_links}")
        else:
            logger.info("All references valid")
            
        with Path("data/references.json").open("w", encoding="utf-8") as f:
            json.dump({"references": updated_refs}, f, indent=2)
            
    except Exception as e:
        logger.error(f"Validation failed: {e}")

def main():
    validate_references()

if __name__ == "__main__":
    main()
