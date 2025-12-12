# Book Chapter Summarizer

An AI-powered tool that generates comprehensive chapter summaries and thematic analyses for books. Supports both fiction and nonfiction works with intelligent content extraction and rolling context awareness.

## Features

- **Intelligent Summarization**: Generates summaries that are 10-15% of original chapter length
- **Thematic Analysis**: Provides character dynamics, theme exploration, and narrative analysis
- **Rolling Context**: Maintains story/argument continuity across chapters
- **Fiction & Nonfiction Support**: Automatically detects book type and adapts prompts accordingly
- **Long Chapter Handling**: Automatically chunks and processes lengthy chapters
- **EPUB Support**: Works with extracted EPUB book folders

## Installation

1. Clone the repository:
```bash
git clone https://github.com/pokemon918/Book_Features.git
cd Book_Features
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure API key:
```bash
cp env_example.txt .env
# Edit .env and add your OpenAI API key
```

## Configuration

Edit `config.py` to customize:

| Setting | Default | Description |
|---------|---------|-------------|
| `MODEL_NAME` | `gpt-4o` | OpenAI model (use `gpt-4o-mini` for faster/cheaper) |
| `TARGET_SUMMARY_RATIO` | `0.13` | Target summary length (13% of original) |
| `MAX_CHUNK_TOKENS` | `6000` | Token limit before chunking long chapters |
| `OUTPUT_DIR` | `summaries` | Output folder name within each book |

## Usage

### Process a Single Book

```bash
python summarizer.py <book_folder>
```

Example:
```bash
python summarizer.py the_murder_links_epub
```

### Process All Books

```bash
python run_all.py
```

## Book Folder Structure

Each book should be in a folder with the following structure:

```
book_name_epub/
├── book.metadata          # JSON with title, authors, etc.
├── 01_Chapter_Title.txt   # Chapter files (sorted alphabetically)
├── 02_Chapter_Title.txt
├── ...
└── summaries/             # Generated output (created automatically)
    ├── 01_Chapter_Title_summary.txt
    ├── 02_Chapter_Title_summary.txt
    └── book_context.json
```

### Metadata Format

The `.metadata` file should contain:
```json
{
  "title": "Book Title",
  "authors": ["Author Name"]
}
```

## Output Format

Each summary file contains:

```
Chapter Title

SUMMARY

[Detailed chapter summary - 10-15% of original length]

ANALYSIS

[Thematic analysis and character dynamics]
```

## How It Works

1. **Load Book**: Reads metadata and chapter files from the book folder
2. **Detect Type**: Identifies fiction vs nonfiction based on author/title
3. **For Each Chapter**:
   - **Extract Elements**: Characters, events, themes (fiction) or arguments, concepts, evidence (nonfiction)
   - **Generate Summary**: Creates detailed summary maintaining narrative flow
   - **Generate Analysis**: Analyzes themes and character/narrative dynamics
   - **Update Context**: Maintains rolling context for continuity
4. **Save Output**: Writes summaries and final book context

## Project Structure

```
Book_Features/
├── summarizer.py      # Main processing logic
├── prompts.py         # LLM prompt templates
├── config.py          # Configuration settings
├── run_all.py         # Batch processing script
├── requirements.txt   # Python dependencies
├── env_example.txt    # API key template
└── *_epub/            # Book folders
```

## Requirements

- Python 3.10+
- OpenAI API key
- Dependencies: `openai`, `tiktoken`, `python-dotenv`

## License

MIT License

