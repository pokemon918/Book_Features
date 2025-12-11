"""
Book Chapter Summarizer
=======================
Generates summaries with analysis for book chapters.

Usage:
    python summarizer.py <book_folder>

Example:
    python summarizer.py the_murder_links_epub
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

import tiktoken
from openai import OpenAI

import config
import prompts


# =============================================================================
# INITIALIZATION
# =============================================================================

client = OpenAI(api_key=config.OPENAI_API_KEY)
tokenizer = tiktoken.encoding_for_model(config.MODEL_NAME)


def count_tokens(text: str) -> int:
    """Count tokens in text."""
    return len(tokenizer.encode(text))


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


# =============================================================================
# FILE LOADING
# =============================================================================

def load_metadata(book_folder: Path) -> dict:
    """Load book metadata from .metadata file."""
    metadata_files = list(book_folder.glob("*.metadata"))
    if not metadata_files:
        raise FileNotFoundError(f"No metadata file found in {book_folder}")
    
    with open(metadata_files[0], "r", encoding="utf-8") as f:
        return json.load(f)


def load_chapters(book_folder: Path) -> list[tuple[str, str, str]]:
    """
    Load all chapter files from book folder.
    Returns list of (filename, chapter_title, chapter_text) tuples, sorted by filename.
    """
    chapter_files = sorted([
        f for f in book_folder.glob("*.txt")
        if not f.name.startswith(".")
    ])
    
    chapters = []
    for filepath in chapter_files:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        
        # Extract chapter title from first line
        lines = text.strip().split("\n")
        title = lines[0].strip() if lines else filepath.stem
        content = "\n".join(lines[1:]).strip() if len(lines) > 1 else text
        
        chapters.append((filepath.name, title, content))
    
    return chapters


def detect_book_type(metadata: dict) -> str:
    """
    Detect if book is fiction or nonfiction.
    Simple heuristic based on author - can be extended.
    """
    author = metadata.get("authors", [""])[0].lower()
    title = metadata.get("title", "").lower()
    
    # Known fiction authors/patterns
    fiction_indicators = ["christie", "agatha", "novel", "mystery", "murder"]
    # Known nonfiction indicators
    nonfiction_indicators = ["freud", "interpretation", "psychology", "theory", "analysis"]
    
    for indicator in fiction_indicators:
        if indicator in author or indicator in title:
            return "fiction"
    
    for indicator in nonfiction_indicators:
        if indicator in author or indicator in title:
            return "nonfiction"
    
    # Default to fiction
    return "fiction"


# =============================================================================
# LLM INTERACTION
# =============================================================================

def call_llm(prompt: str, expect_json: bool = False) -> str:
    """Call the LLM with a prompt and return the response."""
    response = client.chat.completions.create(
        model=config.MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,  # Lower temperature for more consistent output
        response_format={"type": "json_object"} if expect_json else None
    )
    return response.choices[0].message.content


def chunk_text(text: str, max_tokens: int = config.MAX_CHUNK_TOKENS) -> list[str]:
    """
    Split text into chunks if it exceeds max_tokens.
    Splits on paragraph boundaries for cleaner breaks.
    """
    if count_tokens(text) <= max_tokens:
        return [text]
    
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for para in paragraphs:
        para_tokens = count_tokens(para)
        
        if current_tokens + para_tokens > max_tokens and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [para]
            current_tokens = para_tokens
        else:
            current_chunk.append(para)
            current_tokens += para_tokens
    
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
    
    return chunks


# =============================================================================
# CORE PROCESSING FUNCTIONS
# =============================================================================

def extract_elements(
    chapter_text: str,
    chapter_title: str,
    metadata: dict,
    book_type: str,
    prior_context: str
) -> dict:
    """Extract key elements from a chapter."""
    
    prompt_template = (
        prompts.EXTRACT_FICTION_PROMPT if book_type == "fiction" 
        else prompts.EXTRACT_NONFICTION_PROMPT
    )
    
    # If chapter is very long, extract from chunks and merge
    chunks = chunk_text(chapter_text)
    
    if len(chunks) == 1:
        prompt = prompt_template.format(
            book_title=metadata.get("title", "Unknown"),
            author=metadata.get("authors", ["Unknown"])[0],
            chapter_title=chapter_title,
            prior_context=prior_context or "This is the first chapter.",
            chapter_text=chapter_text
        )
        response = call_llm(prompt, expect_json=True)
        return json.loads(response)
    
    # Multiple chunks - extract from each and merge
    all_extractions = []
    for i, chunk in enumerate(chunks):
        chunk_context = f"{prior_context}\n\n[Processing part {i+1} of {len(chunks)} of this chapter]"
        prompt = prompt_template.format(
            book_title=metadata.get("title", "Unknown"),
            author=metadata.get("authors", ["Unknown"])[0],
            chapter_title=chapter_title,
            prior_context=chunk_context,
            chapter_text=chunk
        )
        response = call_llm(prompt, expect_json=True)
        all_extractions.append(json.loads(response))
    
    # Merge extractions
    return merge_extractions(all_extractions, book_type)


def merge_extractions(extractions: list[dict], book_type: str) -> dict:
    """Merge multiple extraction dicts into one."""
    if book_type == "fiction":
        merged = {
            "characters": [],
            "events": [],
            "plot_developments": [],
            "settings": [],
            "clues_or_foreshadowing": [],
            "relationships": [],
            "tone_mood": ""
        }
        seen_chars = set()
        for ext in extractions:
            for char in ext.get("characters", []):
                if char.get("name") not in seen_chars:
                    merged["characters"].append(char)
                    seen_chars.add(char.get("name"))
            merged["events"].extend(ext.get("events", []))
            merged["plot_developments"].extend(ext.get("plot_developments", []))
            merged["settings"].extend(list(set(ext.get("settings", []))))
            merged["clues_or_foreshadowing"].extend(ext.get("clues_or_foreshadowing", []))
            merged["relationships"].extend(ext.get("relationships", []))
            if ext.get("tone_mood"):
                merged["tone_mood"] = ext.get("tone_mood")
    else:
        merged = {
            "main_arguments": [],
            "key_concepts": [],
            "evidence": [],
            "case_studies": [],
            "historical_references": [],
            "techniques_methods": [],
            "figures_data": [],
            "connections": []
        }
        seen_concepts = set()
        for ext in extractions:
            merged["main_arguments"].extend(ext.get("main_arguments", []))
            for concept in ext.get("key_concepts", []):
                if concept.get("concept") not in seen_concepts:
                    merged["key_concepts"].append(concept)
                    seen_concepts.add(concept.get("concept"))
            merged["evidence"].extend(ext.get("evidence", []))
            merged["case_studies"].extend(ext.get("case_studies", []))
            merged["historical_references"].extend(list(set(ext.get("historical_references", []))))
            merged["techniques_methods"].extend(list(set(ext.get("techniques_methods", []))))
            merged["figures_data"].extend(ext.get("figures_data", []))
            merged["connections"].extend(ext.get("connections", []))
    
    return merged


def generate_summary(
    chapter_text: str,
    chapter_title: str,
    metadata: dict,
    book_type: str,
    extraction: dict,
    story_so_far: str
) -> str:
    """Generate a chapter summary."""
    
    # Calculate target word count (10-15% of original)
    original_words = count_words(chapter_text)
    target_words = int(original_words * config.TARGET_SUMMARY_RATIO)
    target_words = max(200, target_words)  # Minimum 200 words for adequate coverage
    
    prompt_template = (
        prompts.SUMMARY_FICTION_PROMPT if book_type == "fiction"
        else prompts.SUMMARY_NONFICTION_PROMPT
    )
    
    # For very long chapters, summarize in chunks then combine
    chunks = chunk_text(chapter_text)
    
    if len(chunks) == 1:
        prompt = prompt_template.format(
            book_title=metadata.get("title", "Unknown"),
            author=metadata.get("authors", ["Unknown"])[0],
            chapter_title=chapter_title,
            story_so_far=story_so_far or "This is the first chapter.",
            extraction=json.dumps(extraction, indent=2),
            chapter_text=chapter_text,
            target_words=target_words
        )
        return call_llm(prompt)
    
    # Summarize chunks first
    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        chunk_target = target_words // len(chunks)
        prompt = prompt_template.format(
            book_title=metadata.get("title", "Unknown"),
            author=metadata.get("authors", ["Unknown"])[0],
            chapter_title=f"{chapter_title} (Part {i+1}/{len(chunks)})",
            story_so_far=story_so_far if i == 0 else f"{story_so_far}\n\n[Previous part of this chapter: {chunk_summaries[-1][:500]}...]",
            extraction=json.dumps(extraction, indent=2),
            chapter_text=chunk,
            target_words=chunk_target
        )
        chunk_summaries.append(call_llm(prompt))
    
    # Combine chunk summaries
    combine_prompt = f"""Combine these partial summaries into one cohesive chapter summary.

CRITICAL LENGTH REQUIREMENT: You MUST write approximately {target_words} words (10-15% of original). This is a MINIMUM - do not write less.

PARTIAL SUMMARIES:
{chr(10).join(f'Part {i+1}: {s}' for i, s in enumerate(chunk_summaries))}

Write a single, flowing summary in plain text (no markdown) that captures all key points:"""
    
    return call_llm(combine_prompt)


def generate_analysis(
    chapter_summary: str,
    chapter_title: str,
    metadata: dict,
    book_type: str,
    extraction: dict,
    themes_so_far: str
) -> str:
    """Generate analysis section for the chapter."""
    
    prompt_template = (
        prompts.ANALYSIS_FICTION_PROMPT if book_type == "fiction"
        else prompts.ANALYSIS_NONFICTION_PROMPT
    )
    
    prompt = prompt_template.format(
        book_title=metadata.get("title", "Unknown"),
        author=metadata.get("authors", ["Unknown"])[0],
        chapter_title=chapter_title,
        themes_so_far=themes_so_far or "No themes identified yet.",
        chapter_summary=chapter_summary,
        extraction=json.dumps(extraction, indent=2)
    )
    
    return call_llm(prompt)


def update_context(
    current_context: dict,
    chapter_summary: str,
    extraction: dict,
    book_type: str
) -> dict:
    """Update rolling context after processing a chapter."""
    
    prompt_template = (
        prompts.UPDATE_CONTEXT_FICTION_PROMPT if book_type == "fiction"
        else prompts.UPDATE_CONTEXT_NONFICTION_PROMPT
    )
    
    prompt = prompt_template.format(
        current_context=json.dumps(current_context, indent=2) if current_context else "No prior context.",
        chapter_summary=chapter_summary,
        extraction=json.dumps(extraction, indent=2)
    )
    
    response = call_llm(prompt, expect_json=True)
    return json.loads(response)


# =============================================================================
# MAIN PROCESSING PIPELINE
# =============================================================================

def process_book(book_folder: str) -> None:
    """
    Process an entire book and generate summaries for each chapter.
    
    Args:
        book_folder: Name of the book folder (e.g., "the_murder_links_epub")
    """
    book_path = Path(book_folder)
    if not book_path.exists():
        # Try relative to script location
        book_path = Path(__file__).parent / book_folder
    
    if not book_path.exists():
        raise FileNotFoundError(f"Book folder not found: {book_folder}")
    
    print(f"\n{'='*60}")
    print(f"Processing: {book_folder}")
    print(f"{'='*60}\n")
    
    # Load book data
    metadata = load_metadata(book_path)
    chapters = load_chapters(book_path)
    book_type = detect_book_type(metadata)
    
    print(f"Title: {metadata.get('title')}")
    print(f"Author: {metadata.get('authors', ['Unknown'])[0]}")
    print(f"Type: {book_type}")
    print(f"Chapters: {len(chapters)}")
    print()
    
    # Create output directory
    output_dir = book_path / config.OUTPUT_DIR
    output_dir.mkdir(exist_ok=True)
    
    # Initialize rolling context
    context = {}
    
    # Process each chapter
    for i, (filename, title, text) in enumerate(chapters):
        chapter_num = i + 1
        print(f"[{chapter_num}/{len(chapters)}] Processing: {title[:50]}...")
        
        # Skip very short chapters (like index, bibliography)
        if count_words(text) < 100:
            print(f"  -> Skipping (too short: {count_words(text)} words)")
            continue
        
        # Get context strings for prompts
        story_so_far = context.get("story_so_far") or context.get("argument_so_far", "")
        themes_so_far = ", ".join(context.get("themes_identified", []))
        
        # Step 1: Extract key elements
        print("  -> Extracting elements...")
        extraction = extract_elements(
            chapter_text=text,
            chapter_title=title,
            metadata=metadata,
            book_type=book_type,
            prior_context=story_so_far
        )
        
        # Step 2: Generate summary
        print("  -> Generating summary...")
        summary = generate_summary(
            chapter_text=text,
            chapter_title=title,
            metadata=metadata,
            book_type=book_type,
            extraction=extraction,
            story_so_far=story_so_far
        )
        
        # Step 3: Generate analysis
        print("  -> Generating analysis...")
        analysis = generate_analysis(
            chapter_summary=summary,
            chapter_title=title,
            metadata=metadata,
            book_type=book_type,
            extraction=extraction,
            themes_so_far=themes_so_far
        )
        
        # Step 4: Update rolling context
        print("  -> Updating context...")
        context = update_context(
            current_context=context,
            chapter_summary=summary,
            extraction=extraction,
            book_type=book_type
        )
        
        # Save output
        output_filename = f"{filename.replace('.txt', '')}_summary.txt"
        output_path = output_dir / output_filename
        
        original_words = count_words(text)
        summary_words = count_words(summary)
        ratio = (summary_words / original_words * 100) if original_words > 0 else 0
        
        output_content = f"""{title}

SUMMARY

{summary}

ANALYSIS

{analysis}
"""
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output_content)
        
        print(f"  -> Saved: {output_filename} ({ratio:.1f}% of original)")
        print()
    
    # Save final context
    context_path = output_dir / "book_context.json"
    with open(context_path, "w", encoding="utf-8") as f:
        json.dump(context, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Complete! Summaries saved to: {output_dir}")
    print(f"{'='*60}\n")


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nAvailable books:")
        for folder in Path(__file__).parent.glob("*_epub"):
            print(f"  - {folder.name}")
        sys.exit(1)
    
    book_folder = sys.argv[1]
    process_book(book_folder)

