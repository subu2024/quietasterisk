import os
import uuid
import re

def normalize_filenames(folder_path):
    for filename in os.listdir(folder_path):
        old_path = os.path.join(folder_path, filename)

        if not os.path.isfile(old_path):
            continue

        name, ext = os.path.splitext(filename)

        # lowercase and replace spaces with dash
        normalized_name = name.lower().replace(" ", "-")

        # remove any character that is not a-z, 0-9, _, or -
        normalized_name = re.sub(r"[^a-z0-9_-]", "", normalized_name)

        # combine with extension (lowercase)
        normalized = normalized_name + ext.lower()
        new_path = os.path.join(folder_path, normalized)

        # If it's already correct, skip
        if filename == normalized:
            continue

        # Case-only rename on macOS needs a temp step
        if os.path.exists(new_path):
            # If same file but different casing
            if filename.lower() == normalized.lower():
                temp_name = f".tmp_{uuid.uuid4().hex}"
                temp_path = os.path.join(folder_path, temp_name)

                os.rename(old_path, temp_path)
                os.rename(temp_path, new_path)
                print(f"Fixed case: {filename} → {normalized}")
            else:
                print(f"⚠️ Skipping duplicate: {filename}")
            continue

        os.rename(old_path, new_path)
        print(f"Renamed: {filename} → {normalized}")



if __name__ == "__main__":
    folder = "./blogger"
    normalize_filenames(folder)