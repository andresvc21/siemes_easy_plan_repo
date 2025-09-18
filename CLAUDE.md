# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Teamcenter Easy Plan AI Agent - a terminal-based RAG (Retrieval-Augmented Generation) system that provides contextual answers about Siemens Teamcenter Easy Plan configuration. The system combines local documentation (~50 documents) with curated web content from forums and documentation sites.

## Development Commands

**Note: This project is currently in the design phase. The following commands will be available once implementation begins:**

```bash
# Environment Setup
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your_key"
export LANGFUSE_PUBLIC_KEY="your_key"
export LANGFUSE_SECRET_KEY="your_key"

# Initial Setup and Indexing
python main.py --index-documents                    # Process documents into vector store
python main.py --scrape-urls web_sources/urls.txt  # Scrape and index web content
python main.py --reindex                           # Rebuild entire index

# Running the Agent
python main.py                              # Start interactive session
python main.py --session <session_id>       # Load specific session
python main.py --history                    # Show conversation history

# Web Content Management
python main.py --scrape-urls web_sources/urls.txt           # Scrape specific URLs
python main.py --crawl-site https://community.siemens.com   # Crawl entire site
python main.py --update-web-content                         # Refresh existing content
python main.py --search-forums "user role configuration"   # Search for new forum content

# Testing and Evaluation
python main.py --evaluate --test-set tests/test_questions.txt     # Run evaluation on test questions
python main.py --compare-models --models sonnet4,gpt4,gemini      # Compare different LLMs
python main.py --experiment --config experiments/prompt_variants.yaml # Run experiments

# Maintenance
python main.py --cleanup-old-content --days 30  # Remove old web content
python main.py --stats                          # Show system statistics
python main.py --dashboard                      # View Langfuse dashboard
```

## Architecture Overview

The system follows a modular RAG architecture:

```
Terminal CLI → Conversation Manager → RAG Pipeline → Vector Store (FAISS)
                     ↓                      ↓
               Langfuse Tracking    Document Processor ← Web Scraper
                     ↓                      ↓
               Claude Sonnet 4 API   Combined Index (Documents + Web Content)
```

### Core Components

**RAG Pipeline (`src/rag_pipeline.py`)**: Orchestrates retrieval and generation
- Processes user queries with conversation context
- Retrieves relevant chunks from both document and web content indices
- Generates responses using Claude Sonnet 4 with structured prompts

**Vector Store (`src/vector_store.py`)**: FAISS-based semantic search
- Uses `all-MiniLM-L6-v2` embeddings (384 dimensions)
- Maintains dual indices: documents vs web content
- IndexFlatL2 for exact search with current dataset size

**Document Processor (`src/document_processor.py`)**: Handles multiple formats
- Supports PDF, DOCX, MD files
- Chunk size: 500-1000 characters with 100-character overlap
- Preserves document structure and metadata

**Web Scraper (`src/web_scraper.py`)**: Extracts web content
- Targets Siemens Community Forums, documentation sites
- Implements content quality filtering and relevance scoring
- Respects robots.txt and implements rate limiting

**Conversation Manager (`src/conversation.py`)**: Maintains context
- Sliding window of last 10 Q&A pairs
- Session-based conversation grouping
- Source tracking for citations

**Langfuse Client (`src/langfuse_client.py`)**: Experiment tracking
- Logs all interactions for evaluation
- Supports A/B testing across models and prompts
- Tracks performance metrics and costs

## Key Configuration

**Primary LLM**: Claude Sonnet 4 (`claude-sonnet-4-20250514`)
**Fallback Models**: GPT-4, Gemini Pro
**Embedding Model**: `all-MiniLM-L6-v2`
**Vector Database**: FAISS with IndexFlatL2
**Context Window**: Up to 4000 characters from retrieved documents
**Memory Limit**: 10 conversation turns per session

## Data Structure

### File Organization
```
teamcenter_agent/
├── src/                    # Core application modules
├── documents/              # Input documents (~50 files)
├── web_sources/           # Web content configuration
├── data/
│   ├── vectors/           # FAISS indices
│   ├── web_content/       # Scraped content storage
│   ├── conversations.json # Chat history
│   └── processed_docs.json # Document chunks & metadata
├── experiments/           # Langfuse experiment configs
└── tests/                # Test questions and sample documents
```

### Important Data Models

**DocumentChunk**: Core content unit with source attribution
- Includes content, source, page, section, chunk_type, source_type
- Maintains metadata for documents vs web content

**ConversationMessage**: Chat interaction with full traceability
- Role, content, timestamp, sources, session_id, trace_id

**SearchResult**: Retrieved content with scoring
- Chunk reference, similarity score, rank, source type

## Development Guidelines

**Code Style**: Follow the established patterns when implementing:
- Use dataclasses for data models
- Implement proper error handling with logging
- Add type hints throughout
- Follow the modular architecture shown in design docs

**Testing Approach**:
- Use the 15 test questions in `tests/test_questions.txt`
- Implement evaluation via Langfuse integration
- Test both document-only and web-enhanced retrieval

**Web Scraping Ethics**:
- Always respect robots.txt
- Implement delays between requests (1s minimum)
- Use clear User-Agent identification
- Focus on educational/internal use

**Security Considerations**:
- Store API keys in environment variables only
- Process all documents locally before sending to LLM APIs
- Validate file paths to prevent directory traversal
- Implement content filtering for scraped data

## Performance Expectations

**Dataset Size**: 50 documents + 150-200 web pages (~1500-2000 chunks)
**Query Response Time**: 5-15 seconds total (acceptable for use case)
**Memory Usage**: <500MB during operation
**Storage Requirements**: <500MB total project size
**Index Build Time**: ~2 minutes for combined document and web content

## Experimental Framework

The system supports systematic evaluation via Langfuse:
- **Model Comparison**: Test Claude Sonnet 4 vs GPT-4 vs Gemini
- **Prompt Variants**: Different instruction styles and expert personas
- **Retrieval Tuning**: TOP_K variations, web content weighting
- **Evaluation Metrics**: Relevance, accuracy, completeness, source attribution

Use experiment configurations in `experiments/` directory to run systematic comparisons and track performance improvements.