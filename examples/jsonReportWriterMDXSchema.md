Here is a Pydantic schema designed to transform a markdown document into a structured JSON representation suitable for rendering into an MDX file.

This schema is "flat," representing the document as a linear sequence of blocks. The LLM's task is to chunk the source document into the appropriate block type.

```Python
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
    items: List[DefinitionListItem] = Field(..., description="The list of key-value pairs.")

# Block Type 3: A Custom Component for a MITRE ATT&CK Chain

class MitreAttackStep(BaseModel):
    """A single step within a MITRE ATT&CK chain."""
    number: int = Field(..., description="The step number in the attack sequence.")
    title: str = Field(..., description="The title of the ATT&CK stage (e.g., 'Initial Access').")
    mitre_id: Optional[str] = Field(None, description="The corresponding MITRE technique ID (e.g., 'T1190').")
    description: str = Field(..., description="The description of the step, as a markdown string.")

class MitreAttackChainComponent(BaseModel):
    """
    Represents the entire MITRE ATT&CK chain.
    This will be rendered as a custom <MitreAttackChain> component in MDX.
    """
    type: Literal["mitre_attack_chain_component"] = "mitre_attack_chain_component"
    title: str = Field(..., description="The title for the attack chain section (e.g., 'The Full Attack Chain').")
    steps: List[MitreAttackStep] = Field(..., description="The sequential steps of the attack.")

# The Top-Level Schema: The Document Itself

class MdxDocument(BaseModel):
    """
    The complete report, represented as a flat list of content and component blocks.
    """
    document_title: str = Field(..., description="The main title of the entire document.")
    blocks: List[Union[MarkdownBlock, DefinitionListComponent, MitreAttackChainComponent]] = Field(
        ..., 
        description="The sequence of blocks that constitute the document."
    )

```

Here is an example prompt that instructs an LLM on how to use the schema above.

````Markdown
# Role: AI Content Structuring Agent

Your task is to transform a given research article into a structured JSON object that conforms to the `MdxDocument` Pydantic schema.

The goal is to represent the article as a linear sequence of "blocks". You must iterate through the document and decide which block type is most appropriate for each section of the content.

## Schema and Block Types:

You have been provided with the `MdxDocument` schema, which contains a list of `blocks`. The available block types are:

1.  **`MarkdownBlock`**:
    *   This is your **default** tool.
    *   Use it for all general content, including headers (`#`), paragraphs, blockquotes, and standard markdown lists (`-`, `*`, `1.`).
    *   The `content` field should contain the **raw, original markdown text** for that chunk. Preserve all formatting.
    *   You should group contiguous sections of markdown into a single `MarkdownBlock` where it makes sense. For example, a header and its following paragraphs can be one block.

2.  **`DefinitionListComponent`**:
    *   This is a **specialized** tool.
    *   You MUST use this block **only** when you identify a section that is semantically a profile or a list of key-value definitions. A clear signal for this is a list of items where each item starts with a bolded term followed by a colon (e.g., "**Origin and Attribution**: ...").
    *   Extract the section title and the list of key-value pairs into the `props`.

3.  **`MitreAttackChainComponent`**:
    *   This is a **specialized** tool.
    *   You MUST use this block **only** for the section describing a numbered sequence of MITRE ATT&CK tactics.
    *   Extract the overall title for the chain and then process each numbered step, capturing its number, title, MITRE ID (if present), and full description.

## Instructions:

1.  Read the entire input article to understand its structure.
2.  Start from the beginning and create the `MdxDocument` object, starting with the `document_title`.
3.  Process the article sequentially, chunking it into the appropriate block types.
4.  Default to using `MarkdownBlock`. Only switch to a specialized component block when the content's semantic meaning is a clear match for that component.
5.  Ensure no content from the original article is lost. Every part of the text must be placed into one of the blocks.
6.  Your final output must be a single JSON object that strictly validates against the `MdxDocument` schema.

## Input Article:

```markdown
{{article_text}}
````

## JSON Output:

```JSON
```

```
```

