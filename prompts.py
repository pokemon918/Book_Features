"""Prompt templates for book summarization."""

# =============================================================================
# EXTRACTION PROMPTS - Extract key elements from chapter text
# =============================================================================

EXTRACT_FICTION_PROMPT = """You are analyzing a chapter from a fiction book. Extract key elements.

BOOK: {book_title} by {author}
CHAPTER: {chapter_title}
PRIOR CONTEXT: {prior_context}

CHAPTER TEXT:
{chapter_text}

Extract the following in JSON format:
{{
    "characters": [
        {{"name": "...", "description": "brief description if new", "actions": "key actions in this chapter"}}
    ],
    "events": [
        {{"event": "what happened", "significance": "why it matters"}}
    ],
    "plot_developments": ["key plot points that advance the story"],
    "settings": ["locations/places introduced or featured"],
    "clues_or_foreshadowing": ["anything that might be important later"],
    "relationships": ["character relationship developments"],
    "tone_mood": "overall tone of this chapter"
}}

IMPORTANT: Base your extraction ONLY on the provided text. Do not use any external knowledge about this book."""

EXTRACT_NONFICTION_PROMPT = """You are analyzing a chapter from a nonfiction book. Extract key elements.

BOOK: {book_title} by {author}
CHAPTER: {chapter_title}
PRIOR CONTEXT: {prior_context}

CHAPTER TEXT:
{chapter_text}

Extract the following in JSON format:
{{
    "main_arguments": ["central arguments or claims made"],
    "key_concepts": [
        {{"concept": "term/idea", "definition": "explanation"}}
    ],
    "evidence": [
        {{"claim": "what is claimed", "evidence": "supporting evidence/examples"}}
    ],
    "case_studies": ["any case studies, examples, or narratives used"],
    "historical_references": ["historical events, figures mentioned"],
    "techniques_methods": ["any techniques, methods, or tools described"],
    "figures_data": ["any important figures, statistics, or data"],
    "connections": ["connections to previous chapters or broader arguments"]
}}

IMPORTANT: Base your extraction ONLY on the provided text. Do not use any external knowledge about this book."""

# =============================================================================
# SUMMARY PROMPTS - Generate the actual summary
# =============================================================================

SUMMARY_FICTION_PROMPT = """You are creating a chapter summary for a fiction book.

BOOK: {book_title} by {author}
CHAPTER: {chapter_title}

STORY SO FAR (from previous chapters):
{story_so_far}

KEY ELEMENTS EXTRACTED FROM THIS CHAPTER:
{extraction}

FULL CHAPTER TEXT:
{chapter_text}

CRITICAL LENGTH REQUIREMENT: You MUST write approximately {target_words} words (10-15% of original chapter length). This is a MINIMUM requirement - do not write less. If your summary is shorter than {target_words} words, expand it with more detail from the chapter.

Write a summary that:
1. Captures ALL key events, character actions, and plot developments in detail
2. Preserves important dialogue or character moments with sufficient context
3. Maintains the narrative flow - a reader should be able to continue reading the original book after this summary without confusion
4. Includes any plot twists, revelations, or clues with proper setup
5. Notes character introductions and relationship developments thoroughly
6. Provides enough detail that someone could follow the story without reading the original

Write in clear, engaging prose that matches the book's tone. Do NOT reveal information from later chapters. Write ONLY based on the provided text. Output ONLY plain text - no markdown formatting, headers, or bullet points.

SUMMARY:"""

SUMMARY_NONFICTION_PROMPT = """You are creating a chapter summary for a nonfiction book.

BOOK: {book_title} by {author}
CHAPTER: {chapter_title}

CONTEXT FROM PREVIOUS CHAPTERS:
{story_so_far}

KEY ELEMENTS EXTRACTED FROM THIS CHAPTER:
{extraction}

FULL CHAPTER TEXT:
{chapter_text}

CRITICAL LENGTH REQUIREMENT: You MUST write approximately {target_words} words (10-15% of original chapter length). This is a MINIMUM requirement - do not write less. If your summary is shorter than {target_words} words, expand it with more detail from the chapter.

Write a summary that:
1. Captures ALL main arguments and key concepts with sufficient explanation
2. Preserves important evidence, examples, and case studies in detail
3. Includes any techniques, methods, or tools described thoroughly
4. Notes historical references and figures mentioned with context
5. Maintains logical flow of the author's reasoning
6. A reader should be able to continue reading the original book after this summary without confusion
7. Provides enough detail that someone could understand the key points without reading the original

Write in clear, informative prose. Do NOT use external knowledge about this topic - base everything on the provided text. Output ONLY plain text - no markdown formatting, headers, or bullet points.

SUMMARY:"""

# =============================================================================
# ANALYSIS PROMPTS - Generate thematic analysis
# =============================================================================

ANALYSIS_FICTION_PROMPT = """You are writing an analysis section for a fiction chapter summary.

BOOK: {book_title} by {author}
CHAPTER: {chapter_title}

THEMES IDENTIFIED SO FAR IN THE BOOK:
{themes_so_far}

CHAPTER SUMMARY:
{chapter_summary}

KEY ELEMENTS FROM THIS CHAPTER:
{extraction}

Write a brief analysis section covering:

1. **Thematic Analysis**: What themes are explored in this chapter? How do characters' actions and events reflect or develop these themes?

2. **Character Dynamics**: What nuances in character relationships are revealed? How do power dynamics, conflicts, or bonds develop?

Keep the analysis concise but insightful. Base it ONLY on the provided text.

ANALYSIS:"""

ANALYSIS_NONFICTION_PROMPT = """You are writing an analysis section for a nonfiction chapter summary.

BOOK: {book_title} by {author}
CHAPTER: {chapter_title}

THEMES/ARGUMENTS DEVELOPED SO FAR:
{themes_so_far}

CHAPTER SUMMARY:
{chapter_summary}

KEY ELEMENTS FROM THIS CHAPTER:
{extraction}

Write a brief analysis section covering:

1. **Thematic Analysis**: What overarching themes or arguments does this chapter develop? How does it contribute to the book's central thesis?

2. **Narrative Approach**: How does the author present their ideas? What rhetorical techniques, case studies, or narrative elements are used to make the argument?

Keep the analysis concise but insightful. Base it ONLY on the provided text.

ANALYSIS:"""

# =============================================================================
# CONTEXT UPDATE PROMPTS - Update rolling context after each chapter
# =============================================================================

UPDATE_CONTEXT_FICTION_PROMPT = """Based on the chapter summary and extraction below, update the rolling context.

CURRENT CONTEXT:
{current_context}

NEW CHAPTER SUMMARY:
{chapter_summary}

NEW EXTRACTION:
{extraction}

Provide an updated context in JSON format:
{{
    "story_so_far": "2-3 sentence summary of the story up to this point",
    "active_characters": ["list of characters currently active in the story"],
    "unresolved_threads": ["ongoing plot threads or mysteries"],
    "themes_identified": ["themes that have emerged"],
    "key_facts": ["important facts the reader must remember"]
}}"""

UPDATE_CONTEXT_NONFICTION_PROMPT = """Based on the chapter summary and extraction below, update the rolling context.

CURRENT CONTEXT:
{current_context}

NEW CHAPTER SUMMARY:
{chapter_summary}

NEW EXTRACTION:
{extraction}

Provide an updated context in JSON format:
{{
    "argument_so_far": "2-3 sentence summary of the author's argument up to this point",
    "key_concepts_defined": ["concepts that have been defined"],
    "evidence_presented": ["major evidence or case studies presented"],
    "themes_identified": ["themes or threads being developed"],
    "key_facts": ["important facts or findings to remember"]
}}"""

