# Books Page Setup Guide

## Overview
The updated blog generator now includes a dedicated Books page that showcases all your published works with a beautiful, modern design matching the rest of the site.

## Features
- **Dedicated Books page** (`books.html`) accessible from main navigation
- **Homepage preview** showing first 3 books with "View All Books" button
- **Grouping by type** (optional) - Books, Poetry, Upcoming, etc.
- **Full descriptions** on the books page
- **Beautiful card layout** matching the essay design system
- **Buy buttons** linking to external stores

## books.json Format

Create a `books.json` file in your project root with the following structure:

```json
[
  {
    "title": "Book Title",
    "description": "Full description of the book...",
    "image": "book-cover.jpg",
    "link": "https://amazon.com/your-book"
  }
]
```

### Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| `title` | Yes | The book title |
| `description` | Yes | Book description (truncated to 150 chars on homepage, full on books page) |
| `image` | No | Filename of book cover image (place in same directory as script or in ./images/) |
| `link` | No | URL to purchase the book. Use empty string `""` if not available yet |

### Optional Advanced Fields

You can also include these optional fields for more control:

| Field | Description |
|-------|-------------|
| `author` | Author name (useful for anthologies or guest authors) |
| `year` | Publication year |
| `type` | Category type for grouping: "Books", "Poetry", "Upcoming", etc. |

## Usage

### 1. Create books.json
Place your `books.json` file in the same directory as the Python script.

### 2. Add Book Cover Images
Place book cover images in an `images/` directory or reference them with the correct path in the JSON file. The script will automatically copy them to the output directory.

### 3. Run the Generator
```bash
python make_blog_v7.py
```

The script will:
- Generate `output/books.html` with all books
- Show first 3 books on homepage with "View All" button
- Copy all book cover images to `output/images/`
- Add "Books" link to navigation header and footer

## Navigation Structure

After generation, your site will have:
- **Essays** (index.html) - Homepage with featured/recent essays
- **Books** (books.html) - All books page
- **Categories** (categories.html) - Essays grouped by category
- **About** (about.html) - About page

## Book Types / Grouping (Optional)

If you want to group books into sections on the books page, add a `type` field:

```json
[
  { "title": "Book 1", "description": "...", "type": "Books", ... },
  { "title": "Poem Collection", "description": "...", "type": "Poetry", ... },
  { "title": "Upcoming Work", "description": "...", "type": "Upcoming", ... }
]
```

This will create separate sections on the books page. Without the `type` field, all books are shown together in a single grid (which works great for most cases).

## Example books.json

```json
[
  {
    "title": "Space Between Knowing",
    "description": "A reflective exploration of thoughts, uncertainty, and outcomes we don't fully control. It challenges the belief that mindset guarantees results and suggests peace comes from changing our relationship to chance.",
    "image": "space_between_knowing.jpg",
    "link": "https://www.amazon.com/Space-Between-Knowing-Subu-Sangameswar-ebook/dp/B0GHZMSKY5"
  },
  {
    "title": "The Quiet Asterisk",
    "description": "A meditation on probability and everyday resilience. Through human stories, it reframes uncertainty as something to live with—rather than conquer.",
    "image": "the_quiet_asterisk.jpg",
    "link": ""
  }
]
```

**Note**: The second book has an empty `link` field, so no "Buy Book" button will be displayed for it.

## Customization

### Book Card Styling
Book cards use the same design system as essay cards:
- Warm cream background
- Rust/gold accents
- Hover effects with shadows
- Responsive grid layout

### Modify Book Section
To customize the books page, edit the `generate_books()` function in `make_blog_v7.py`:
- Change hero section text
- Modify grid layout
- Add additional metadata fields
- Customize grouping logic

## Tips

1. **Image Placement**: Place book cover images in the same directory as your script, or in an `./images/` subdirectory
2. **Image Format**: Use just the filename in JSON (e.g., `"book.jpg"` not `"./images/book.jpg"`)
3. **Image Size**: Use consistent dimensions for book covers (recommended: 600x900px for best results)
4. **Empty Links**: Use `"link": ""` for books not yet available - no buy button will show
5. **Description Length**: Homepage shows first 150 characters; full description appears on books page
6. **No books.json?**: Script gracefully skips books sections if file doesn't exist

## File Structure
```
your-project/
├── make_blog_v7.py
├── books.json
├── images/
│   ├── book1.jpg
│   ├── book2.jpg
│   └── ...
├── blogger_markdown_posts/
│   └── *.md
└── output/
    ├── index.html
    ├── books.html
    ├── categories.html
    ├── about.html
    └── images/
        └── (copied images)
```
