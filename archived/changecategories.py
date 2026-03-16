import os
import json
import string
import yaml
import re

# Folder containing your blog markdown files
BLOG_FOLDER = "blogger"  # replace with your folder path
# Mapping JSON file
MAPPING_FILE = "blog_title_category.json"

def normalize_title(title: str) -> str:
    title = title.lower().strip()
    # remove punctuation
    title = title.translate(str.maketrans('', '', string.punctuation))
    return title

def load_mapping(mapping_file):
    """Load JSON mapping and normalize titles."""
    with open(mapping_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Build dictionary with normalized titles
    mapping = {normalize_title(entry["title"]): entry["category"] for entry in data}
    return mapping

def update_blog_categories(blog_folder, mapping):
    for filename in os.listdir(blog_folder):
        if not filename.endswith(".md"):
            continue
        filepath = os.path.join(blog_folder, filename)
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Match YAML front matter
        match = re.match(r'^(---\n.*?---\n)', content, re.DOTALL)
        if not match:
            print(f"No front matter found in {filename}, skipping.")
            continue
        
        front_matter = match.group(1)
        body = content[len(front_matter):]

        # Strip the leading and trailing --- before loading YAML
        fm_content = front_matter.strip('-\n')
        try:
            fm_dict = yaml.safe_load(fm_content)
        except yaml.YAMLError as e:
            print(f"Error parsing YAML in {filename}: {e}")
            continue
        
        if not fm_dict or "title" not in fm_dict:
            print(f"No title in front matter of {filename}, skipping.")
            continue

        title_norm = normalize_title(fm_dict["title"])
        print(f"Processing '{filename}' with title '{fm_dict['title']}' (normalized '{title_norm}')...")

        if title_norm not in mapping:
            print(f"No category mapping found for '{fm_dict['title']}' (normalized '{title_norm}'), skipping.")
            continue

        # Ensure category is saved as a quoted string
        fm_dict["category"] = mapping[title_norm]

        # Custom representer to always quote the category string
        def str_representer(dumper, data):
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')
        yaml.add_representer(str, str_representer)

        print(f"Setting category '{mapping[title_norm]}' for '{fm_dict['title']}'.")

        # Rebuild front matter with proper --- markers
        new_front_matter = "---\n" + yaml.safe_dump(fm_dict, sort_keys=False) + "---\n"

        # Save updated markdown
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_front_matter + body)

        print(f"Updated '{filename}' with category '{mapping[title_norm]}'.")

if __name__ == "__main__":
    mapping = load_mapping(MAPPING_FILE)
    update_blog_categories(BLOG_FOLDER, mapping)
    print("All files updated!")
