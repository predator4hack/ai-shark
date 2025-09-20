## Task: Questionnaire Agent

**Objective:** Generate structured questions by the investor to the founders clarifying the gaps from various reports provided. This questinnaire document should contain all the question that isn't present or cross-question the fesability or other aspects or need more information from the founders to make a sound investment descision.

**Implementation Details**

1. Analyse the questionnaire_agent.py file, questionnaire pipeline associated with it.
2. Instead of taking investment memo(/results/analysis_results.md), the questionnaire agent should intake all the reports from various analysis agents stored in /outputs
3. Based on the reports ingested, the agent should understand the business and clarify all the questions an investor would ask to the founding team to make a sound investment descision.
4. The output should be saved as /outputs/<company-name>/founders-checklist.md.

You may need to modify the existing pipeline and prompt in questionnaire_agent.py file.

Also I am planning to remove the questionnaire_agent.py file so don't keep any dependency on it. Create new python modules and put it in appropriate directory.

Sample Questions that can be in founder-checklit(not exhaustive list):

```
Revenue Streams
    ● Clearly define all sources of revenue. For each stream, include:
        ○ Name of the Revenue Stream: (e.g., Subscription Fees, Commission, Product Sales).
    ○ Description:
        ■ What is it?
        ■ How does it work?
    ○ Target Audience: Who is paying?
    ○ Percentage Contribution: Share of total revenue (if available).

Pricing Strategy – Separate sheet attached
    ● Rationale behind pricing – Straight feature pricing, considering our costs and margins, future expansion costs, enterprise ROIs, existing competitors pricing, and discounts

Unit Economics:
    - Customer Acquision Cost (CAC)
    - Lifetime Value (LTV)
    - LTV

Recurring vs. One-Time Revenue
Segregate revenue into:
    - Recurring Revenue
    - One-Time Revenue

Payment Flow and Terms
    - How payments are collected and processed.

Scalability of Revenue Model

Competitor Analysis Framework
(cover 2-3 competitors operating in the similar revenue model or advanced revenue model in
comparison to your company)


Founders Profile of all the founders

Financials:
    - MRR
    - ARR
    - Burn
    - Runway
    - Gross Margin

Facilities:


Technology:
● Write up on Tech stack –

Fundraiser:

Valuation:

Round structure:

Following the above information, we request you to provide a detailed business note for reference
in the format below:
● Key Problems Solved –
● Business Model –

Pipeline:

Why now?:

Financials:

Risk And Mitigation:
```
