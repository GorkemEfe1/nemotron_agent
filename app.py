import streamlit as st
from agent import run_agent_chain

# --- Streamlit UI Configuration ---

st.set_page_config(
    page_title="ClearQuery: Agents for Impact (Nemotron Dual-Agent)",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling (using simple markdown/HTML for Streamlit)
st.markdown(
    """
    <style>
    .reportview-container .main {
        padding-top: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 0.5rem;
        font-weight: bold;
        background-color: #2e7bff; /* NVIDIA-esque blue */
        color: white;
        padding: 0.75rem;
    }
    .stTextArea {
        border: 2px solid #ccc;
        border-radius: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("💡 ClearQuery: Jargon-to-Action Translator")
st.subheader("A Dual-Agent System for Social Impact, powered by NVIDIA Nemotron")

st.markdown("""
<p style='font-size: 1.1rem;'>
Paste any complex bureaucratic text below (e.g., legal document, government form, or medical bill). 
Our dual-agent system—Nemotron-Nano for analysis, Nemotron-Super for simplification—will turn the jargon 
into clear, actionable steps.
</p>
""", unsafe_allow_html=True)

# --- User Input ---

original_text = st.text_area(
    "1. Paste Your Confusing Text Here:", 
    height=300,
    placeholder="Example: 'Pursuant to Section 7.2 of the Residency Maintenance Addendum, failure by the tenant to remit the stipulated monthly premium by the tenth (10th) day of the calendar month shall constitute a material breach...'"
)

# --- Agent Execution ---

if st.button("2. 🤖 Run ClearQuery Agent Chain"):
    if not original_text:
        st.error("Please paste some text into the box to begin the analysis.")
    else:
        # Use a Streamlit spinner to show the user the agent is working
        with st.spinner("Analyzing text with Nemotron-Nano and simplifying with Nemotron-Super..."):
            try:
                # This calls the run_agent_chain function from agent.py
                simplified_output = run_agent_chain(original_text)
                
                # Check for the specific API key error message
                if "🛑 **SETUP ERROR:**" in simplified_output:
                    st.error(simplified_output)
                elif "API Key Error:" in simplified_output:
                    st.error(simplified_output)
                else:
                    st.success("Analysis Complete!")
                    st.markdown("---")
                    
                    # Display the final output from the Simplifier Agent
                    st.markdown(simplified_output)
                    
            except Exception as e:
                st.error(f"An unexpected error occurred during processing: {e}")

# --- Footer/Credits ---
st.markdown("---")
st.caption("🏆 Built for the Agents for Impact Hackathon using Nemotron-Nano-9B-v2 and Llama-3_3-Nemotron-Super-49B-v1_5")
