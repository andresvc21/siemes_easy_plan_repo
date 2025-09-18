"""
Core data models for the Teamcenter Easy Plan AI Agent.

This module defines the fundamental data structures used throughout the system
for document processing, conversation management, search results, and web sources.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import json
from enum import Enum


class DocumentType(Enum):
    """Enumeration of supported document types."""
    PDF = "pdf"
    DOCX = "docx"
    MD = "markdown"
    TXT = "text"
    WEB = "web"
    UNKNOWN = "unknown"


class ContentSource(Enum):
    """Enumeration of content sources."""
    LOCAL_DOCUMENT = "local_document"
    WEB_SCRAPE = "web_scrape"
    FORUM_POST = "forum_post"
    DOCUMENTATION = "documentation"
    MANUAL = "manual"


@dataclass
class DocumentChunk:
    """
    Represents a chunk of processed document content with metadata.

    This is the fundamental unit for document processing and retrieval.
    Each chunk contains a portion of text with associated metadata for
    tracking, indexing, and citation purposes.
    """
    content: str
    source_file: str
    chunk_id: str
    start_char: int = 0
    end_char: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    document_type: DocumentType = DocumentType.UNKNOWN
    content_source: ContentSource = ContentSource.LOCAL_DOCUMENT
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Post-initialization to set derived fields."""
        if not self.end_char and self.content:
            self.end_char = self.start_char + len(self.content)

        # Auto-detect document type from file extension if not set
        if self.document_type == DocumentType.UNKNOWN and self.source_file:
            self._detect_document_type()

    def _detect_document_type(self):
        """Auto-detect document type from file extension."""
        try:
            suffix = Path(self.source_file).suffix.lower()
            type_mapping = {
                '.pdf': DocumentType.PDF,
                '.docx': DocumentType.DOCX,
                '.md': DocumentType.MD,
                '.txt': DocumentType.TXT,
                '.html': DocumentType.WEB,
                '.htm': DocumentType.WEB,
            }
            self.document_type = type_mapping.get(suffix, DocumentType.UNKNOWN)
        except Exception:
            self.document_type = DocumentType.UNKNOWN

    @property
    def length(self) -> int:
        """Return the length of the content."""
        return len(self.content)

    @property
    def word_count(self) -> int:
        """Return approximate word count."""
        return len(self.content.split())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'content': self.content,
            'source_file': self.source_file,
            'chunk_id': self.chunk_id,
            'start_char': self.start_char,
            'end_char': self.end_char,
            'metadata': self.metadata,
            'embedding': self.embedding,
            'document_type': self.document_type.value,
            'content_source': self.content_source.value,
            'created_at': self.created_at.isoformat(),
            'length': self.length,
            'word_count': self.word_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentChunk':
        """Create instance from dictionary."""
        # Convert enum strings back to enums
        doc_type = DocumentType(data.get('document_type', DocumentType.UNKNOWN.value))
        content_src = ContentSource(data.get('content_source', ContentSource.LOCAL_DOCUMENT.value))
        created_at = datetime.fromisoformat(data.get('created_at', datetime.now().isoformat()))

        return cls(
            content=data['content'],
            source_file=data['source_file'],
            chunk_id=data['chunk_id'],
            start_char=data.get('start_char', 0),
            end_char=data.get('end_char', 0),
            metadata=data.get('metadata', {}),
            embedding=data.get('embedding'),
            document_type=doc_type,
            content_source=content_src,
            created_at=created_at
        )


@dataclass
class ConversationMessage:
    """
    Represents a single message in a conversation between user and AI.

    Used for maintaining conversation history and context for the RAG system.
    """
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: str = ""
    sources: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    token_count: Optional[int] = None

    def __post_init__(self):
        """Generate message ID if not provided."""
        if not self.message_id:
            self.message_id = f"{self.role}_{self.timestamp.strftime('%Y%m%d_%H%M%S_%f')}"

    @property
    def is_user_message(self) -> bool:
        """Check if this is a user message."""
        return self.role.lower() == 'user'

    @property
    def is_assistant_message(self) -> bool:
        """Check if this is an assistant message."""
        return self.role.lower() == 'assistant'

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'message_id': self.message_id,
            'sources': self.sources,
            'metadata': self.metadata,
            'token_count': self.token_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationMessage':
        """Create instance from dictionary."""
        timestamp = datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat()))

        return cls(
            role=data['role'],
            content=data['content'],
            timestamp=timestamp,
            message_id=data.get('message_id', ''),
            sources=data.get('sources', []),
            metadata=data.get('metadata', {}),
            token_count=data.get('token_count')
        )


@dataclass
class SearchResult:
    """
    Represents a search result with relevance scoring and source information.

    Used by the RAG system to return ranked search results with attribution.
    """
    content: str
    source: str
    score: float
    chunk_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    document_type: DocumentType = DocumentType.UNKNOWN
    content_source: ContentSource = ContentSource.LOCAL_DOCUMENT
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def is_relevant(self) -> bool:
        """Check if result meets relevance threshold."""
        # Default threshold - can be made configurable
        return self.score >= 0.7

    @property
    def relevance_level(self) -> str:
        """Return human-readable relevance level."""
        if self.score >= 0.9:
            return "Very High"
        elif self.score >= 0.8:
            return "High"
        elif self.score >= 0.7:
            return "Medium"
        elif self.score >= 0.5:
            return "Low"
        else:
            return "Very Low"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'content': self.content,
            'source': self.source,
            'score': self.score,
            'chunk_id': self.chunk_id,
            'metadata': self.metadata,
            'document_type': self.document_type.value,
            'content_source': self.content_source.value,
            'timestamp': self.timestamp.isoformat(),
            'relevance_level': self.relevance_level,
            'is_relevant': self.is_relevant
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchResult':
        """Create instance from dictionary."""
        doc_type = DocumentType(data.get('document_type', DocumentType.UNKNOWN.value))
        content_src = ContentSource(data.get('content_source', ContentSource.LOCAL_DOCUMENT.value))
        timestamp = datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat()))

        return cls(
            content=data['content'],
            source=data['source'],
            score=data['score'],
            chunk_id=data.get('chunk_id', ''),
            metadata=data.get('metadata', {}),
            document_type=doc_type,
            content_source=content_src,
            timestamp=timestamp
        )


@dataclass
class WebSource:
    """
    Represents a web source with scraping metadata and content quality metrics.

    Used for managing web content sources, tracking scraping status,
    and maintaining content quality information.
    """
    url: str
    title: str = ""
    content: str = ""
    last_scraped: Optional[datetime] = None
    scrape_frequency: str = "monthly"  # daily, weekly, monthly, manual
    status: str = "pending"  # pending, scraped, failed, excluded
    content_type: str = "unknown"  # documentation, forum, blog, manual
    quality_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    chunk_count: int = 0

    @property
    def is_stale(self) -> bool:
        """Check if content needs re-scraping based on frequency."""
        if not self.last_scraped:
            return True

        now = datetime.now()
        time_diff = now - self.last_scraped

        frequency_days = {
            "daily": 1,
            "weekly": 7,
            "monthly": 30,
            "manual": float('inf')  # Never stale for manual
        }

        threshold_days = frequency_days.get(self.scrape_frequency, 30)
        return time_diff.days >= threshold_days

    @property
    def is_high_quality(self) -> bool:
        """Check if content meets quality threshold."""
        return self.quality_score >= 0.7

    @property
    def status_emoji(self) -> str:
        """Return text representation of status."""
        status_emojis = {
            "pending": "PENDING",
            "scraped": "SUCCESS",
            "failed": "FAILED",
            "excluded": "EXCLUDED"
        }
        return status_emojis.get(self.status, "UNKNOWN")

    def mark_scraped(self, content: str, title: str = "", quality_score: float = 0.0):
        """Mark as successfully scraped."""
        self.content = content
        self.title = title
        self.last_scraped = datetime.now()
        self.status = "scraped"
        self.quality_score = quality_score
        self.error_message = ""

    def mark_failed(self, error_message: str):
        """Mark as failed scraping."""
        self.status = "failed"
        self.error_message = error_message
        self.last_scraped = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'url': self.url,
            'title': self.title,
            'content': self.content,
            'last_scraped': self.last_scraped.isoformat() if self.last_scraped else None,
            'scrape_frequency': self.scrape_frequency,
            'status': self.status,
            'content_type': self.content_type,
            'quality_score': self.quality_score,
            'metadata': self.metadata,
            'error_message': self.error_message,
            'chunk_count': self.chunk_count,
            'is_stale': self.is_stale,
            'is_high_quality': self.is_high_quality,
            'status_emoji': self.status_emoji
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebSource':
        """Create instance from dictionary."""
        last_scraped = None
        if data.get('last_scraped'):
            last_scraped = datetime.fromisoformat(data['last_scraped'])

        return cls(
            url=data['url'],
            title=data.get('title', ''),
            content=data.get('content', ''),
            last_scraped=last_scraped,
            scrape_frequency=data.get('scrape_frequency', 'monthly'),
            status=data.get('status', 'pending'),
            content_type=data.get('content_type', 'unknown'),
            quality_score=data.get('quality_score', 0.0),
            metadata=data.get('metadata', {}),
            error_message=data.get('error_message', ''),
            chunk_count=data.get('chunk_count', 0)
        )


@dataclass
class ConversationSession:
    """
    Represents a conversation session with multiple messages.

    Used for grouping related messages and managing conversation context.
    """
    session_id: str
    messages: List[ConversationMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, message: ConversationMessage):
        """Add a message to the session."""
        self.messages.append(message)
        self.last_activity = datetime.now()

    def get_recent_messages(self, count: int = 10) -> List[ConversationMessage]:
        """Get the most recent messages (for context window)."""
        return self.messages[-count:] if len(self.messages) > count else self.messages

    @property
    def message_count(self) -> int:
        """Return total number of messages."""
        return len(self.messages)

    @property
    def total_tokens(self) -> int:
        """Return total token count for all messages."""
        return sum(msg.token_count or 0 for msg in self.messages)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'session_id': self.session_id,
            'messages': [msg.to_dict() for msg in self.messages],
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'metadata': self.metadata,
            'message_count': self.message_count,
            'total_tokens': self.total_tokens
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationSession':
        """Create instance from dictionary."""
        messages = [ConversationMessage.from_dict(msg) for msg in data.get('messages', [])]
        created_at = datetime.fromisoformat(data.get('created_at', datetime.now().isoformat()))
        last_activity = datetime.fromisoformat(data.get('last_activity', datetime.now().isoformat()))

        return cls(
            session_id=data['session_id'],
            messages=messages,
            created_at=created_at,
            last_activity=last_activity,
            metadata=data.get('metadata', {})
        )


# Utility functions for model operations
def save_models_to_json(models: List[Union[DocumentChunk, ConversationMessage, SearchResult, WebSource]],
                       file_path: str):
    """Save a list of model instances to JSON file."""
    data = [model.to_dict() for model in models]
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_document_chunks_from_json(file_path: str) -> List[DocumentChunk]:
    """Load DocumentChunk instances from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [DocumentChunk.from_dict(item) for item in data]


def load_web_sources_from_json(file_path: str) -> List[WebSource]:
    """Load WebSource instances from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [WebSource.from_dict(item) for item in data]


def load_conversation_session_from_json(file_path: str) -> ConversationSession:
    """Load ConversationSession from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return ConversationSession.from_dict(data)