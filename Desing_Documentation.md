# Teamcenter Easy Plan AI Agent - Design Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Directory Structure](#directory-structure)
4. [Core Components](#core-components)
5. [Data Models](#data-models)
6. [Configuration](#configuration)
7. [CLI Interface](#cli-interface)
8. [Web Content Integration](#web-content-integration)
9. [Performance Characteristics](#performance-characteristics)
10. [Langfuse Integration & Experimentation](#langfuse-integration--experimentation)
11. [Error Handling](#error-handling)
12. [Security Considerations](#security-considerations)

## System Overview

A terminal-based AI agent that provides contextual answers about Siemens Teamcenter Easy Plan configuration using Retrieval-Augmented Generation (RAG) with conversation memory. The system combines local documentation (~50 documents) with curated web content from forums and documentation sites to provide comprehensive technical support.

**Key Features:**
- Semantic search across documents and web content
- Conversation memory with context preservation
- Multiple LLM support with primary focus on Claude Sonnet 4
- Experiment tracking and model comparison via Langfuse
- Web content scraping and integration
- Terminal-based interface for rapid prototyping

## Architecture

```
┌─────────────────┐
│  Terminal CLI   │
└─────────┬───────┘
          │
┌─────────▼───────┐
│ Conversation    │
│ Manager         │ 
└─────────┬───────┘
          │
┌─────────▼───────┐
│ RAG Pipeline    │
│ (LangChain)     │
└─────────┬───────┘
          │
┌─────────▼───────┐    ┌─────────────┐    ┌─────────────┐
│ FAISS Vector    │◄───┤ Document    │◄───┤ Web Content │
│ Database        │    │ Processor   │    │ Scraper     │
└─────────┬───────┘    └─────────────┘    └─────────────┘
          │
┌─────────▼───────┐    ┌─────────────┐
│ Claude Sonnet 4 │    │ Langfuse    │
│ API             │◄───┤ Monitoring  │
└─────────────────┘    └─────────────┘
```

## Directory Structure

```
teamcenter_agent/
├── README.md
├── requirements.txt
├── design_documentation.md    # This document
├── config.py                  # Configuration settings
├── main.py                    # CLI interface
├── src/
│   ├── __init__.py
│   ├── document_processor.py  # Document ingestion & chunking
│   ├── vector_store.py        # FAISS operations
│   ├── conversation.py        # Memory management
│   ├── rag_pipeline.py        # RAG orchestration
│   ├── llm_client.py          # API client wrapper
│   ├── langfuse_client.py     # Evaluation & monitoring
│   ├── web_scraper.py         # Web content extraction
│   ├── content_classifier.py  # Filter relevant content
│   └── url_manager.py         # Manage web sources
├── documents/                 # Input documents (~50 files)
│   ├── teamcenter_config.pdf
│   ├── user_management.docx
│   ├── workflow_setup.md
│   └── ...
├── web_sources/               # Web content configurations
│   ├── urls.txt              # Specific URLs to scrape
│   ├── forums_config.yaml    # Forum-specific settings
│   ├── sitemap_urls.txt      # Sites to crawl fully
│   └── content_sources.md    # Documentation of sources
├── data/
│   ├── vectors/              # FAISS indices
│   │   ├── documents.faiss
│   │   ├── documents.pkl     # Document metadata
│   │   ├── web_content.faiss
│   │   └── web_content.pkl   # Web content metadata
│   ├── web_content/          # Scraped content storage
│   │   ├── forums/
│   │   ├── documentation/
│   │   └── tutorials/
│   ├── conversations.json    # Chat history
│   ├── processed_docs.json   # Document chunks & metadata
│   └── content_metadata.json # Track web sources
├── experiments/              # Langfuse experiment configs
│   ├── prompt_variants.yaml
│   ├── model_comparisons.yaml
│   └── evaluation_sets.json
└── tests/
    ├── test_questions.txt    # Your 15 test questions
    └── test_documents/       # Sample docs for testing
```

## Core Components

### 1. Document Processor (`document_processor.py`)

**Purpose:** Convert various document formats and web content into searchable chunks

**Key Functions:**
- `load_documents()` - Load PDF, DOCX, MD files
- `load_web_content()` - Process scraped web content
- `chunk_documents()` - Split into semantic chunks
- `extract_metadata()` - Extract titles, sections, page numbers, URLs

**Chunking Strategy:**
- **Size:** 500-1000 characters per chunk
- **Overlap:** 100 characters between chunks
- **Preserve:** Section headers, step numbers, procedure context
- **Metadata:** Document source, section, page, chunk_type, source_type

```python
class DocumentProcessor:
    def chunk_documents(self, documents: List[Document]) -> List[DocumentChunk]:
        # Preserve procedural structure
        # Maintain step-by-step context
        # Add semantic metadata
        
    def process_web_content(self, web_sources: Dict) -> List[DocumentChunk]:
        # Handle forum posts, documentation sites, tutorials
        # Apply content quality filtering
        # Maintain source attribution
```

### 2. Vector Store (`vector_store.py`)

**Purpose:** FAISS-based semantic search functionality

**Key Functions:**
- `create_embeddings()` - Generate embeddings using sentence-transformers
- `build_index()` - Create FAISS index
- `semantic_search()` - Find relevant documents
- `save_index()` / `load_index()` - Persistence
- `merge_indices()` - Combine document and web content indices

**FAISS Configuration:**
- **Index Type:** IndexFlatL2 (exact search for POC)
- **Embedding Model:** `all-MiniLM-L6-v2` (384 dimensions)
- **Distance Metric:** L2 (Euclidean)
- **Dual Indices:** Separate indices for documents vs web content

```python
class VectorStore:
    def __init__(self):
        self.doc_index = faiss.IndexFlatL2(384)
        self.web_index = faiss.IndexFlatL2(384)
        self.combined_search = True
        self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
```

### 3. Web Scraper (`web_scraper.py`)

**Purpose:** Extract and process web content from forums and documentation sites

**Key Functions:**
- `scrape_specific_urls()` - Target specific forum posts/articles
- `scrape_forum_posts()` - Handle forum-specific structures
- `scrape_documentation_sites()` - Process technical documentation
- `crawl_site()` - Full site crawling with limits

**Supported Content Types:**
- Siemens Community Forums
- PLM documentation sites
- Technical tutorial blogs
- Stack Overflow Q&A
- Reddit discussions

```python
class WebScraper:
    def scrape_forum_posts(self, forum_urls: List[str]) -> List[Document]:
        # Extract questions and answers
        # Preserve thread context
        # Handle different forum structures
        
    def extract_main_content(self, html: str, url: str) -> Document:
        # Remove navigation, ads, headers
        # Focus on main content area
        # Preserve formatting for code blocks
```

### 4. Content Classifier (`content_classifier.py`)

**Purpose:** Filter and quality-check web content

**Key Functions:**
- `is_relevant_content()` - Check Teamcenter relevance
- `extract_qa_pairs()` - Parse forum Q&A structure
- `score_content_quality()` - Rate content usefulness
- `deduplicate_content()` - Remove similar content

**Quality Filters:**
- Minimum content length (100 chars)
- Teamcenter keyword presence
- Question-answer structure detection
- Spam/promotional content removal

### 5. Conversation Manager (`conversation.py`)

**Purpose:** Maintain context across multiple exchanges

**Memory Strategy:**
- **Sliding Window:** Keep last 10 Q&A pairs in context
- **Session Management:** Group related conversations
- **Context Compression:** Summarize older exchanges if needed
- **Source Tracking:** Remember which sources were used

**Storage Format:**
```json
{
  "session_id": "uuid4",
  "created_at": "timestamp",
  "messages": [
    {
      "role": "user",
      "content": "How do I set up user roles?",
      "timestamp": "...",
      "context_docs": ["doc1_chunk5", "web_forum_post_123"]
    },
    {
      "role": "assistant", 
      "content": "To set up user roles...",
      "timestamp": "...",
      "sources": ["teamcenter_config.pdf:p23", "forum_url"]
    }
  ]
}
```

### 6. RAG Pipeline (`rag_pipeline.py`)

**Purpose:** Orchestrate the retrieval and generation process

**Process Flow:**
1. **Query Processing:** Clean and expand user query
2. **Retrieval:** Find top-k relevant chunks (docs + web)
3. **Context Building:** Combine retrieved content + conversation history
4. **Generation:** Send to LLM with structured prompt
5. **Response Processing:** Extract answer and update memory

```python
class RAGPipeline:
    def process_query(self, query: str, session_id: str) -> Response:
        # 1. Enhance query with conversation context
        # 2. Semantic search in both document and web indices
        # 3. Rank and filter results by relevance
        # 4. Build context prompt with source attribution
        # 5. Call LLM API with Langfuse tracking
        # 6. Update conversation memory
        # 7. Return structured response with citations
```

### 7. LLM Client (`llm_client.py`)

**Purpose:** Abstract API calls and prompt engineering

**Features:**
- **Primary model:** Claude Sonnet 4 (`claude-sonnet-4-20250514`)
- **Fallback models:** GPT-4, Gemini (for comparison)
- **Prompt templates:** Specialized for technical documentation
- **Error handling:** Retry logic, fallbacks
- **Langfuse integration:** All calls tracked for evaluation

**Prompt Template:**
```
You are a Siemens Teamcenter Easy Plan configuration expert.
Use the provided documentation to give precise, step-by-step answers.

CONTEXT DOCUMENTS:
{retrieved_documents}

WEB SOURCES:
{retrieved_web_content}

CONVERSATION HISTORY:
{conversation_history}

USER QUESTION: {user_query}

Guidelines:
- Reference specific document sections and URLs
- Maintain sequential order for procedures  
- Distinguish between official docs and community sources
- Ask clarifying questions if ambiguous
- Mention if information is not in the provided sources
```

### 8. Langfuse Client (`langfuse_client.py`)

**Purpose:** Experiment tracking, model comparison, and evaluation

**Key Features:**
- **Trace all interactions:** Every query → retrieval → generation
- **A/B testing:** Compare different prompts/models on same questions
- **Evaluation metrics:** Answer relevance, source accuracy, completeness
- **Cost tracking:** Token usage across different models
- **Performance monitoring:** Response times, error rates

```python
class LangfuseClient:
    def create_experiment(self, name: str, config: Dict):
        # Model comparison: Sonnet 4 vs GPT-4 vs Gemini
        # Prompt variants: Different instruction styles
        # Retrieval params: TOP_K variations, chunk sizes
        
    def log_interaction(self, trace_id: str, query: str, response: str, 
                       model: str, prompt_version: str, sources: List[str]):
        # Track every interaction for analysis
        
    def evaluate_responses(self, test_set: List[QAPair]):
        # Run evaluation on your 15 test questions
        # Compare different configurations
```

## Data Models

### DocumentChunk
```python
@dataclass
class DocumentChunk:
    id: str
    content: str
    source: str           # Original file name or URL
    page: Optional[int]   # Page number if PDF
    section: str          # Section/chapter title
    chunk_type: str       # 'procedure', 'configuration', 'overview'
    source_type: str      # 'document', 'forum', 'documentation', 'tutorial'
    url: Optional[str]    # Source URL for web content
    scraped_date: Optional[datetime]  # When web content was scraped
    metadata: Dict[str, Any]
```

### ConversationMessage
```python
@dataclass
class ConversationMessage:
    role: str             # 'user' or 'assistant'
    content: str
    timestamp: datetime
    sources: List[str]    # Referenced document chunks and URLs
    session_id: str
    trace_id: str         # Langfuse trace ID
```

### SearchResult
```python
@dataclass  
class SearchResult:
    chunk: DocumentChunk
    similarity_score: float
    rank: int
    source_type: str      # 'document' or 'web'
```

### WebSource
```python
@dataclass
class WebSource:
    url: str
    source_type: str      # 'forum', 'documentation', 'tutorial'
    last_scraped: datetime
    content_hash: str     # For change detection
    relevance_score: float
```

## Configuration

```python
# config.py
class Config:
    # Vector Store
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    FAISS_INDEX_TYPE = "IndexFlatL2"
    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 100
    
    # RAG Pipeline
    TOP_K_RETRIEVAL = 5
    MAX_CONTEXT_LENGTH = 4000
    CONVERSATION_MEMORY_LIMIT = 10
    WEB_CONTENT_WEIGHT = 0.7  # Relative to document content
    
    # LLM Settings
    PRIMARY_MODEL = "claude-sonnet-4-20250514"
    FALLBACK_MODELS = ["gpt-4", "gemini-pro"]
    MAX_TOKENS = 1000
    TEMPERATURE = 0.1
    
    # Web Scraping
    WEB_SCRAPING_ENABLED = True
    MAX_PAGES_PER_SITE = 50
    SCRAPING_DELAY = 1.0  # Be respectful
    USER_AGENT = "TeamcenterAgent/1.0 (Educational)"
    
    # Content Filtering
    MIN_CONTENT_LENGTH = 100
    MAX_CONTENT_LENGTH = 5000
    RELEVANCE_THRESHOLD = 0.7
    
    # Langfuse Configuration
    LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
    LANGFUSE_HOST = "https://cloud.langfuse.com"
    
    # File Paths
    DOCUMENTS_DIR = "documents/"
    WEB_SOURCES_DIR = "web_sources/"
    DATA_DIR = "data/"
    CONVERSATIONS_FILE = "data/conversations.json"
    FAISS_INDEX_PATH = "data/vectors/"
    WEB_CONTENT_PATH = "data/web_content/"
    EXPERIMENTS_DIR = "experiments/"
    
    # Web Sources
    FORUM_URLS = [
        "https://community.sw.siemens.com/s/topic/teamcenter",
        # Add specific forum URLs
    ]
    
    DOCUMENTATION_SITES = [
        "https://docs.plm.automation.siemens.com/",
        # Add documentation sites
    ]
```

## CLI Interface

### Commands

```bash
# Basic Operations
python main.py                              # Start interactive session
python main.py --session <session_id>       # Load specific session
python main.py --history                    # Show conversation history

# Document Processing
python main.py --index-documents            # Process new documents
python main.py --reindex                    # Rebuild entire index

# Web Content Management
python main.py --scrape-urls web_sources/urls.txt           # Scrape specific URLs
python main.py --crawl-site https://community.siemens.com   # Crawl entire site
python main.py --update-web-content                         # Refresh existing content
python main.py --search-forums "user role configuration"   # Search for new forum content

# Evaluation & Experimentation
python main.py --evaluate --test-set test_questions.txt     # Run evaluation
python main.py --compare-models --models sonnet4,gpt4,gemini # Compare models
python main.py --experiment --config experiments/prompt_variants.yaml # Run experiments
python main.py --dashboard                                  # View Langfuse dashboard

# Maintenance
python main.py --cleanup-old-content --days 30             # Remove old web content
python main.py --stats                                     # Show system statistics
```

### Interactive Flow

```
$ python main.py

🔧 Teamcenter Easy Plan Agent v1.0
Loading document index (50 documents)... ✓
Loading web content index (150 pages)... ✓
Connecting to Langfuse... ✓
Model: Claude Sonnet 4 ✓

[Agent]: Hello! I'm ready to help with Teamcenter Easy Plan configuration.
         Ask me about setup procedures, user management, or workflows.
         [Trace ID: trace_abc123]

> How do I configure user roles for engineers?

[Agent]: Based on multiple sources, here's how to configure user roles for engineers:

         **From Official Documentation:**
         1. Navigate to Administration > User Management
         2. Select "Role Templates" 
         3. Create new role: "Engineer"...
         
         **Community Best Practices:**
         Many users recommend also setting up group-based permissions...
         
         Sources: 
         - user_management.pdf (p.23-25) [Official Documentation]
         - https://community.siemens.com/post/12345 [Community Forum]
         
         [Response time: 8.2s | Tokens: 234 | Cost: $0.008]

> What permissions should they have?

[Agent]: For the engineer role you're setting up, here are the recommended 
         permissions from both official docs and community experience...
```

## Web Content Integration

### Content Sources

**Forums:**
- Siemens Community Forums (primary)
- PLM World discussions
- Reddit r/PLM, r/CAD
- Stack Overflow Teamcenter tags
- LinkedIn professional groups

**Documentation Sites:**
- Official Siemens documentation portals
- PLM consultancy blogs
- University course materials
- Technical tutorial sites

**Content Types:**
- Q&A forum posts
- Step-by-step tutorials
- Configuration guides
- Troubleshooting discussions
- Best practices articles

### Scraping Strategy

**Targeted URL Collection (Recommended for POC):**
1. Manual curation of high-quality sources
2. Specific forum threads and documentation pages
3. Quality over quantity approach
4. Regular updates for new content

**Processing Pipeline:**
```python
URL → HTML Extraction → Content Cleaning → Relevance Filtering → Chunking → Indexing
```

**Quality Assurance:**
- Content length validation
- Teamcenter keyword presence
- Spam/promotional content removal
- Duplicate detection across sources
- Source reliability scoring

### Source Attribution

**Enhanced Citation System:**
```python
# Example response citations
Sources: 
- teamcenter_config.pdf (p.23-25) [Official Documentation]
- https://community.siemens.com/post/12345 [Community Forum - 2024]
- https://plm-tutorial.com/teamcenter-roles [Tutorial - Updated 2025]
- user_management.docx (Section 4.2) [Internal Documentation]
```

## Performance Characteristics

### Expected Metrics (50 Documents + 150-200 Web Pages)

**Processing Performance:**
- **Document Processing:** All 50 docs processed in ~30 seconds
- **Web Content Scraping:** 100 URLs processed in ~5 minutes
- **Index Building:** Combined index built in ~2 minutes
- **Index Size:** ~200-300MB total (vectors + metadata)
- **Memory Usage:** <500MB during operation
- **Storage Requirements:** <500MB total project size

**Query Performance:**
- **Total Response Time:** 5-15 seconds (acceptable for use case)
  - Document retrieval: ~0.5s
  - Web content retrieval: ~0.5s
  - Result ranking and filtering: ~0.5s
  - Claude Sonnet 4 API call: 4-12s (varies by complexity)
  - Response processing: ~0.5s

**Scalability Profile:**
- **Current Load:** 50 documents + 200 web pages, ~1500-2000 total chunks
- **FAISS Performance:** Sub-millisecond search with this dataset size
- **Concurrent Users:** 1 (single-user POC)
- **Session Storage:** JSON handles hundreds of conversations efficiently

**Model-Specific Performance (Claude Sonnet 4):**
- **Context Window:** 200K tokens (can hold entire conversation + docs)
- **Quality:** Excellent for technical documentation
- **Cost:** ~$0.005-0.020 per query (acceptable for POC)
- **Reliability:** High uptime, consistent responses

**Content Freshness:**
- **Documents:** Static, re-process only when updated
- **Web Content:** Refresh weekly/monthly via automated scripts
- **Forums:** Check for new posts in relevant threads

## Langfuse Integration & Experimentation

### Experiment Configurations

**Model Comparison:**
```yaml
# experiments/model_comparisons.yaml
experiments:
  - name: "model_comparison_v1"
    models: ["claude-sonnet-4", "gpt-4", "gemini-pro"]
    test_questions: "tests/test_questions.txt"
    evaluation_metrics: ["relevance", "accuracy", "completeness", "source_attribution"]
    web_content_enabled: true
```

**Prompt Variants:**
```yaml
# experiments/prompt_variants.yaml
prompts:
  - name: "detailed_expert"
    template: "You are a senior Teamcenter consultant with 10+ years experience..."
  - name: "step_by_step"
    template: "Provide clear step-by-step instructions with screenshots when mentioned..."
  - name: "context_aware" 
    template: "Consider the conversation history and build upon previous answers..."
  - name: "source_prioritized"
    template: "Prioritize official documentation over community sources..."
```

**Retrieval Experiments:**
```yaml
# experiments/retrieval_variants.yaml
retrieval_configs:
  - name: "docs_only"
    web_content_enabled: false
    top_k: 5
  - name: "balanced"
    web_content_weight: 0.5
    top_k: 8
  - name: "web_heavy"
    web_content_weight: 0.8
    top_k: 10
```

### Evaluation Metrics

**Automated Metrics:**
- **Relevance:** How well the answer addresses the question
- **Source Accuracy:** Correct document/URL references
- **Completeness:** All necessary steps included
- **Consistency:** Similar answers to similar questions
- **Response Time:** End-to-end latency
- **Cost Efficiency:** Tokens used per query

**Manual Evaluation (for your 15 test questions):**
- **Technical Accuracy:** Correctness of procedural steps
- **Clarity:** Ease of understanding for end users
- **Actionability:** Can a user follow the instructions successfully
- **Source Quality:** Mix of official vs community sources appropriately

### Dashboard Views

**Query Analysis:**
- Most common questions and success rates
- Source attribution patterns
- User satisfaction trends

**Model Performance:**
- Comparative metrics across models
- Cost analysis per model
- Response time distributions

**Content Analysis:**
- Document vs web content usage
- Source reliability scoring
- Content freshness impact

**Experiment Results:**
- A/B test outcomes
- Statistical significance testing
- Recommendation generation

## Error Handling

### Document Processing Errors
- **Unsupported file formats:** Skip with warning, log for review
- **Corrupted files:** Log error, continue processing other files
- **Empty chunks:** Filter out automatically
- **Encoding issues:** Attempt multiple encodings, fallback to binary

### Web Scraping Errors
- **HTTP errors (404, 500):** Log and skip, retry later
- **Rate limiting:** Implement exponential backoff
- **JavaScript-heavy sites:** Use Selenium fallback
- **Robots.txt violations:** Respect and skip
- **Content parsing failures:** Log for manual review

### API Errors
- **Rate limits:** Exponential backoff, Langfuse logs delay
- **Network issues:** Retry with fallback models
- **Token limits:** Intelligent context truncation
- **Langfuse connection issues:** Local fallback logging
- **Authentication errors:** Clear error messages, configuration guidance

### Vector Store Errors
- **Missing index:** Rebuild automatically from source
- **Corrupted FAISS file:** Fallback to re-indexing
- **Memory issues:** Not expected with current dataset size, but implement batching
- **Dimension mismatches:** Validate embeddings before indexing

### Runtime Errors
- **Session corruption:** Create new session, preserve conversation history
- **Configuration errors:** Validate configuration on startup
- **Disk space issues:** Implement cleanup procedures
- **Permission errors:** Clear error messages with solutions

## Security Considerations

### Data Privacy
- **Local Processing:** All document and web content processing done locally
- **API Calls:** Only query content and responses sent to LLM APIs
- **Conversation Storage:** All conversation history stored locally only
- **Web Content:** Scraped content stored locally, not re-transmitted
- **Langfuse Data:** Only metadata and evaluation metrics, no sensitive content

### Input Validation
- **File Path Sanitization:** Prevent directory traversal attacks
- **URL Validation:** Validate URLs before scraping
- **Query Length Limits:** Prevent overly long queries
- **Content Filtering:** Remove potentially malicious content from scraped data
- **SQL Injection Prevention:** Use parameterized queries if database is added

### Web Scraping Ethics
- **Robots.txt Compliance:** Always check and respect robots.txt
- **Rate Limiting:** Implement delays between requests
- **User Agent Identification:** Clear identification of scraping bot
- **Terms of Service:** Review and comply with site terms
- **Fair Use:** Educational/internal use only

### API Security
- **Environment Variables:** Store all API keys in environment variables
- **Key Rotation:** Support for API key rotation
- **Access Logging:** Log all API calls for monitoring
- **Error Handling:** Don't expose API keys in error messages
- **Rate Monitoring:** Track API usage to prevent overages

### Access Control
- **Single User:** Designed for individual use, no multi-user authentication
- **File Permissions:** Secure storage of configuration and data files
- **Temporary Files:** Clean up temporary files after processing
- **Backup Security:** Secure storage of conversation and configuration backups

---

## Getting Started

1. **Environment Setup:**
   ```bash
   pip install -r requirements.txt
   export ANTHROPIC_API_KEY="your_key"
   export LANGFUSE_PUBLIC_KEY="your_key"
   export LANGFUSE_SECRET_KEY="your_key"
   ```

2. **Initial Setup:**
   ```bash
   python main.py --index-documents
   python main.py --scrape-urls web_sources/urls.txt
   ```

3. **Start Agent:**
   ```bash
   python main.py
   ```

4. **Run Evaluation:**
   ```bash
   python main.py --evaluate --test-set tests/test_questions.txt
   ```

This design provides a comprehensive foundation for your Teamcenter Easy Plan AI agent with document processing, web content integration, conversation memory, and experimental capabilities.