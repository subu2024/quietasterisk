# Downloads Feature Guide

## Overview

The blog generator now supports a `downloads/` directory for hosting downloadable files (PDFs, ebooks, spreadsheets, etc.) that will be automatically copied to your generated site.

## How It Works

When you run `python generate_blog.py`, the generator will:
1. Look for a `downloads/` directory in your project root
2. Copy all files and subdirectories to `output/downloads/`
3. Preserve the directory structure
4. Log how many files were copied

## Setup

### 1. Create Downloads Directory

```bash
mkdir downloads
```

### 2. Add Your Files

Place any downloadable files in the `downloads/` directory:

```
my-blog/
├── downloads/
│   ├── my-ebook.pdf
│   ├── research-paper.pdf
│   ├── resources/
│   │   ├── template.xlsx
│   │   └── guide.docx
│   └── code/
│       └── sample-script.py
├── generate_blog.py
├── config.py
└── ...
```

### 3. Generate Blog

```bash
python generate_blog.py
```

Output will include:
```
my-blog/
└── output/
    ├── index.html
    ├── downloads/        # ← All files copied here
    │   ├── my-ebook.pdf
    │   ├── research-paper.pdf
    │   ├── resources/
    │   │   ├── template.xlsx
    │   │   └── guide.docx
    │   └── code/
    │       └── sample-script.py
    └── ...
```

## Linking to Downloads in Posts

You can link to downloadable files in your markdown posts:

```markdown
---
title: "My Post with Downloads"
date: 2025-03-03
category: Essays
---

Check out my [free ebook](downloads/my-ebook.pdf) for more details.

Download the [research paper](downloads/research-paper.pdf).

Here's a [helpful template](downloads/resources/template.xlsx) to get started.
```

## Use Cases

### 1. Ebooks and PDFs
```
downloads/
├── ebook-chapter-1.pdf
├── ebook-chapter-2.pdf
└── complete-ebook.pdf
```

Link in post:
```markdown
Download the [complete ebook](downloads/complete-ebook.pdf) (PDF, 2.5MB).
```

### 2. Code Samples
```
downloads/
└── code/
    ├── example-1.py
    ├── example-2.js
    └── README.md
```

Link in post:
```markdown
Get the [Python example](downloads/code/example-1.py).
```

### 3. Resources and Templates
```
downloads/
└── templates/
    ├── blog-post-template.md
    ├── pitch-deck-template.pptx
    └── budget-spreadsheet.xlsx
```

Link in post:
```markdown
Use this [blog post template](downloads/templates/blog-post-template.md).
```

### 4. Research Papers
```
downloads/
└── papers/
    ├── 2024-research-study.pdf
    └── 2025-whitepaper.pdf
```

Link in post:
```markdown
Read the full [research study](downloads/papers/2024-research-study.pdf).
```

## Features

### ✅ Preserves Directory Structure
Subdirectories in `downloads/` are maintained in `output/downloads/`.

### ✅ Preserves File Metadata
Uses `shutil.copy2()` to preserve modification times and permissions.

### ✅ Recursive Copying
Automatically copies all nested files and folders.

### ✅ Safe Operation
- Skips if `downloads/` doesn't exist (no errors)
- Creates necessary directories automatically
- Logs warnings if individual files fail to copy

### ✅ Logging
Shows how many files were copied:
```
INFO - Copying downloadable files...
INFO - Copied 12 file(s) from downloads directory
```

## Configuration

The downloads directory paths are defined in `config.py`:

```python
DOWNLOADS_DIR = Path("./downloads")           # Source directory
OUTPUT_DOWNLOADS_DIR = OUTPUT_DIR / "downloads"  # Destination
```

To change the source directory:

```python
DOWNLOADS_DIR = Path("./my-files")  # Use ./my-files instead
```

To change the output location:

```python
OUTPUT_DOWNLOADS_DIR = OUTPUT_DIR / "files"  # Output to /files instead
```

## Best Practices

### 1. Organize by Type
```
downloads/
├── pdfs/
├── ebooks/
├── templates/
└── code/
```

### 2. Use Descriptive Names
❌ `file1.pdf`, `doc.docx`  
✅ `introduction-guide.pdf`, `monthly-budget-template.docx`

### 3. Keep Files Reasonably Sized
- Compress large PDFs
- Optimize images in PDFs
- Consider splitting very large files

### 4. Include README
Add a `README.md` in `downloads/` to document what's there:

```markdown
# Downloads Directory

## Contents
- `/ebooks/` - Free ebook downloads
- `/templates/` - Productivity templates
- `/code/` - Code examples from blog posts
```

### 5. Version Your Files
```
downloads/
├── my-ebook-v1.pdf
├── my-ebook-v2.pdf     # Updated version
└── my-ebook-latest.pdf # Symlink or copy of latest
```

## Security Considerations

### ✅ Safe Files
- PDFs
- Office documents (DOC, XLS, PPT)
- Text files (TXT, MD, CSV)
- Code files (PY, JS, HTML, CSS)
- Images (JPG, PNG, SVG)

### ⚠️ Be Careful With
- Executable files (.exe, .app, .sh)
- Archives (.zip, .tar.gz) - scan for malware
- Scripts that run on download

### 🛡️ Recommendations
1. **Scan files for viruses** before adding to downloads
2. **Don't include sensitive data** (passwords, API keys, personal info)
3. **Check file permissions** - ensure files aren't executable unless intended
4. **Review before deploying** - verify all files in output/downloads/

## Troubleshooting

### Downloads directory not found
**Message:** `Downloads directory ./downloads does not exist. Skipping.`

**Solution:** This is normal if you don't have a downloads directory. Create one:
```bash
mkdir downloads
```

### Files not copied
**Problem:** Files in `downloads/` but not in `output/downloads/`

**Check:**
1. Run with verbose logging: Check console output
2. Verify file permissions: `ls -la downloads/`
3. Check for symlinks: Use real files, not symlinks
4. Look for error messages in logs

### Broken links in blog posts
**Problem:** Link `[file](downloads/doc.pdf)` returns 404

**Solutions:**
- Verify file exists in `downloads/doc.pdf`
- Regenerate blog: `python generate_blog.py`
- Check path is relative: Use `downloads/file.pdf` not `/downloads/file.pdf`

### Large files slow generation
**Problem:** Blog takes long time to generate with large files

**Solutions:**
1. Compress large PDFs (use PDF optimization tools)
2. Exclude from git: Add `downloads/` to `.gitignore`
3. Use external hosting for very large files (>10MB)
4. Reference external URLs instead of copying locally

## Example: Complete Setup

### Project Structure
```
my-blog/
├── downloads/
│   ├── ebooks/
│   │   └── my-guide.pdf
│   ├── templates/
│   │   └── worksheet.xlsx
│   └── README.md
├── blogger_markdown_posts/
│   └── post-with-downloads.md
├── generate_blog.py
└── config.py
```

### Post Content
```markdown
---
title: "Resources and Downloads"
date: 2025-03-03
category: Resources
---

## Free Downloads

### Ebooks
- [Complete Guide to Blogging](downloads/ebooks/my-guide.pdf) (PDF, 1.2MB)

### Templates
- [Content Planning Worksheet](downloads/templates/worksheet.xlsx) (Excel)

All files are free to download and use!
```

### Generated Output
```
output/
├── index.html
├── downloads/
│   ├── ebooks/
│   │   └── my-guide.pdf
│   ├── templates/
│   │   └── worksheet.xlsx
│   └── README.md
└── post-with-downloads.html
```

### Result
Users can click links in the blog post to download files directly!

## Advanced: Custom Download Locations

If you want downloads in a different location per post, you can create subdirectories:

```
downloads/
├── post-1/
│   └── resources.pdf
├── post-2/
│   └── template.xlsx
└── shared/
    └── ebook.pdf
```

Link in posts:
```markdown
<!-- In post 1 -->
[Resources for this post](downloads/post-1/resources.pdf)

<!-- In post 2 -->
[Template](downloads/post-2/template.xlsx)

<!-- Shared across posts -->
[Free ebook](downloads/shared/ebook.pdf)
```

## Integration with Books

You can use the downloads feature for book samples:

```
downloads/
└── books/
    ├── space-between-knowing-sample.pdf
    └── quiet-asterisk-chapter1.pdf
```

Reference in `books.json`:
```json
{
  "title": "Space Between Knowing",
  "description": "...",
  "link": "https://amazon.com/...",
  "sample": "downloads/books/space-between-knowing-sample.pdf"
}
```

Then link to sample in the books page or posts!

---

**Remember:** The downloads feature automatically runs every time you generate your blog. No extra steps needed!
