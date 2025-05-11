import json
import os
import uuid

def save_graph(data: dict,sessionID: str) -> str:
    # Debug: show current working dir
    print("Working directory:", os.getcwd())

    # Use absolute & normalized path
    base_dir = os.path.abspath(".")
    output_folder = os.path.join(base_dir, "memory", "sessions")
    os.makedirs(output_folder, exist_ok=True)  # Force creation if missing

    uid = str(uuid.uuid4())
    filename = f"{uid}.json"
    filepath = os.path.normpath(os.path.join(output_folder, filename))

    print(f"Saving to: {filepath}")

    # Actually save the file
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return filepath



# def save_memmory(data: dict, output_folder: str = "./snapshots") -> str:
#     # Create output folder if it doesn't exist
#     os.makedirs(output_folder, exist_ok=True)

#     # Generate unique file name
#     uid = str(uuid.uuid4())
#     filename = f"{uid}.txt"
#     filepath = os.path.join(output_folder, filename)

#     # Save JSON data as text
#     with open(filepath, "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=2)

#     return filepath
