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

# Block Type 1.5: Semantic Section with Explicit Heading

class SectionBlock(BaseModel):
    """
    Represents a document section with an explicit heading and content.
    This allows granular control over section-level formatting and styling.
    Use this for any content section that has a markdown heading (# through ######).
    """
    type: Literal["section_block"] = "section_block"
    level: int = Field(..., description="Heading level (1-6, corresponding to h1-h6). Count the number of # symbols in the original markdown.")
    title: str = Field(..., description="The section heading text WITHOUT the markdown # symbols.")
    content: str = Field(..., description="The markdown content under this heading (excluding the heading itself). If a heading has no content before the next heading, use an empty string.")

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
    blocks: List[Union[MarkdownBlock, SectionBlock, DefinitionListComponent, MitreAttackChainComponent, SourcesComponent]] = Field(
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

2.  **`SectionBlock`**:
    *   This is a **semantic** tool for representing document structure.
    *   You MUST use this block for ANY section that has a markdown heading (# through ######).
    *   **CRITICAL RULE**: Every heading at ANY level (##, ###, ####, etc.) creates a NEW `SectionBlock`.
    *   Extract the heading level by counting the number of # symbols (1-6).
    *   Extract the heading text WITHOUT the # symbols or any trailing #.
    *   The `content` field contains ONLY the text/paragraphs/lists that follow the heading, EXCLUDING any subsequent headings.
    *   The `content` field should NEVER contain markdown headings (no #, ##, ###, etc.) - those become separate blocks.
    *   If a heading has no content before the next heading, use an empty string for `content`.
    
    **Complete Example:** For this markdown input:
    ```markdown
    ## Background
    
    The incident began in early 2025.
    
    ### Attack Vector
    
    Malicious code was injected.
    
    ### Impact Assessment
    
    Over 10,000 systems affected.
    
    ## Recommendations
    
    Implement controls.
    ```
    
    You would create FOUR separate `SectionBlock` entries:
    ```json
    [
      {{
        "type": "section_block",
        "level": 2,
        "title": "Background",
        "content": "The incident began in early 2025."
      }},
      {{
        "type": "section_block",
        "level": 3,
        "title": "Attack Vector",
        "content": "Malicious code was injected."
      }},
      {{
        "type": "section_block",
        "level": 3,
        "title": "Impact Assessment",
        "content": "Over 10,000 systems affected."
      }},
      {{
        "type": "section_block",
        "level": 2,
        "title": "Recommendations",
        "content": "Implement controls."
      }}
    ]
    ```
    
    **Key Points:**
    - Each heading becomes its own block, regardless of level
    - Content NEVER includes headings - only text, lists, images, tables
    - This provides maximum granularity for frontend section-level styling

3.  **`DefinitionListComponent`**:
    *   This is a **specialized** tool.
    *   You MUST use this block **only** when you identify a section that is semantically a profile or a list of key-value definitions. A clear signal for this is a list of items where each item starts with a bolded term followed by a colon (e.g., "**Origin and Attribution**: ...").
    *   Extract the section title from the document. The title should be concise and factual - extract the actual section heading, not create an explanatory description. Avoid mentioning frameworks or standards in the title (e.g., use "Controls" not "Tactical Defense Recommendations (NIST CSF v2 Controls)").
    *   For `item_key_display_name`: Use a brief, general label for the key column header. Prefer concise names like "Ref", "ID", "Key", or "Field". Avoid overly specific names like "NIST CSF v2.0 Reference Id" - use "Ref" instead. Keep it reusable and general.
    *   For `item_value_display_name`: Use a brief, general label for the value column header. Default to "Description" or similar succinct terms like "Value" or "Details" that represent the content type. Avoid domain-specific or verbose names.
    *   Extract the list of key-value pairs into the `items` field.

4.  **`MitreAttackChainComponent`**:
    *   This is a **specialized** tool.
    *   You MUST use this block **only** for the section describing a numbered sequence of MITRE ATT&CK tactics.
    *   Extract the overall title for the chain from the document. The title should be concise and factual - extract the actual section heading (e.g., "Attack Chain"), not create an explanatory description like "Attack Chain Mapped to MITRE ATT&CK". Avoid mentioning frameworks or standards in the title.
    *   Process each step, capturing:
        - its date (if present)
        - its action; A description of the corresponding attack used by the threat actor in the story
        - its MITRE TACTIC; Tactic ID : Name of the tactic
        - its MITRE TECHNIQUE; Technique ID : Name of the technique
        - its full description

5.  **`SourcesComponent`**:
    *   This is a **specialized** tool.
    *   You MUST use this block **only** when you encounter a "Sources" section (or similar section title) containing numbered source citations in the format `[1] Title: URL`.
    *   Extract the section title from the document. The title should be concise and factual - typically "Sources" but extract the actual section heading if it differs.
    *   Parse each source entry from the markdown format:
        - Extract the citation number from the brackets (e.g., `[1]` → number: 1)
        - Extract the source title/name (the text before the colon, e.g., "The Hacker News")
        - Extract the URL (the text after the colon)

## Instructions:

1.  Read the entire input article to understand its structure.
2.  Start from the beginning and create the `MdxDocument` object, starting with the `document_title`.
3.  Process the article sequentially, chunking it into the appropriate block types.
4.  Use `SectionBlock` for ANY content with a heading. Use `MarkdownBlock` only for content without any headings (e.g., standalone paragraphs between specialized components).
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

