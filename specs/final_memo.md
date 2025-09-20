# Final Memo Agent

**Objective**: Come up with final investment memo based on the /outputs/<company-name>/ans-founders-checklist.md and all the agent analysis in /outputs/<company-name>/analysis/ based on the agent weights provided by the user

## Implementation Plan

1. Analyse the streamlit_app.py and understand the workflow. Once the ans-founders-checklist.md is created either by simulating founders answers or by user directly uploading the Q&A document, the UI should show one input box corresponding to each agent. The user should enter the values out of 100 and the sum of values of all the agents should be 100 as well

example

```
Agent A: __/100
Agnet B: __/100
Agent C: __/100
```

There should be proper checks as the sum of values for all agents should not exceed 100 in UI before submitting. You can auto fill for the last agent or something. So basically do every checks and make sure that the values are appropriate and only then these values are passed for processing.

2. Once you have the values, you have to pass these values with corresponsding agnet name and agent analysis from previous steps to the LLM.

The prompt parameter for passing the values and agent analysis content could look like:

```
{
    "agents": [
        {
            "agent_name": "Business Analysis Agent",
            "weight": 30,
            "analysis": "..."
        },
        {
            "agent_name": "Market Analysis Agent",
            "weight": 70,
            "analysis": "..."
        },
    ]
}
```

Another parameter that should be passed to the LLM prompt is the ans-founders-checklist.md. Write a prompt asking LLM to come up with a final investment memo based on the agent analysis and percentage of weightage it should give to that particular analysis. So for example, user has provided 60 to founder analysis agent, then the recommendation and investment memo should have 60% wieghtage to founder analysis.

3. The final investment memo should be stored in the /outputs/<company-name>/investment-memo.md. In addition to that, in the UI, the user should get option to download the pdf version of it.
