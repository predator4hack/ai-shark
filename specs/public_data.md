# Public Data Pipeline

**Objective**: Extract publically available information about the company and store it in /outputs/<company-name>/public_data.md

## Implementation Details

Analyse the streamlit_app.py and understand the flow of data processing pipeline. The way it works is when a user uploads pitch deck and additional information, the data processing pipeline runs and stores the extracted information in /outputs/<company-name>/. Now, once the files are stored, you have to integrate another pipeline that would extract information from the web.

The web data extraction may include(and more may come) extration about:
_ Prods and services
_ News and social media
_ Competitors
_ Founders Information

All these services are yet to be built, your task is to implement one of the services called prods and services and integrate in the existing data extraction pipeline.

### Prods And Services:

This would be a very simple Gemini LLM with search tool added, and in the prompt, pass the startup_name and website in the prvious step. The llm would do indepth analysis of the website and understand the products and services and mention it in the public_data.md file

There will be more public data extraction services so keep the code extensible. All these services would run and append the information in public_data.md

Clarifying Questions:

1. Integration Point: Should this new pipeline run automatically after
   the existing data extraction completes, or should it be triggered
   manually/separately?
   Run automatically after the data extraction completes

2. Gemini API: Do you have Gemini API credentials already set up in
   the project, or should I help configure that as well?
   Already set up

3. Search Tool: For the "search tool" with Gemini - are you referring
   to:

-   Google Search API integration?
-   Or Gemini's built-in search functionality?
    I saw a snippet of gemini model using URL context, I guess this would help in our usecase if we pass the website. Feel free to correct me if I am wrong. We can use gemini grounding with search as well

```
model = "gemini-2.5-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""INSERT_INPUT_HERE"""),
            ],
        ),
    ]
    tools = [
        types.Tool(url_context=types.UrlContext()),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config = types.ThinkingConfig(
            thinking_budget=-1,
        ),
        tools=tools,
    )

```

4. Input Data: The pipeline should use startup_name and website from
   the previous extraction step - are these stored in a specific file
   format in /outputs/<company-name>/?
   **Answer**: Yes, it can be retrieved from /outputs/<company-name>/metadata.json.

5. Output Format: For the public_data.md file, do you have a preferred
   structure/template, or should I design a clean markdown format?
   **Answer**: No structured template, whatever comes out of LLM, store it in markdown format

6. Extensibility: For future services (News, Competitors, Founders),
   should I create a base class/interface pattern, or a plugin-style
   architecture?
   **Answer**: Yes, create a plugin-style architecture

---

## Detailed Implementation Plan

### Overview
Based on the analysis of the existing codebase, this plan outlines the implementation of an extensible public data extraction pipeline that will automatically run after the pitch deck processing is complete.

### Current System Analysis

**Existing Pipeline Flow:**
1. User uploads pitch deck via `src/ui/streamlit_app.py`
2. `PitchDeckProcessor` processes the file and extracts metadata
3. Company folder created under `outputs/<company-name>/`
4. Files generated: `metadata.json`, `pitch_deck.md`, `table_of_contents.json`

**Key Infrastructure Available:**
- Gemini API configured via `src/utils/llm_manager.py`
- Output management system via `src/utils/output_manager.py`
- Prompt management system via `src/utils/prompt_manager.py`
- Extensible processor pattern with `BaseProcessor` class

### Architecture Design

#### 1. Public Data Extraction System Structure

```
src/
├── public_data/
│   ├── __init__.py
│   ├── base_extractor.py           # Abstract base class for all extractors
│   ├── orchestrator.py             # Coordinates all extraction services
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── products_services_extractor.py
│   │   ├── news_extractor.py       # Future: News and social media
│   │   ├── competitor_extractor.py # Future: Competitor analysis
│   │   └── founder_extractor.py    # Future: Founder information
│   └── utils/
│       ├── __init__.py
│       ├── web_fetcher.py          # Web content utilities using Gemini URL context
│       └── content_analyzer.py     # Content analysis utilities
```

#### 2. Integration Points

**Pipeline Integration:**
- Hook into `PitchDeckProcessor.process()` completion
- Trigger public data extraction automatically
- Append results to existing company directory

**Data Flow:**
```
PitchDeckProcessor.process() 
→ Extract metadata (company_name, website) saved to metadata.json
→ PublicDataOrchestrator.extract_all()
→ ProductsServicesExtractor.extract()
→ Use Gemini with URL context tools
→ Save results to public_data.md
```

### Detailed Component Specifications

#### 1. Base Extractor Class (`base_extractor.py`)

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseExtractor(ABC):
    """Abstract base class for all public data extractors using plugin-style architecture"""
    
    @abstractmethod
    def extract(self, company_name: str, website: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract public data for the company"""
        pass
    
    @abstractmethod
    def get_extractor_name(self) -> str:
        """Return the name of this extractor"""
        pass
    
    @abstractmethod
    def get_section_title(self) -> str:
        """Return the markdown section title for this extractor"""
        pass
    
    def should_extract(self, metadata: Dict[str, Any]) -> bool:
        """Determine if this extractor should run for the given company"""
        return True
    
    def is_enabled(self) -> bool:
        """Check if this extractor is enabled in configuration"""
        return True
```

#### 2. Orchestrator (`orchestrator.py`)

```python
class PublicDataOrchestrator:
    """Coordinates all public data extraction services using plugin architecture"""
    
    def __init__(self):
        self.extractors = self._discover_extractors()
    
    def _discover_extractors(self) -> List[BaseExtractor]:
        """Automatically discover available extractors"""
        extractors = []
        # Import and instantiate all available extractors
        from src.public_data.extractors.products_services_extractor import ProductsServicesExtractor
        extractors.append(ProductsServicesExtractor())
        return extractors
    
    def extract_all(self, company_name: str, company_dir: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Run all enabled extractors and aggregate results"""
        results = {}
        public_data_content = f"# Public Data Analysis for {company_name}\n\n"
        public_data_content += f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        
        for extractor in self.extractors:
            if extractor.is_enabled() and extractor.should_extract(metadata):
                try:
                    logger.info(f"Running {extractor.get_extractor_name()} for {company_name}")
                    extraction_result = extractor.extract(company_name, metadata.get('website', ''), metadata)
                    
                    if extraction_result.get('status') == 'success':
                        # Append to public data markdown
                        section_title = extractor.get_section_title()
                        section_content = extraction_result.get('content', '')
                        public_data_content += f"## {section_title}\n\n{section_content}\n\n"
                        
                        results[extractor.get_extractor_name()] = extraction_result
                    else:
                        logger.warning(f"Extraction failed for {extractor.get_extractor_name()}: {extraction_result.get('error')}")
                        results[extractor.get_extractor_name()] = extraction_result
                        
                except Exception as e:
                    logger.error(f"Error running {extractor.get_extractor_name()}: {e}")
                    results[extractor.get_extractor_name()] = {'status': 'error', 'error': str(e)}
        
        # Save aggregated public data
        public_data_path = os.path.join(company_dir, 'public_data.md')
        with open(public_data_path, 'w', encoding='utf-8') as f:
            f.write(public_data_content)
        
        return {
            'status': 'success',
            'extractors_run': len([r for r in results.values() if r.get('status') == 'success']),
            'total_extractors': len(self.extractors),
            'results': results,
            'output_file': public_data_path
        }
```

#### 3. Products & Services Extractor (`products_services_extractor.py`)

```python
import google.generativeai as genai
from src.public_data.base_extractor import BaseExtractor

class ProductsServicesExtractor(BaseExtractor):
    """Extracts products and services information using Gemini with URL context"""
    
    def __init__(self):
        self.model_name = "gemini-2.5-flash"
    
    def get_extractor_name(self) -> str:
        return "products_services"
    
    def get_section_title(self) -> str:
        return "Products and Services Analysis"
    
    def extract(self, company_name: str, website: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract products and services using Gemini with URL context tools"""
        
        if not website:
            return {
                'status': 'skipped',
                'reason': 'No website provided in metadata',
                'content': '*Website not available for analysis*'
            }
        
        try:
            # Use Gemini with URL context as specified in requirements
            import google.ai.generativelanguage as glm
            
            prompt = f"""
            Analyze the website for {company_name} ({website}) and provide a comprehensive analysis of their products and services.
            
            Please extract and organize the following information:
            
            1. **Core Products/Services**: What are the main products or services offered?
            2. **Key Features**: What are the most important features or capabilities?
            3. **Target Market**: Who is the primary target audience?
            4. **Value Proposition**: What makes their offering unique or valuable?
            5. **Pricing Information**: Any pricing details if available
            6. **Technology/Platform**: What technologies or platforms do they use?
            7. **Business Model**: How do they generate revenue?
            
            Format your response in clear markdown. Be specific and factual, only including information that can be found on their website.
            """
            
            contents = [
                glm.Content(
                    role="user",
                    parts=[
                        glm.Part(text=prompt),
                    ],
                ),
            ]
            
            tools = [
                glm.Tool(url_context=glm.UrlContext()),
            ]
            
            generate_content_config = glm.GenerateContentConfig(
                thinking_config=glm.ThinkingConfig(thinking_budget=-1),
                tools=tools,
            )
            
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(
                contents=contents,
                config=generate_content_config
            )
            
            return {
                'status': 'success',
                'content': response.text,
                'website_analyzed': website
            }
            
        except Exception as e:
            logger.error(f"Error extracting products/services for {company_name}: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'content': f'*Error analyzing website: {str(e)}*'
            }
    
    def should_extract(self, metadata: Dict[str, Any]) -> bool:
        """Only extract if website is available"""
        return bool(metadata.get('website'))
```

#### 4. Web Content Utilities (`utils/web_fetcher.py`)

```python
class WebContentAnalyzer:
    """Utilities for web content analysis using Gemini URL context"""
    
    @staticmethod
    def is_website_accessible(url: str) -> bool:
        """Quick check if website is accessible"""
        try:
            import requests
            response = requests.head(url, timeout=10, allow_redirects=True)
            return response.status_code < 400
        except:
            return False
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize URL format for Gemini URL context"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url.rstrip('/')
```

### Integration with Existing System

#### 1. Modify PitchDeckProcessor

Add hook to trigger public data extraction after successful processing:

```python
# In src/processors/pitch_deck_processor.py

def process(self, file_path: str, output_dir: str = "outputs") -> Dict[str, Any]:
    # ... existing processing logic ...
    
    if result['status'] == 'success' and metadata:
        # Trigger public data extraction
        try:
            from src.public_data.orchestrator import PublicDataOrchestrator
            logger.info(f"Starting public data extraction for {result['company_name']}")
            
            orchestrator = PublicDataOrchestrator()
            public_data_result = orchestrator.extract_all(
                company_name=result['company_name'],
                company_dir=result['output_dir'],
                metadata=metadata
            )
            
            result['public_data_extraction'] = public_data_result
            logger.info(f"Public data extraction completed for {result['company_name']}")
            
        except Exception as e:
            logger.warning(f"Public data extraction failed for {result['company_name']}: {e}")
            result['public_data_extraction'] = {
                'status': 'failed', 
                'error': str(e),
                'extractors_run': 0,
                'total_extractors': 0
            }
    
    return result
```

#### 2. Configuration System

Add to `config/settings.py`:

```python
# Public Data Extraction Configuration
PUBLIC_DATA_ENABLED: bool = bool(os.getenv("PUBLIC_DATA_ENABLED", "true").lower() == "true")
PUBLIC_DATA_EXTRACTORS: List[str] = os.getenv("PUBLIC_DATA_EXTRACTORS", "products_services").split(",")
PUBLIC_DATA_TIMEOUT: int = int(os.getenv("PUBLIC_DATA_TIMEOUT", "60"))
PUBLIC_DATA_RETRY_ATTEMPTS: int = int(os.getenv("PUBLIC_DATA_RETRY_ATTEMPTS", "2"))
```

### Implementation Steps

#### Phase 1: Core Implementation (Steps 1-3)
1. **Create base infrastructure**
   - Create `src/public_data/` directory structure
   - Implement `BaseExtractor` abstract class
   - Create basic `PublicDataOrchestrator`

2. **Implement Products & Services Extractor**
   - Create `ProductsServicesExtractor` using Gemini URL context
   - Test URL context functionality with sample websites
   - Add error handling for inaccessible websites

3. **Integrate with pipeline**
   - Modify `PitchDeckProcessor` to trigger public data extraction
   - Test end-to-end flow with sample data

#### Phase 2: Enhancement (Steps 4-6)
4. **Add web utilities**
   - Implement `WebContentAnalyzer` helper class
   - Add URL normalization and accessibility checking
   - Test with various website formats

5. **Improve error handling**
   - Add comprehensive error handling for network issues
   - Implement graceful degradation for missing websites
   - Add proper logging and user feedback

6. **Testing and validation**
   - Create unit tests for each component
   - Test with real company websites
   - Validate extraction quality and accuracy

#### Phase 3: Future Extensibility (Steps 7-9)
7. **Plugin architecture finalization**
   - Finalize extractor discovery mechanism
   - Create configuration system for enabling/disabling extractors
   - Document plugin development guidelines

8. **Performance optimization**
   - Add timeout controls for web requests
   - Implement async processing if needed
   - Optimize Gemini API usage

9. **Documentation and maintenance**
   - Create comprehensive documentation
   - Add troubleshooting guide
   - Set up monitoring and alerting

### File Structure After Implementation

```
src/
├── public_data/
│   ├── __init__.py
│   ├── base_extractor.py
│   ├── orchestrator.py
│   ├── extractors/
│   │   ├── __init__.py
│   │   └── products_services_extractor.py
│   └── utils/
│       ├── __init__.py
│       └── web_fetcher.py
└── processors/
    └── pitch_deck_processor.py (modified)

outputs/
└── {company-name}/
    ├── metadata.json
    ├── pitch_deck.md
    ├── table_of_contents.json
    └── public_data.md (new)
```

### Expected Output Format

The `public_data.md` file will contain:

```markdown
# Public Data Analysis for Company Name

*Last updated: 2024-01-15 14:30:22*

## Products and Services Analysis

### Core Products/Services
[LLM-generated analysis of main offerings]

### Key Features
[Important features and capabilities]

### Target Market
[Primary audience identification]

### Value Proposition
[Unique selling points]

### Pricing Information
[Pricing strategy if available]

### Technology/Platform
[Technology stack mentioned]

### Business Model
[Revenue generation approach]

[Additional sections will be added here as more extractors are implemented]
```

### Success Criteria

1. **Functional Success**
   - Public data extraction triggers automatically after pitch deck processing
   - Products & services information is accurately extracted using Gemini URL context
   - Results are saved in proper markdown format
   - System handles missing websites gracefully

2. **Quality Metrics**
   - Extracted information is relevant and factual
   - Extraction completes within 60 seconds
   - System handles 95% of common website formats

3. **Extensibility Success**
   - Plugin architecture allows easy addition of new extractors
   - Configuration system provides control over enabled extractors
   - Clear interface documentation for future development

This implementation plan provides a complete, step-by-step approach to building the public data extraction pipeline with proper integration into the existing system and extensibility for future enhancements.
