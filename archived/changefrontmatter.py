import os
import re

import os
import re

def normalize_front_matter(folder_path):
    front_matter_re = re.compile(r"^---\n(.*?)\n---", re.DOTALL)

    for filename in os.listdir(folder_path):
        if not filename.endswith(".md"):
            continue

        file_path = os.path.join(folder_path, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        match = front_matter_re.match(content)
        if not match:
            continue  # no front matter

        front_matter = match.group(1)
        lines = front_matter.splitlines()
        new_lines = []

        has_featured = False
        has_archived = False

        for line in lines:
            stripped = line.strip()

            # Remove status entirely
            if stripped.startswith("status:"):
                continue

            # Quote title
            if stripped.startswith("title:"):
                key, value = stripped.split(":", 1)
                value = value.strip()
                if not (value.startswith('"') and value.endswith('"')):
                    value = f'"{value}"'
                new_lines.append(f"{key}: {value}")
                continue

            # Quote date
            if stripped.startswith("date:"):
                key, value = stripped.split(":", 1)
                value = value.strip()
                if not (value.startswith('"') and value.endswith('"')):
                    value = f'"{value}"'
                new_lines.append(f"{key}: {value}")
                continue

              # Quote category
            if stripped.startswith("category:"):
                key, value = stripped.split(":", 1)
                value = value.strip()
                if not (value.startswith('"') and value.endswith('"')):
                    value = f'"{value}"'
                new_lines.append(f"{key}: {value}")
                continue

            if stripped.startswith("featured:"):
                has_featured = True

            if stripped.startswith("archived:"):
                has_archived = True

            new_lines.append(line)

        if not has_featured:
            new_lines.append("featured: true")

        if not has_archived:
            new_lines.append("archived: true")

        updated_front_matter = "\n".join(new_lines)
        new_content = content.replace(front_matter, updated_front_matter, 1)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"Updated: {filename}")

if __name__ == "__main__":
    folder_path = "./blogger"
    normalize_front_matter(folder_path)