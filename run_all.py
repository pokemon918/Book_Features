"""
Process All Books
=================
Runs the summarizer on all book folders in the project.

Usage:
    python run_all.py
"""

from pathlib import Path
from summarizer import process_book


def main():
    """Process all books in the project."""
    project_dir = Path(__file__).parent
    
    # Find all book folders (ending with _epub)
    book_folders = sorted(project_dir.glob("*_epub"))
    
    if not book_folders:
        print("No book folders found!")
        return
    
    print(f"Found {len(book_folders)} books to process:\n")
    for folder in book_folders:
        print(f"  - {folder.name}")
    print()
    
    # Process each book
    for folder in book_folders:
        try:
            process_book(str(folder))
        except Exception as e:
            print(f"Error processing {folder.name}: {e}")
            continue
    
    print("\n" + "="*60)
    print("All books processed!")
    print("="*60)


if __name__ == "__main__":
    main()

