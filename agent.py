import os
import json
from dotenv import load_dotenv 
from openai import OpenAI # Using the official OpenAI client library

# Load environment variables from a .env file if it exists
load_dotenv() 

# --- NVIDIA API Endpoints (Refactored to OpenAI Client Style) ---

# The base URL for the NVIDIA Integration API
BASE_URL = "https://integrate.api.nvidia.com/v1"

# Nemotron-Nano model name (Analyzer)
# FIX: Using the exact, capitalized model name from the Model Card, without the 'nvidia/' prefix
NANO_MODEL = "nvidia/nvidia-nemotron-nano-9b-v2"

# Nemotron-Super model name (Simplifier)
# FIX: Applying the same capitalization and naming convention to the Super model
SUPER_MODEL = "nvidia/llama-3.3-nemotron-super-49b-v1.5"


def get_api_key():
    """
    Retrieves the NVIDIA API key from the environment variable.
    """
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        print("ERROR: NVIDIA_API_KEY environment variable not set.")
        return "MISSING_API_KEY" 
    return api_key


def call_nemotron(system_prompt, user_prompt, model_name, max_tokens=2048):
    """
    Reusable function to call a Nemotron model using the OpenAI client structure.
    """
    api_key = get_api_key()
    
    if api_key == "MISSING_API_KEY":
        return "API Key Error: Cannot proceed without API key."

    try:
        # Initialize the OpenAI client with the specific NVIDIA base URL and API key
        client = OpenAI(
            base_url=BASE_URL,
            api_key=api_key
        )
        
        # Use the standard chat completions endpoint
        completion = client.chat.completions.create(
            model=model_name, # Now using the corrected, capitalized model name
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=max_tokens,
            stream=False # Requesting non-streaming response for simplicity
        )

        # Extract the content from the response object
        if completion.choices and completion.choices[0].message.content:
            return completion.choices[0].message.content.strip()
        
        return "No content received from the model."

    except Exception as e:
        # Catch network or authentication errors
        print(f"API Call Error: {e}")
        return f"Final API Error: Failed to connect or receive a valid response. Check key and model name. Error: {e}"


# --- Agentic Workflow (The Core Logic) ---

def run_agent_chain(original_text):
    """
    Executes the two-step, multi-agent chain: Analyzer -> Simplifier.
    """
    
    # Check for API key early
    if get_api_key() == "MISSING_API_KEY":
        return "🛑 **SETUP ERROR:** The NVIDIA_API_KEY is not set. Please set it in your terminal or a `.env` file."

    # ----------------------------------------
    # AGENT 1: THE ANALYZER (Nemotron-Nano)
    # Goal: Extract structure and intent (fast and cheap)
    # ----------------------------------------
    
    # The Analyzer needs a JSON schema for reliable, structured output
    ANALYZER_SYSTEM_PROMPT = """
    You are an expert paralegal agent, specializing in identifying barriers to understanding in bureaucratic documents. 
    Your task is to analyze the user's input and extract key information into a structured JSON object. 
    Do not add any text outside the JSON block.
    
    JSON Schema MUST include:
    1. 'confusing_terms': [list of jargon or complex terms]
    2. 'key_entities': [list of relevant dates, amounts, or names]
    3. 'implicit_question': 'The single most likely question the user has (e.g., What is my deadline?)'
    
    Example Output:
    {'confusing_terms': ["Residency Maintenance Addendum", "non-renewal notice issuance"], 'key_entities': ["Section 7.2", "security deposit"], 'implicit_question': 'What are the rules for modifying the apartment?'}
    """
    
    print("--- 1. Calling Analyzer Agent (Nano) ---")
    analysis_json_str = call_nemotron(ANALYZER_SYSTEM_PROMPT, f"Analyze the following text: {original_text}", NANO_MODEL, max_tokens=1024)
    
    try:
        # Check if the response from the API call was an error message
        if analysis_json_str.startswith("Final API Error:") or analysis_json_str.startswith("API Key Error:"):
            return analysis_json_str
            
        # Attempt to clean up and parse the JSON response
        analysis_json_str = analysis_json_str.strip().replace("```json", "").replace("```", "")
        analysis_data = json.loads(analysis_json_str)
        
        # Format the analysis data for the next agent
        analysis_summary = (
            f"Jargon Identified: {', '.join(analysis_data.get('confusing_terms', ['None']))}\n"
            f"Key Data Points: {', '.join(analysis_data.get('key_entities', ['None']))}\n"
            f"User's Core Question: {analysis_data.get('implicit_question', 'The general meaning.')}"
        )
        print(f"Analysis complete: {analysis_summary}")
        
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error in Analyzer: {e}. Raw response: {analysis_json_str}")
        analysis_summary = f"Error in analysis. Please simplify the raw text: {analysis_json_str[:100]}..."
        
    
    # ----------------------------------------
    # AGENT 2: THE SIMPLIFIER (Nemotron-Super)
    # Goal: High-quality, empathetic text generation
    # ----------------------------------------
    
    SIMPLIFIER_SYSTEM_PROMPT = """
    You are an Agents for Impact agent named 'ClearQuery'. Your mission is to provide clear, actionable, and empathetic translations of complex, bureaucratic documents. 
    
    Your response MUST be structured as follows:
    
    ## 🎯 What This Means for You
    [One or two short paragraphs in simple, 5th-grade English. Focus on the core meaning and action required. Use kind, encouraging language.]
    
    ## ✅ Your Next Steps
    [A simple, numbered list of 2-3 actionable tasks.]
    
    Maintain a friendly, supportive tone throughout.
    """
    
    # The prompt for the Simplifier is a combination of the original text and the analysis
    simplifier_user_prompt = f"""
    Original Complex Text:
    ---
    {original_text}
    ---
    
    Agent 1 Analysis Summary:
    {analysis_summary}
    
    Now, rewrite and simplify this for a user who needs clear, actionable instructions.
    """
    
    print("--- 2. Calling Simplifier Agent (Super) ---")
    simplified_text = call_nemotron(SIMPLIFIER_SYSTEM_PROMPT, simplifier_user_prompt, SUPER_MODEL)
    
    print("--- Agent Chain Complete ---")
    return simplified_text

# Example of how this will be integrated into the Streamlit app later:
if __name__ == '__main__':
    test_input = """
    Pursuant to Section 7.2 of the Residency Maintenance Addendum, failure by the tenant 
    to remit the stipulated monthly premium by the tenth (10th) day of the calendar 
    month shall constitute a material breach, rendering the dwelling unit subject 
    to non-renewal notice issuance without prejudice to the security deposit.
    """
    
    # Remember to set your NVIDIA_API_KEY environment variable first!
    print(f"Original Text:\n{test_input}\n")
    result = run_agent_chain(test_input)
    print("\n--- FINAL CLEARQUERY OUTPUT ---\n")
    print(result)
