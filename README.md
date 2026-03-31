# Quiet Asterisk Blog Generator

A modern, feature-rich static blog generator with glassmorphic design, AI chat integration, video library, archives, and sophisticated content management. Converts markdown files into a beautiful, responsive website.

## 🎨 Design Philosophy

The blog features a **modern literary editorial** aesthetic with:
- Warm, earthy color palette (cream, rust, sage, gold)
- Beautiful typography (Crimson Pro serif + Work Sans sans-serif)
- Modern glassmorphism effects and gradient backgrounds
- Animated floating elements and smooth transitions
- Card-based layouts with elegant hover effects
- Responsive design that works on all devices
- Clean, readable content-first approach

## 📁 Project Structure

```
blog-generator/
├── generate_blog.py      # Main entry point
├── config.py             # Configuration and constants
├── models.py             # Data models (Post class)
├── parser.py             # Markdown front matter parser + YouTube embeds
├── similarity.py         # Related posts calculation
├── utils.py              # Utility functions
├── styles.py             # CSS styles
├── templates.py          # HTML header/footer templates
├── cards.py              # Card component generators
├── generators.py         # Page generation functions
├── chat_widget.py        # AI chat widget (optional)
├── books.json            # Book data
├── categories.json       # Category metadata
├── videos.json           # Video library data
├── blogger_markdown_posts/  # Your markdown files
├── downloads/            # Downloadable files (PDFs, etc.)
├── images/               # Book covers, post images
└── output/               # Generated website
    ├── index.html
    ├── books.html
    ├── videos.html
    ├── archives.html
    ├── categories.html
    ├── category-*.html
    ├── about.html
    ├── contact.html
    ├── downloads/
    ├── images/
    └── *.html            # Blog posts
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

![Image](./images/photo.jpg)

[youtube:dQw4w9WgXcQ]

More content...
```

### 3. Configure Data Files

**books.json:**
```json
[
  {
    "title": "Your Book Title",
    "description": "Book description",
    "image": "cover.jpg",
    "link": "https://amazon.com/your-book",
    "video_id": "YouTube_Video_ID"
  }
]
```

**categories.json:**
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

**videos.json:**
```json
[
  {
    "title": "Introduction to My Blog",
    "video_id": "YouTube_Video_ID",
    "article_link": "my-post.html",
    "featured": true
  }
]
```

### 4. Configure Settings

Edit `config.py`:

```python
BLOG_TITLE = "your blog name"
TAG_LINE = "your tagline"
CONTACT_EMAIL = "you@example.com"
YOUTUBE_CHANNEL = "https://www.youtube.com/@yourchannel"

# Optional: AI Chat
ENABLE_AI_CHAT = True
AWS_API_ENDPOINT = "your-lambda-url"
AWS_API_TOKEN = "your-secret-token"
```

### 5. Generate the Blog

```bash
python generate_blog.py
```

Your site will be in `output/` - open `output/index.html` to view!

## 🎯 Features

### Content Management
- **Markdown-based**: Write in markdown, generates HTML
- **Front matter**: YAML-style metadata for each post
- **Categories**: Automatic categorization and dedicated pages
- **Featured posts**: Highlight important essays on homepage
- **Archived posts**: Exclude drafts without deleting
- **Images**: Support for both markdown and HTML image syntax
- **YouTube embeds**: Simple `[youtube:VIDEO_ID]` syntax in posts

### Related Posts
- **Automatic**: TF-IDF similarity algorithm
- **Threshold-based**: Only shows truly related content
- **Top 3**: Most relevant posts displayed on each post

### Books Section
- **JSON-based**: Easy to update book information
- **Images**: Cover images with automatic copying
- **Buy links**: Direct links to purchase (optional)
- **Video integration**: Embed YouTube videos for each book
- **Smart buttons**: Auto-detects downloads vs external links
- **Flexible**: All metadata fields optional

### Videos Library
- **JSON-based**: Centralized video management
- **Featured video**: Display on homepage
- **Video page**: Dedicated page with all videos
- **Article linking**: Connect videos to related essays
- **Responsive embeds**: 16:9 aspect ratio, mobile-friendly

### Archives
- **Timeline view**: Browse all posts by year and month
- **Accordion interface**: Expandable years and months
- **Latest post highlight**: Featured at top of archive
- **Post counts**: Shows number of essays per period
- **Modern design**: Glassmorphic cards, smooth animations
- **Single page**: No separate page loads needed

### Categories
- **Two-level**: Landing page + individual category pages
- **Descriptions**: Rich text from categories.json
- **Load More**: 10 posts per page, progressive loading
- **Post counts**: Automatic counting and display

### Modern Design
- **Glassmorphism**: Frosted glass effects on cards and badges
- **Gradient backgrounds**: Subtle color transitions
- **Gradient text**: Multi-color typography using background-clip
- **Animated blobs**: Floating background elements
- **Hover animations**: Smooth lift effects on cards and buttons
- **Pill badges**: Modern rounded labels with colored borders
- **Responsive**: Mobile-first, works on all screen sizes
- **Accessible**: Semantic HTML, WCAG AA contrast ratios
- **Fast**: Static HTML, minimal JavaScript
- **SEO-friendly**: Clean URLs, proper meta tags

### Downloads
- **Automatic copying**: Files in `downloads/` directory copied to output
- **Preserves structure**: Subdirectories maintained
- **Easy linking**: Reference files directly in markdown posts
- **Multiple formats**: PDFs, ebooks, templates, code samples, etc.

### AI Chat Widget (Optional)
- **AWS Lambda integration**: Call your backend API
- **Configurable**: Toggle on/off in config
- **Modern interface**: Chat bubbles, loading states
- **Error handling**: User-friendly error messages
- **Customizable**: Configure endpoint, token, and styling

## 📚 Module Documentation

### config.py
Contains all configuration constants:
- Site metadata (title, tagline, copyright, contact email)
- Social media (YouTube channel)
- File paths (input/output directories)
- Content settings (posts per page, similarity threshold)
- Feature toggles (AI chat enable/disable)

**Key Constants:**
- `BLOG_TITLE`: Site name
- `INPUT_DIR`: Where markdown files are located
- `OUTPUT_DIR`: Where generated HTML goes
- `POSTS_PER_CATEGORY_PAGE`: Number of posts before "Load More"
- `ENABLE_AI_CHAT`: Toggle AI chat widget

### models.py
Defines the `Post` dataclass representing a blog post.

**Properties:**
- `slug`: URL-friendly filename
- `reading_time`: Calculated from word count (words/155)
- `formatted_date`: Display format (Month Year)

### parser.py
Handles markdown file reading and front matter parsing.

**Main Functions:**
- `read_markdown_files(directory)`: Reads all `.md` files, parses front matter, returns sorted list of Post objects
- `process_youtube_embeds(html)`: Converts `[youtube:ID]` to responsive iframe embeds

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
- `copy_downloads()`: Copies all files from downloads/ to output/downloads/
- `load_books()`: Loads and validates books.json
- `load_categories()`: Loads and validates categories.json
- `load_videos()`: Loads and validates videos.json
- `clean_text(text)`: Normalizes text for similarity comparison
- `slugify(text)`: Converts text to URL-safe slug

### styles.py
Contains the complete CSS stylesheet as a Python string.

**Design System:**
- CSS variables for colors and fonts
- Glassmorphism effects with backdrop-filter
- Responsive grid layouts
- Card components with hover effects
- Hero sections with animated background blobs
- Footer with three-column layout
- Gradient text effects
- Modern pill badges

**Color Palette:**
- Cream (#FAF8F3): Main background
- Rust (#B8503E): Primary accent
- Charcoal (#2B2826): Text and dark elements
- Sage (#8B9B7E): Secondary accent
- Gold (#C9A767): Tertiary accent
- Slate (#5A5450): Muted text

### templates.py
HTML template functions for consistent page structure.

**Functions:**
- `header_html(title, active_page)`: Generates header with navigation
- `footer_html()`: Generates footer with links and contact info

**Features:**
- Sticky header with backdrop blur
- Active state highlighting
- Responsive navigation
- Three-column footer layout
- Social media links (YouTube)

### cards.py
Component generators for displaying content.

**Functions:**
- `format_featured_card(post)`: Large card for hero section
- `format_card(post)`: Standard card for listings
- `format_book_card(book, show_full_description)`: Book card with cover, video, and buy button

**Card Features:**
- Hover effects (lift, shadow, color change)
- Metadata display (date, category, reading time)
- Responsive layout
- Consistent styling across site

### generators.py
Page generation functions - the core of the site builder.

**Functions:**
- `generate_index(posts, related_map)`: Homepage with modern hero, featured video, books, essays
- `generate_post_pages(posts, related_map)`: Individual blog post pages with related posts
- `generate_books()`: Books landing page with video embeds
- `generate_videos()`: Video library page with all videos
- `generate_archives(posts)`: Archive page with year/month accordion
- `generate_categories(posts)`: Category landing page
- `generate_category_page(category, posts, meta)`: Individual category pages with load more
- `generate_about()`: About page with letter-style format
- `generate_contact()`: Contact page with email CTA

**Homepage Structure:**
1. Modern hero with gradient background and floating blobs
2. Featured video (from videos.json)
3. Featured essays (1 large + 3 small cards)
4. Recent essays (6 most recent non-featured)
5. AI chat widget (if enabled)

### chat_widget.py (Optional)
AI chat widget HTML generator for AWS Lambda integration.

**Function:**
- `get_chat_widget_html()`: Returns complete chat widget HTML with JavaScript

**Features:**
- Modern chat interface with message bubbles
- Loading indicators
- Error handling with user-friendly messages
- Configurable via config.py
- Can be toggled on/off

## ⚙️ Configuration Options

### Site Settings (config.py)

```python
# Change site title
BLOG_TITLE = "Your Blog Name"

# Change tagline
TAG_LINE = "Your tagline here"

# Change contact email
CONTACT_EMAIL = "you@example.com"

# Change YouTube channel
YOUTUBE_CHANNEL = "https://www.youtube.com/@yourchannel"

# Change posts per category page
POSTS_PER_CATEGORY_PAGE = 15

# Change books on homepage
BOOKS_ON_HOMEPAGE = 5

# AI Chat settings
ENABLE_AI_CHAT = True
AWS_API_ENDPOINT = "your-api-endpoint"
AWS_API_TOKEN = "your-secret-token"
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

## 🎨 Content Features

### YouTube Videos in Posts

```markdown
Here's a video:

[youtube:dQw4w9WgXcQ]

More content...
```

### Images in Posts

```markdown
# Markdown syntax
![Alt text](./images/photo.jpg)

# HTML syntax
<img src="photo.png" alt="Description">
```

### Downloads in Posts

```markdown
Download my [free ebook](downloads/my-ebook.pdf).

Get the [template](downloads/templates/worksheet.xlsx).
```

## 📊 Data File Formats

### books.json

```json
[
  {
    "title": "Book Title",
    "author": "Author Name",
    "year": "2024",
    "description": "Book description...",
    "image": "cover.jpg",
    "link": "https://amazon.com/book" or "downloads/book.pdf",
    "video_id": "YouTube_Video_ID"
  }
]
```

### categories.json

```json
{
  "Category Name": {
    "description": "Category description for landing page"
  }
}
```

### videos.json

```json
[
  {
    "title": "Video Title",
    "video_id": "YouTube_Video_ID",
    "article_link": "blog/post.html",
    "featured": true
  }
]
```

## 🎬 Archive System

The archive page organizes all posts chronologically:

1. **Latest Post**: Featured at top with full excerpt
2. **Year Accordion**: Click year to expand (2026, 2025, etc.)
3. **Month Accordion**: Click month within year (December, November, etc.)
4. **Post List**: All posts for that month with title, excerpt, and link
5. **Post Counts**: Shows total essays per year/month

All navigation happens on one page with smooth JavaScript accordion.

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
- Use relative paths: `images/photo.jpg` or `./images/photo.jpg`

### Videos Not Displaying
- Check video ID is correct (from YouTube URL)
- Verify `[youtube:ID]` syntax with no spaces
- Error 153: Usually means video has embedding disabled
- Test video URL: `https://www.youtube.com/embed/YOUR_ID`

### Categories Not Working
- Category names must match exactly (case-sensitive)
- Check `categories.json` exists and is valid JSON
- Verify posts have `category:` field in front matter

### AI Chat Not Working
- Check `ENABLE_AI_CHAT = True` in config
- Verify AWS endpoint and token are correct
- Check browser console for JavaScript errors
- Ensure Lambda function is deployed and accessible

## 📝 Best Practices

### Content
- Write clear, descriptive excerpts
- Use meaningful category names
- Keep featured posts count reasonable (3-5)
- Regular frontmatter format

### Images
- Optimize before adding to project (<500KB)
- Use consistent dimensions for book covers
- Include alt text in markdown
- Store in organized directories

### Organization
- One post per markdown file
- Descriptive filenames (lowercase, hyphens)
- Consistent date format (YYYY-MM-DD)
- Logical category structure

### Performance
- Compress large images
- Limit number of books on homepage
- Use excerpts wisely (150-200 chars)
- Test on mobile devices

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
3. Configure custom domain (optional)

### Custom Server
```bash
# Generate site
python generate_blog.py

# Upload output/ contents to web server
scp -r output/* user@server:/var/www/html/
```

## 📦 Dependencies

- **Python 3.8+**: Core language
- **markdown**: Markdown to HTML conversion
- **scikit-learn**: Text similarity calculation (TF-IDF)
  - numpy (auto-installed)
  - scipy (auto-installed)

## 📄 Documentation Files

- **README.md**: This file - complete usage guide
- **DESIGN_GUIDE.md**: Design system specifications
- **MIGRATION_GUIDE.md**: Transition from v7 to v8
- **DOWNLOADS_README.md**: Downloads feature guide
- **CATEGORIES_README.md**: Categories system guide
- **BOOKS_README.md**: Books feature guide

## 🙏 Acknowledgments

- Design inspired by literary journals and editorial websites
- Typography: Google Fonts (Crimson Pro, Work Sans)
- Markdown parsing: python-markdown library
- Similarity: scikit-learn TF-IDF implementation

---

**Author**: Subu Sangameswar  
**Contact**: hello@quietasterisk.com  
**Version**: 8.0 (Refactored + Modern Design)

Built with ❤️ for writers who care about design.
