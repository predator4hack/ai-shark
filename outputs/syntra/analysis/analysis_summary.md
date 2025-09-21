# Multi-Agent Analysis Summary

**Generated:** 2025-09-21 01:15:08
**Analysis System:** AI-Shark Multi-Agent Pipeline
**Company Directory:** outputs/Syntra

## Analysis Overview

- **Total Agents Executed:** 2
- **Successful Analyses:** 0
- **Failed Analyses:** 2
- **Total Processing Time:** 0.00 seconds

## Agent Results

### ✅ Successful Analyses


### ❌ Failed Analyses

#### Business Analysis
- **Agent:** BusinessAnalysisAgent
- **Error:** Token limit exceeded. Try reducing document size or check max_tokens settings: 429 You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits.
* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 200
Please retry in 55.55580848s. [violations {
  quota_metric: "generativelanguage.googleapis.com/generate_content_free_tier_requests"
  quota_id: "GenerateRequestsPerDayPerProjectPerModel-FreeTier"
  quota_dimensions {
    key: "model"
    value: "gemini-2.0-flash"
  }
  quota_dimensions {
    key: "location"
    value: "global"
  }
  quota_value: 200
}
, links {
  description: "Learn more about Gemini API quotas"
  url: "https://ai.google.dev/gemini-api/docs/rate-limits"
}
, retry_delay {
  seconds: 55
}
]

#### Market Analysis
- **Agent:** MarketAnalysisAgent
- **Error:** Token limit exceeded. Try reducing document size or check max_tokens settings: 429 You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits.
* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 200
Please retry in 51.730096208s. [violations {
  quota_metric: "generativelanguage.googleapis.com/generate_content_free_tier_requests"
  quota_id: "GenerateRequestsPerDayPerProjectPerModel-FreeTier"
  quota_dimensions {
    key: "model"
    value: "gemini-2.0-flash"
  }
  quota_dimensions {
    key: "location"
    value: "global"
  }
  quota_value: 200
}
, links {
  description: "Learn more about Gemini API quotas"
  url: "https://ai.google.dev/gemini-api/docs/rate-limits"
}
, retry_delay {
  seconds: 51
}
]


## Analysis Files Generated


## Next Steps

The individual agent analysis reports are available in the analysis directory. Each report contains:
- Comprehensive analysis from the specific agent's perspective
- Sector-specific insights and recommendations
- Business intelligence generated using advanced AI models

For complete insights, please review all successful analysis reports.
