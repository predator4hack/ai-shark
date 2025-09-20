# Founder Simulation Agent

**Objective**: Build an fonder simulation agent that answers the questionnaire document based on the reference documents uploaded

## Implementation Details

Prerequeisite: The questionnaire document is ready from the previous pipeline.

1. UI: Two uplaod sections pop ups:
   a. The first upload section allows the user to upload real Q&A document where each of the questions are answered by the founder.
   b. The second upload section is to allow user to upload reference documents(founders-checklist, draft investment memo etc.) mentioning that this will simulate the Question answering using an agent

2. If the user selects the second option, and uplaods the document(pdf or docx), the content should be extracted and stored in /outputs/<company-name>/ref-data/ in markdown format. Company name you can extract from the previous workflows. If only it's feasible, try to reuse the exising extractin pipelines.

3. Once the files are extracted, create an agent that would ingest all the documents in the ref-data and pass it to LLM, along with /outputs/<company-name>/founders-checklist.md. The LLM should answer all the questions in the founders-checklist based on all the documents in the ref-data and output a file /outputs/<company-name>/ans-founders-checklist.md
