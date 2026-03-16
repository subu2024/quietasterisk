import json
import os
import re

JSON_FILE = "article_summaries.json"        # path to your json file
POSTS_FOLDER = "./blogger_markdown"        # folder containing markdown files

def update_front_matter(file_path, title, summary):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Match YAML front matter
    match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not match:
        print(f"No front matter found in {file_path}")
        return

    front_matter = match.group(1)
    body = content[match.end():]

    lines = front_matter.split("\n")
    new_lines = []
    excerpt_added = False

    for line in lines:
        if line.startswith("title:"):
            new_lines.append(f'title: "{title}"')
        elif line.startswith("date:"):
            # remove single quotes from date
            cleaned = line.replace("'", "")
            new_lines.append(cleaned)
        elif line.startswith("excerpt:"):
            new_lines.append(f'excerpt: "{summary}"')
            excerpt_added = True
        else:
            new_lines.append(line)

    if not excerpt_added:
        new_lines.append(f'excerpt: "{summary}"')

    new_front_matter = "---\n" + "\n".join(new_lines) + "\n---\n"
    new_content = new_front_matter + body

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Updated: {file_path}")


def main():
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        filename = item["filename"]
        title = item["title"]
        summary = item["excerpt"]

        file_path = os.path.join(POSTS_FOLDER, filename)

        if os.path.exists(file_path):
            update_front_matter(file_path, title, summary)
        else:
            print(f"File not found: {file_path}")


if __name__ == "__main__":
    main()