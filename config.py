"""Configuration for the book summarization system."""

import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4o"  # or "gpt-4o-mini" for faster/cheaper processing

# Summary Configuration
TARGET_SUMMARY_RATIO = 0.13  # 13% of original (closer to middle-upper range of 10-15%)
MIN_SUMMARY_RATIO = 0.10
MAX_SUMMARY_RATIO = 0.15

# Chunking Configuration (for long chapters)
MAX_CHUNK_TOKENS = 6000  # Process in chunks if chapter exceeds this
CHUNK_OVERLAP_TOKENS = 200

# Output Configuration
OUTPUT_DIR = "summaries"

