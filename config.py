"""
Configuration management for Teamcenter Easy Plan AI Agent
"""
import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the Teamcenter Easy Plan AI Agent"""

    # Project Paths
    PROJECT_ROOT = Path(__file__).parent
    DATA_DIR = PROJECT_ROOT / os.getenv("DATA_DIRECTORY", "data")
    DOCUMENTS_DIR = PROJECT_ROOT / os.getenv("DOCUMENTS_DIRECTORY", "documents")
    WEB_SOURCES_DIR = PROJECT_ROOT / os.getenv("WEB_SOURCES_DIRECTORY", "web_sources")
    EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"
    TESTS_DIR = PROJECT_ROOT / "tests"

    # Ensure directories exist
    DATA_DIR.mkdir(exist_ok=True)
    DOCUMENTS_DIR.mkdir(exist_ok=True)
    WEB_SOURCES_DIR.mkdir(exist_ok=True)
    (DATA_DIR / "vectors").mkdir(exist_ok=True)
    (DATA_DIR / "web_content").mkdir(exist_ok=True)
    (DATA_DIR / "web_content" / "forums").mkdir(exist_ok=True)
    (DATA_DIR / "web_content" / "documentation").mkdir(exist_ok=True)
    (DATA_DIR / "web_content" / "tutorials").mkdir(exist_ok=True)

    # API Keys (Required)
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
    LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

    # Optional API Keys for fallback models
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    # Vector Store Settings
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    FAISS_INDEX_TYPE = "IndexFlatL2"
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

    # RAG Pipeline Settings
    TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "5"))
    MAX_CONTEXT_LENGTH = int(os.getenv("MAX_CONTEXT_LENGTH", "4000"))
    CONVERSATION_MEMORY_LIMIT = 10
    WEB_CONTENT_WEIGHT = 0.7  # Relative weight of web content vs documents

    # LLM Settings
    PRIMARY_MODEL = os.getenv("PRIMARY_MODEL", "claude-sonnet-4-20250514")
    FALLBACK_MODELS = ["gpt-4", "gemini-pro"]
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))

    # Web Scraping Settings
    WEB_SCRAPING_ENABLED = os.getenv("WEB_SCRAPING_ENABLED", "true").lower() == "true"
    MAX_PAGES_PER_SITE = int(os.getenv("MAX_PAGES_PER_SITE", "50"))
    SCRAPING_DELAY = float(os.getenv("SCRAPING_DELAY", "1.0"))
    USER_AGENT = os.getenv("USER_AGENT", "TeamcenterAgent/1.0 (Educational)")

    # Content Filtering
    MIN_CONTENT_LENGTH = 100
    MAX_CONTENT_LENGTH = 5000
    RELEVANCE_THRESHOLD = 0.7

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # File Paths
    CONVERSATIONS_FILE = DATA_DIR / "conversations.json"
    PROCESSED_DOCS_FILE = DATA_DIR / "processed_docs.json"
    CONTENT_METADATA_FILE = DATA_DIR / "content_metadata.json"
    FAISS_INDEX_PATH = DATA_DIR / "vectors"
    WEB_CONTENT_PATH = DATA_DIR / "web_content"

    # Web Sources Configuration Files
    URLS_FILE = WEB_SOURCES_DIR / "urls.txt"
    FORUMS_CONFIG_FILE = WEB_SOURCES_DIR / "forums_config.yaml"
    SITEMAP_URLS_FILE = WEB_SOURCES_DIR / "sitemap_urls.txt"
    CONTENT_SOURCES_FILE = WEB_SOURCES_DIR / "content_sources.md"

    # Test Files
    TEST_QUESTIONS_FILE = TESTS_DIR / "test_questions.txt"
    TEST_DOCUMENTS_DIR = TESTS_DIR / "test_documents"

    # Default Web Sources
    FORUM_URLS = [
        "https://community.sw.siemens.com/s/topic/teamcenter",
        # Add more specific forum URLs as needed
    ]

    DOCUMENTATION_SITES = [
        "https://docs.plm.automation.siemens.com/",
        # Add more documentation sites as needed
    ]

    @classmethod
    def validate_config(cls) -> List[str]:
        """Validate required configuration and return list of errors"""
        errors = []

        # Check required API keys
        if not cls.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY is required")

        if not cls.LANGFUSE_PUBLIC_KEY:
            errors.append("LANGFUSE_PUBLIC_KEY is required for experiment tracking")

        if not cls.LANGFUSE_SECRET_KEY:
            errors.append("LANGFUSE_SECRET_KEY is required for experiment tracking")

        # Validate numeric settings
        if cls.CHUNK_SIZE < 100:
            errors.append("CHUNK_SIZE must be at least 100 characters")

        if cls.CHUNK_OVERLAP >= cls.CHUNK_SIZE:
            errors.append("CHUNK_OVERLAP must be less than CHUNK_SIZE")

        if cls.TOP_K_RETRIEVAL < 1:
            errors.append("TOP_K_RETRIEVAL must be at least 1")

        if cls.MAX_TOKENS < 100:
            errors.append("MAX_TOKENS must be at least 100")

        if not (0.0 <= cls.TEMPERATURE <= 2.0):
            errors.append("TEMPERATURE must be between 0.0 and 2.0")

        if cls.SCRAPING_DELAY < 0.1:
            errors.append("SCRAPING_DELAY must be at least 0.1 seconds")

        return errors

    @classmethod
    def get_model_config(cls, model_name: Optional[str] = None) -> dict:
        """Get configuration for a specific model"""
        model = model_name or cls.PRIMARY_MODEL

        base_config = {
            "max_tokens": cls.MAX_TOKENS,
            "temperature": cls.TEMPERATURE,
        }

        if model.startswith("claude"):
            return {
                **base_config,
                "api_key": cls.ANTHROPIC_API_KEY,
                "model": model,
            }
        elif model.startswith("gpt"):
            return {
                **base_config,
                "api_key": cls.OPENAI_API_KEY,
                "model": model,
            }
        elif model.startswith("gemini"):
            return {
                **base_config,
                "api_key": cls.GOOGLE_API_KEY,
                "model": model,
            }
        else:
            raise ValueError(f"Unsupported model: {model}")

    @classmethod
    def print_config_summary(cls):
        """Print a summary of current configuration"""
        print("=== Teamcenter Easy Plan AI Agent Configuration ===")
        print(f"Project Root: {cls.PROJECT_ROOT}")
        print(f"Data Directory: {cls.DATA_DIR}")
        print(f"Documents Directory: {cls.DOCUMENTS_DIR}")
        print(f"Primary Model: {cls.PRIMARY_MODEL}")
        print(f"Embedding Model: {cls.EMBEDDING_MODEL}")
        print(f"Chunk Size: {cls.CHUNK_SIZE}")
        print(f"Top-K Retrieval: {cls.TOP_K_RETRIEVAL}")
        print(f"Web Scraping Enabled: {cls.WEB_SCRAPING_ENABLED}")
        print(f"Log Level: {cls.LOG_LEVEL}")

        # Check for API keys (without revealing them)
        print(f"Anthropic API Key: {'OK Set' if cls.ANTHROPIC_API_KEY else 'X Missing'}")
        print(f"Langfuse Keys: {'OK Set' if cls.LANGFUSE_PUBLIC_KEY and cls.LANGFUSE_SECRET_KEY else 'X Missing'}")
        print(f"OpenAI API Key: {'OK Set' if cls.OPENAI_API_KEY else 'O Optional'}")
        print(f"Google API Key: {'OK Set' if cls.GOOGLE_API_KEY else 'O Optional'}")
        print("=" * 50)


# Validate configuration on import
config_errors = Config.validate_config()
if config_errors:
    print("⚠️  Configuration Errors:")
    for error in config_errors:
        print(f"   - {error}")
    print("Please check your .env file and fix these issues.")