import os
import re

def lowercase_links_in_markdown(content):
    # Match [text](URL)
    def replace_link(match):
        text = match.group(1)
        url = match.group(2)
        return f"[{text}]({url.lower()})"
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, content)

def clean_front_matter(content):
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            front_matter = parts[1]
            body = parts[2]

            # Remove 'tags:' line
            new_front_matter_lines = []
            found_status = False
            for line in front_matter.strip().split('\n'):
                if line.strip().lower().startswith('tags:'):
                    continue  # skip tags line
                if line.strip().lower().startswith('status:'):
                    found_status = True
                new_front_matter_lines.append(line)
            
            # Add status if not present
            if not found_status:
                new_front_matter_lines.append('status: published')

            new_front_matter = '\n'.join(new_front_matter_lines)
            return f"---\n{new_front_matter}\n---{body}"
    
    # No front matter found — add new front matter
    return f"---\nstatus: published\n---\n{content}"

def process_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    content = lowercase_links_in_markdown(content)
    content = clean_front_matter(content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ Processed: {file_path}")

def process_markdown_files_in_folder(folder_path):
    for root, _, files in os.walk(folder_path):
        print(f"Processing folder: {root}")
        print(f"🔍 Processing folder: {root}")
        print(f"Files found: {files}")
        for filename in files:
            if filename.lower().endswith(".md"):
                file_path = os.path.join(root, filename)
                process_markdown_file(file_path)
                print(f"Processed file: {file_path}")

# 👉 Replace this with your actual folder path
def main():
    folder_path = "./test"
    print(f"Starting to process markdown files in folder: {folder_path}")
    process_markdown_files_in_folder(folder_path)

if __name__ == "__main__":
    main()