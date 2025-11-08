"""BLUF writer implementation for generating executive summaries from MDX reports."""

import json
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from open_deep_research.configuration import Configuration
from open_deep_research.prompts import bluf_writer_base_prompt
from open_deep_research.schemas import BlufDocument
from open_deep_research.state import AgentState
from open_deep_research.utils import get_api_key_for_model

# Initialize a configurable model for BLUF writing
configurable_model = init_chat_model(
    configurable_fields=("model", "max_tokens", "api_key"),
)


async def bluf_writer(state: AgentState, config: RunnableConfig):
    """Generate BLUF (Bottom Line Up Front) executive summary from MDX-structured report.
    
    This function takes the MDX-structured JSON report and generates a concise executive
    summary with four key blocks: bottom line, actions, implications, and forward-looking indicators.
    
    Args:
        state: Agent state containing the MDX-structured JSON report
        config: Runtime configuration with model settings
        
    Returns:
        Dictionary containing the BLUF report as a JSON-serializable dict
    """
    # Step 1: Extract MDX report from state
    json_report = state.get("json_report", {})
    
    if not json_report:
        # If no MDX report exists, return error
        return {"bluf_report": {"error": "No MDX report found in state"}}
    
    # Step 2: Configure the BLUF writer model
    configurable = Configuration.from_runnable_config(config)
    bluf_model_config = {
        "model": configurable.final_report_model,  # Use same model as MDX writer
        "max_tokens": configurable.final_report_model_max_tokens,
        "api_key": get_api_key_for_model(configurable.final_report_model, config),
        "tags": ["langsmith:nostream"]
    }
    
    # Configure model with structured output and retry logic
    bluf_model = (
        configurable_model
        .with_structured_output(BlufDocument)
        .with_retry(stop_after_attempt=configurable.max_structured_output_retries)
        .with_config(bluf_model_config)
    )
    
    # Step 3: Format the prompt with MDX JSON input
    # Convert dict to JSON string for the prompt
    mdx_json_str = json.dumps(json_report, indent=2)
    prompt_content = bluf_writer_base_prompt.format(mdx_json=mdx_json_str)
    
    # Step 4: Generate BLUF report with error handling
    try:
        response = await bluf_model.ainvoke([HumanMessage(content=prompt_content)])
        # Convert Pydantic model to dict for state serialization
        bluf_json = response.model_dump() if hasattr(response, 'model_dump') else response.dict()
    except Exception as e:
        # In case of failure, return error in structured format
        bluf_json = {"error": f"Failed to generate BLUF report: {str(e)}"}
    
    # Step 5: Return the BLUF report to update state
    return {"bluf_report": bluf_json}
