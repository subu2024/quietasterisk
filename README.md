# Quiet Asterisk Blog Generator

A modern, static blog generator with a refined editorial design system. Converts markdown files into a beautiful, responsive website with books, categories, and sophisticated typography.

## 🎨 Design Philosophy

The blog features a **literary editorial** aesthetic with:
- Warm, earthy color palette (cream, rust, sage, gold)
- Beautiful typography (Crimson Pro serif + Work Sans sans-serif)
- Card-based layouts with elegant hover effects
- Responsive design that works on all devices
- Clean, readable content-first approach

## 📁 Project Structure

```
blog-generator/
├── generate_blog.py      # Main entry point
├── config.py             # Configuration and constants
├── models.py             # Data models (Post class)
├── parser.py             # Markdown front matter parser
├── similarity.py         # Related posts calculation
├── utils.py              # Utility functions
├── styles.py             # CSS styles
├── templates.py          # HTML header/footer templates
├── cards.py              # Card component generators
├── generators.py         # Page generation functions
├── books.json            # Book data
├── categories.json       # Category metadata
├── blogger_markdown_posts/  # Your markdown files
└── output/               # Generated website (created)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install markdown scikit-learn
```

### 2. Prepare Your Content

Create markdown files in `blogger_markdown_posts/`:

```markdown
---
title: "Your Post Title"
date: 2025-01-15
category: Essays
featured: true
excerpt: "A brief description of your post"
---

Your markdown content here...
```

### 3. Configure Books and Categories

Create `books.json`:
```json
[
  {
    "title": "Your Book Title",
    "description": "Book description",
    "image": "cover.jpg",
    "link": "https://amazon.com/your-book"
  }
]
```

Create `categories.json`:
```json
{
  "Essays": {
    "description": "Deep explorations of meaning and systems"
  },
  "Stories": {
    "description": "Narratives that illuminate"
  }
}
```

### 4. Generate the Blog

```bash
python generate_blog.py
```

Your site will be in `output/` - open `output/index.html` to view!

## 📚 Module Documentation

### config.py
Contains all configuration constants:
- Site metadata (title, tagline, copyright, contact email)
- File paths (input/output directories)
- Content settings (posts per page, similarity threshold)

**Key Constants:**
- `BLOG_TITLE`: Site name
- `INPUT_DIR`: Where markdown files are located
- `OUTPUT_DIR`: Where generated HTML goes
- `POSTS_PER_CATEGORY_PAGE`: Number of posts before "Load More"

### models.py
Defines the `Post` dataclass representing a blog post.

**Properties:**
- `slug`: URL-friendly filename
- `reading_time`: Calculated from word count
- `formatted_date`: Display format (Month Year)

### parser.py
Handles markdown file reading and front matter parsing.

**Main Function:**
- `read_markdown_files(directory)`: Reads all `.md` files, parses front matter, returns sorted list of Post objects

**Front Matter Fields:**
- `title`: Post title (required)
- `date`: YYYY-MM-DD format
- `category`: Category name
- `featured`: Boolean for homepage featuring
- `archived`: Boolean to exclude from site
- `excerpt`: Short description

### similarity.py
Calculates content similarity for "Related Posts" feature.

**Functions:**
- `compute_similarity(posts)`: Uses TF-IDF and cosine similarity
- `build_related_map(posts, sim_matrix)`: Returns mapping of posts to top 3 related posts

**Algorithm:**
1. Clean and vectorize post content
2. Calculate similarity scores
3. Filter by threshold (0.15 default)
4. Return top 3 matches per post

### utils.py
Utility functions for common operations.

**Key Functions:**
- `copy_image(src_path)`: Copies images to output directory
- `load_books()`: Loads and validates books.json
- `load_categories()`: Loads and validates categories.json
- `clean_text(text)`: Normalizes text for similarity comparison
- `slugify(text)`: Converts text to URL-safe slug

### styles.py
Contains the complete CSS stylesheet as a Python string.

**Design System:**
- CSS variables for colors and fonts
- Responsive grid layouts
- Card components with hover effects
- Hero sections with background blobs
- Footer with three-column layout

**Color Palette:**
- Cream (#FAF8F3): Main background
- Rust (#B8503E): Primary accent
- Charcoal (#2B2826): Text and dark elements
- Sage (#8B9B7E): Secondary accent
- Gold (#C9A767): Tertiary accent

### templates.py
HTML template functions for consistent page structure.

**Functions:**
- `header_html(title, active_page)`: Generates header with navigation
- `footer_html()`: Generates footer with links and contact info

**Features:**
- Sticky header with active state highlighting
- Responsive navigation
- Three-column footer layout
- Email contact in footer

### cards.py
Component generators for displaying content.

**Functions:**
- `format_featured_card(post)`: Large card for hero section
- `format_card(post)`: Standard card for listings
- `format_book_card(book, show_full_description)`: Book card with cover and buy button

**Card Features:**
- Hover effects (lift, shadow, color change)
- Metadata display (date, category, reading time)
- Responsive layout
- Consistent styling

### generators.py
Page generation functions - the core of the site builder.

**Functions:**
- `generate_index(posts, related_map)`: Homepage with hero, books, featured/recent posts
- `generate_post_pages(posts, related_map)`: Individual blog post pages
- `generate_books()`: Books landing page
- `generate_categories(posts)`: Category landing page
- `generate_category_page(category, posts, meta)`: Individual category pages with load more
- `generate_about()`: About page
- `generate_contact()`: Contact page

**Homepage Structure:**
1. Hero section with site description and stats
2. Books section (first 3 books if available)
3. Featured essays (1 large + 3 small cards)
4. Recent essays (6 most recent non-featured)

**Category Pages:**
- Landing page: Grid of category cards with descriptions
- Individual pages: All posts in category, 10 visible initially, "Load More" for rest

## 🎯 Features

### Content Management
- **Markdown-based**: Write in markdown, generates HTML
- **Front matter**: YAML-style metadata for each post
- **Categories**: Automatic categorization and dedicated pages
- **Featured posts**: Highlight important essays on homepage
- **Archived posts**: Exclude drafts without deleting

### Related Posts
- **Automatic**: TF-IDF similarity algorithm
- **Threshold-based**: Only shows truly related content
- **Top 3**: Most relevant posts displayed

### Books Section
- **JSON-based**: Easy to update book information
- **Images**: Cover images with automatic copying
- **Buy links**: Direct links to purchase (optional)
- **Flexible**: All metadata fields optional

### Categories
- **Two-level**: Landing page + individual category pages
- **Descriptions**: Rich text from categories.json
- **Load More**: 10 posts per page, progressive loading
- **Post counts**: Automatic counting and display

### Design
- **Responsive**: Mobile-first, works on all screen sizes
- **Accessible**: Semantic HTML, good contrast ratios
- **Fast**: Static HTML, no JavaScript dependencies (except load more)
- **SEO-friendly**: Clean URLs, proper meta tags

## ⚙️ Configuration Options

### Site Settings (config.py)

```python
# Change site title
BLOG_TITLE = "Your Blog Name"

# Change tagline
TAG_LINE = "Your tagline here"

# Change contact email
CONTACT_EMAIL = "you@example.com"

# Change posts per category page
POSTS_PER_CATEGORY_PAGE = 15

# Change books on homepage
BOOKS_ON_HOMEPAGE = 5
```

### Front Matter Options

```markdown
---
title: "Post Title"          # Required
date: 2025-01-15             # YYYY-MM-DD format
category: Essays             # Must match categories.json key
featured: true               # Boolean, show on homepage
archived: false              # Boolean, exclude from site
excerpt: "Brief description" # Shown in cards
---
```

## 🔧 Customization

### Adding New Colors

Edit `styles.py`:
```css
:root {
  --color-your-name: #HEX;
}
```

### Changing Typography

Edit `styles.py` import and root variables:
```css
@import url('https://fonts.googleapis.com/css2?family=YourFont...');

:root {
  --font-serif: 'YourSerifFont', serif;
  --font-sans: 'YourSansFont', sans-serif;
}
```

### Adding New Pages

1. Create generator function in `generators.py`
2. Add route in `templates.py` header/footer
3. Call generator in `generate_blog.py` main function

## 🐛 Troubleshooting

### No Posts Generated
- Check markdown files are in `INPUT_DIR` (default: `./blogger_markdown_posts`)
- Verify front matter is properly formatted with `---` delimiters
- Check for `archived: true` in front matter

### Images Not Showing
- Verify image paths in markdown
- Check images exist at specified paths
- Images are copied to `output/images/`

### Categories Not Working
- Category names must match exactly (case-sensitive)
- Check `categories.json` exists and is valid JSON
- Verify posts have `category:` field in front matter

### Load More Not Working
- Check JavaScript is enabled in browser
- Verify category has more than 10 posts
- Check browser console for errors

## 📊 Performance

- **Generation time**: ~1-2 seconds for 100 posts
- **Page load**: Static HTML, instant loading
- **File size**: Typical homepage ~50KB (including CSS)
- **Images**: Copied as-is, optimize before adding

## 🔒 Security

- **No database**: Static files, no injection risks
- **No user input**: Generated from trusted markdown
- **External links**: Use `rel="noopener noreferrer"`
- **Email**: Obfuscated with mailto links

## 📝 Best Practices

### Content
- Write clear, descriptive excerpts
- Use meaningful category names
- Keep featured posts count reasonable (3-5)
- Regular frontmatter format

### Images
- Optimize before adding to project
- Use consistent dimensions for book covers
- Include alt text in markdown
- Keep file sizes reasonable (<500KB)

### Organization
- One post per markdown file
- Descriptive filenames
- Consistent date format
- Logical category structure

## 🚀 Deployment

### GitHub Pages
```bash
# Generate site
python generate_blog.py

# Deploy to gh-pages branch
cd output
git init
git add .
git commit -m "Deploy blog"
git remote add origin your-repo-url
git push -f origin main:gh-pages
```

### Netlify
1. Generate site: `python generate_blog.py`
2. Deploy `output/` folder via Netlify web interface or CLI

### Custom Server
```bash
# Generate site
python generate_blog.py

# Upload output/ contents to web server
scp -r output/* user@server:/var/www/html/
```

## 🔄 Development Workflow

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Add/edit markdown posts
vim blogger_markdown_posts/new-post.md

# 3. Generate site
python generate_blog.py

# 4. Preview locally
open output/index.html

# 5. Deploy when ready
# (see Deployment section)
```

## 📦 Dependencies

- **Python 3.8+**: Core language
- **markdown**: Markdown to HTML conversion
- **scikit-learn**: Text similarity calculation
  - numpy (auto-installed)
  - scipy (auto-installed)

## 🤝 Contributing

This is a personal project, but suggestions welcome! Areas for improvement:
- Additional page templates
- More design themes
- Performance optimizations
- Additional markdown extensions

## 📄 License

See LICENSE file for details.

## 🙏 Acknowledgments

- Design inspired by literary journals and editorial websites
- Typography: Google Fonts (Crimson Pro, Work Sans)
- Markdown parsing: python-markdown library
- Similarity: scikit-learn TF-IDF implementation

---

**Author**: Subu Sangameswar  
**Contact**: hello@quietasterisk.com  
**Blog**: https://quietasterisk.com
