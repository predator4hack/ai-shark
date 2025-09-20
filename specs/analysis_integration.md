# Analysis Pipeline Integration

**Objective**: Analyse the demo_analysis_pipeline.py and streamlit_app.py and understand these pipeline. Integrate the existing demo analysis pipeline into the streamlit app data processing pipeline.

## Implementation Details

1. Analyse the streamlit_app.py application and understand the pitch deck and additional data processing pipeline. Currently, the user uploads the pitch deck and additional documents(Optional) and they are being processed and the output is stored in the /outputs/<company-name>/ directory.

In addition to that, there should be a python module comprising of various methods to avail publically available data. Once of them is in

Once the processing is done, there should be a UI button to initiate the analysis pipeline which would use the processed pitch deck, additional data, and public_data.md stored in /outpus/<company-name>/

1. Analyse the demo_analysis_pipeline.py and understand how the pipeline is working. The module currently accepts inputs from user about:
    - Weather to use LLM or use mock response
    - Which analysis agents to use

The task is to configure
