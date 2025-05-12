import json
import os
import uuid

def create_session() -> str:
    base_dir = os.path.abspath(".")
    output_folder = os.path.join(base_dir, "memory", "sessions")
    os.makedirs(output_folder, exist_ok=True)  # Force creation if missing
    uid = str(uuid.uuid4())
    filename = f"{uid}.json"
    filepath = os.path.normpath(os.path.join(output_folder, filename))
    data = {
        "session_id": uid,
        "messages": [],
    }
    # Actually save the file
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return uid