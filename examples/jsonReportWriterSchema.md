```Python
from typing import List, Union, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from enum import Enum

class ContentType(str, Enum):
    PARAGRAPH = "paragraph"
    LIST = "list" 
    TIMELINE = "timeline"
    DEFINITION_LIST = "definition_list"
    NUMBERED_SECTION = "numbered_section"

class SectionType(str, Enum):  # NEW: Consistent with ContentType pattern
    OPENING = "opening"
    BODY = "body"
    CLOSING = "closing"

class TextWithCitations(BaseModel):
    """Text content with its associated citations."""
    text: str
    citations: List[int] = Field(default_factory=list)

class DefinitionItem(BaseModel):
    """Key-value definition pairs."""
    key: str
    value: TextWithCitations

class NumberedSection(BaseModel):
    """Numbered sections like '1. Initial Access'."""
    number: int
    title: str
    subtitle: Optional[str] = None
    mitre_id: Optional[str] = None
    content: List[Union['ContentBlock', 'NumberedSection']] = Field(default_factory=list)

class ContentBlock(BaseModel):
    """Individual content block within a section."""
    type: ContentType
    value: Union[
        TextWithCitations,
        List[TextWithCitations], 
        List[DefinitionItem],
        NumberedSection
    ]
    formatting: Dict[str, Any] = Field(default_factory=dict)

class Section(BaseModel):
    """Hierarchical section structure."""
    title: str
    section_type: SectionType  # Now an enum!
    hierarchy_level: int = 1
    content: List[Union['Section', ContentBlock]] = Field(default_factory=list)

class ResearchReportJSON(BaseModel):
    """Complete structured research report."""
    
    title: str
    sections: List[Section] = Field(default_factory=list)
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    generated_at: str
    language: str = "en"
```

