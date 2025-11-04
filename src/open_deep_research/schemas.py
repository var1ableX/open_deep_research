from typing import List, Union, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field

# Block Type 1: The Default Fallback for Plain Markdown

class MarkdownBlock(BaseModel):
    """
    Used for any standard content that doesn't map to a special component.
    The content should be the raw, original markdown, including headers, lists, etc.
    """
    type: Literal["markdown_block"] = "markdown_block"
    content: str = Field(..., description="The raw markdown content for the block.")

# Block Type 2: A Custom Component for Definition Lists
#
# NOTE: WHY USE A COMPONENT INSTEAD OF PLAIN MARKDOWN?
# You are correct that a definition list could just be part of a `MarkdownBlock`.
# The reason for defining a dedicated component is to enforce a specific,
# consistent structure for semantically important data. This allows you to render
# it with a unique, rich UI instead of leaving it to standard markdown formatting.
# For example, you could define a `NistControlComponent` with fields for
# `action_title`, `csf_references`, and `description`. This guarantees that
# the data is always perfectly structured for a custom React component that might
# add icons, special styling, or interactive elements.

class DefinitionListItem(BaseModel):
    """A single key-value item for a definition list."""
    key: str = Field(..., description="The term or key being defined (e.g., 'Origin and Attribution').")
    value: str = Field(..., description="The definition or value, as a markdown string.")

class DefinitionListComponent(BaseModel):
    """
    Represents a semantic definition list, like a threat actor profile.
    This will be rendered as a custom <DefinitionList> component in MDX.
    """
    type: Literal["definition_list_component"] = "definition_list_component"
    title: str = Field(..., description="The title for the definition list section.")
    item_key_display_name: str = Field(..., description="The table column header label for the key column. Should be brief and general (e.g., 'Ref', 'ID', 'Key', 'Field'). Avoid overly specific or verbose names.")
    item_value_display_name: str = Field(..., description="The table column header label for the value column. Should be brief and general (e.g., 'Description', 'Value', 'Details'). Avoid overly specific or verbose names.")
    items: List[DefinitionListItem] = Field(..., description="The list of key-value pairs.")

# Block Type 3: A Custom Component for a MITRE ATT&CK Chain

class MitreTactic(BaseModel):
    """A MITRE ATT&CK tactic with ID and name."""
    id: str = Field(..., description="The MITRE ATT&CK tactic ID (e.g., 'TA0001').")
    name: str = Field(..., description="The name of the tactic (e.g., 'Initial Access').")

class MitreTechnique(BaseModel):
    """A MITRE ATT&CK technique with ID and name."""
    id: str = Field(..., description="The MITRE ATT&CK technique ID (e.g., 'T1190').")
    name: str = Field(..., description="The name of the technique (e.g., 'Exploit Public-Facing Application').")

class MitreAttackStep(BaseModel):
    """A single step within a MITRE ATT&CK chain."""
    date: Optional[str] = Field(None, description="The date of the attack step (if present).")
    action: str = Field(..., description="A description of the corresponding attack used by the threat actor in the story.")
    tactic: MitreTactic = Field(..., description="The MITRE ATT&CK tactic associated with this step.")
    techniques: List[MitreTechnique] = Field(..., description="The MITRE ATT&CK techniques associated with this step.")

class MitreAttackChainComponent(BaseModel):
    """
    Represents the entire MITRE ATT&CK chain.
    This will be rendered as a custom <MitreAttackChain> component in MDX.
    """
    type: Literal["mitre_attack_chain_component"] = "mitre_attack_chain_component"
    title: str = Field(..., description="The title for the attack chain section (e.g., 'The Full Attack Chain').")
    attack_chain: List[MitreAttackStep] = Field(..., alias="attackChain", description="The sequential steps of the attack chain.")

# Block Type 4: A Custom Component for Sources

class SourceItem(BaseModel):
    """A single source citation item."""
    number: int = Field(..., description="The citation number (e.g., 1, 2, 3).")
    title: str = Field(..., description="The source title or name (e.g., 'The Hacker News').")
    url: str = Field(..., description="The source URL.")

class SourcesComponent(BaseModel):
    """
    Represents a list of numbered source citations.
    This will be rendered as a custom <Sources> component in MDX.
    """
    type: Literal["sources_component"] = "sources_component"
    title: str = Field(..., description="The title for the sources section (typically 'Sources').")
    sources: List[SourceItem] = Field(..., description="The list of numbered source citations.")

# The Top-Level Schema: The Document Itself

class MdxDocument(BaseModel):
    """
    The complete report, represented as a flat list of content and component blocks.
    """
    document_title: str = Field(..., description="The main title of the entire document.")
    blocks: List[Union[MarkdownBlock, DefinitionListComponent, MitreAttackChainComponent, SourcesComponent]] = Field(
        ..., 
        description="The sequence of blocks that constitute the document."
    )
