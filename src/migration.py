import os
import json
import requests
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]

# Configuration
API_URL = os.environ.get("LLMWIKI_API_URL", "http://127.0.0.1:8001")
MEMORY_ROOT = Path(os.environ.get("LOOPSMITH_MEMORY_ROOT", str(WORKSPACE_ROOT / "memory")))
LOG_FILE = Path(os.environ.get("LOOPSMITH_MIGRATION_LOG", str(WORKSPACE_ROOT / "org" / "migration_log.jsonl")))

def migrate_file(file_path):
    print(f"Migrating {file_path}...")
    try:
        content = file_path.read_text(encoding="utf-8")
        payload = {
            "title": file_path.name,
            "content": content,
            "external_id": f"migration_{file_path.name}",
            "source_type": "workspace_memory",
            "source_ref": str(file_path)
        }
        res = requests.post(f"{API_URL}/documents", json=payload)
        res.raise_for_status()
        return {"file": str(file_path), "status": "success", "id": res.json().get("id")}
    except Exception as e:
        return {"file": str(file_path), "status": "error", "error": str(e)}

def main():
    # Target files to migrate
    targets = list(MEMORY_ROOT.glob("*.md")) + list(MEMORY_ROOT.glob("**/*.md"))
    # Remove duplicates and filter out internal logs if necessary
    targets = list(set(targets))
    
    results = []
    for target in targets:
        res = migrate_file(target)
        results.append(res)
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(res) + "\n")
            
    print(f"Migration complete. {len(results)} files processed.")

if __name__ == "__main__":
    main()
