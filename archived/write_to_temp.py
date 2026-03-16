import os
from pathlib import Path

def combine_markdown_to_txt(input_folder, output_file):
    input_path = Path(input_folder)

    with open(output_file, "w", encoding="utf-8") as outfile:
        for md_file in sorted(input_path.glob("*.md")):
            with open(md_file, "r", encoding="utf-8") as infile:
                content = infile.read()

            # Optional: add filename separator
            outfile.write(f"\n===== {md_file.name} =====\n\n")
            outfile.write(content)
            outfile.write("\n\n")

    print(f"All markdown files combined into: {output_file}")


# Example usage
input_folder = "./blogger_markdown"
output_file = "combined_output.txt"

combine_markdown_to_txt(input_folder, output_file)