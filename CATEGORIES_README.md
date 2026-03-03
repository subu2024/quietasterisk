# Categories System Guide

## Overview
The blog now uses a two-level category system:
1. **Categories landing page** (`categories.html`) - Overview of all categories
2. **Individual category pages** (`category-{slug}.html`) - Full list of posts per category with "Load More"

## How It Works

### Categories Landing Page
- Shows all categories as clickable cards
- Displays category name, description, and post count
- Each card links to its dedicated category page

### Individual Category Pages
- Shows all posts in that category
- Displays first 10 posts initially
- "Load More" button reveals next 10 posts
- Button updates with remaining count
- Back navigation to categories page

## categories.json Format

Create a `categories.json` file in your project root:

```json
{
  "Category Name": {
    "description": "A description of what this category covers"
  }
}
```

### Example

```json
{
  "Essays": {
    "description": "Explorations of meaning, systems, and the patterns that shape how we think."
  },
  "Philosophy": {
    "description": "Questions about truth, meaning, and understanding reality."
  },
  "Stories": {
    "description": "Narratives that illuminate and reveal through human experience."
  }
}
```

### Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| Category Name (key) | Yes | Must exactly match the `category` field in your markdown posts |
| `description` | Yes | Brief description shown on the categories landing page |

### Important Notes

1. **Category names must match exactly** - If your post has `category: Essays`, then your categories.json must have `"Essays"` as a key
2. **Case sensitive** - "Essays" ≠ "essays"
3. **Missing categories** - If a category isn't in categories.json, it will use a default description: "Essays exploring {category}"

## Front Matter Format

Your markdown posts should have a category field:

```markdown
---
title: "Your Post Title"
date: 2025-01-15
category: Essays
featured: true
excerpt: "Brief description..."
---

Your content here...
```

The `category` value determines which category page the post appears on.

## Generated Files

### Main Categories Page
- **File**: `output/categories.html`
- **Content**: Grid of category cards
- **Links to**: Individual category pages

### Individual Category Pages
- **Files**: `output/category-{slug}.html`
- **Examples**:
  - `category-essays.html`
  - `category-philosophy.html`
  - `category-stories.html`
- **Content**: All posts in that category (10 at a time)

## URL Structure

```
categories.html
├── category-essays.html (Essays category)
├── category-philosophy.html (Philosophy category)
├── category-stories.html (Stories category)
└── category-reflection.html (Reflection category)
```

## Navigation Flow

```
Home → Categories → [Select Category] → Category Page → Individual Post
  ↓         ↓              ↓                  ↓              ↓
index → categories → category-essays → (load more) → post.html
```

## Usage Example

### Step 1: Create categories.json

```json
{
  "Essays": {
    "description": "Deep explorations of meaning and systems"
  },
  "Stories": {
    "description": "Narratives that illuminate the human experience"
  }
}
```

### Step 2: Tag Your Posts

```markdown
---
title: "On Beginnings"
category: Essays
---
```

```markdown
---
title: "The Long Game"
category: Stories
---
```

### Step 3: Generate

```bash
python make_blog_v7.py
```

### Result

- `categories.html` - Shows "Essays (12)" and "Stories (8)" cards
- `category-essays.html` - Shows 10 Essays posts with "Load More (2 remaining)"
- `category-stories.html` - Shows 8 Stories posts (no button, all visible)

## Customization

### Change Descriptions
Edit `categories.json`:
```json
{
  "Essays": {
    "description": "Your new description here"
  }
}
```

### Add New Category
1. Add to `categories.json`:
```json
{
  "New Category": {
    "description": "Description of new category"
  }
}
```

2. Tag posts with the new category:
```markdown
---
category: New Category
---
```

3. Regenerate blog

### Remove Category
Simply stop using it in your posts. Empty categories won't appear.

## Load More Behavior

- **≤10 posts**: All posts shown, no button
- **11-20 posts**: Shows 10, button says "Load More (X remaining)"
- **21+ posts**: Shows 10, click to reveal next 10, repeats until all shown

## Styling

Category pages use the same design system:
- Warm editorial aesthetic
- Rust accent colors
- Card-based layouts
- Responsive grid
- Hover effects

## File Structure

```
your-project/
├── make_blog_v7.py
├── categories.json          # Category descriptions
├── books.json
├── blogger_markdown_posts/
│   ├── post1.md            # category: Essays
│   ├── post2.md            # category: Stories
│   └── ...
└── output/
    ├── index.html
    ├── categories.html      # Landing page
    ├── category-essays.html # Essays category page
    ├── category-stories.html
    └── ...
```

## Tips

1. **Keep descriptions concise** - 1-2 sentences work best on the cards
2. **Use consistent categories** - Stick to 4-6 main categories for clarity
3. **Descriptive names** - Use clear category names: "Essays", "Stories", not "Misc", "Other"
4. **Test load more** - Create 15+ posts in a category to test the load more feature
5. **Check spelling** - Category names in posts must exactly match categories.json keys

## Troubleshooting

**Problem**: Category not showing on categories page
- **Solution**: Make sure you have at least one post with that category

**Problem**: Category shows "Essays exploring {category}"
- **Solution**: Add the category to categories.json with a proper description

**Problem**: Wrong slug in URL
- **Solution**: Category slugs are auto-generated. "System Thinking" becomes "system-thinking"

**Problem**: Load More not working
- **Solution**: Check browser console for JavaScript errors, ensure script is loaded
