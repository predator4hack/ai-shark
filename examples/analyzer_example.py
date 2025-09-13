"""
Example usage of the IntelligentAnalyzer module

This script demonstrates various ways to use the IntelligentAnalyzer for 
prompt analysis with web scraping and Gemini LLM integration.
"""

import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from intelligent_analyzer import IntelligentAnalyzer, AnalysisResult


def example_basic_analysis():
    """Basic analysis example"""
    print("=" * 60)
    print("BASIC ANALYSIS EXAMPLE")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = IntelligentAnalyzer(
        max_search_results=5,
        timeout=30,
        enable_javascript=True
    )
    
    try:
        # Analyze a prompt
        prompt = "What are the latest trends in sustainable energy technology?"
        print(f"Analyzing: {prompt}")
        
        result = analyzer.analyze_prompt(
            prompt=prompt,
            enable_search=True,
            enable_scraping=True,
            use_selenium=False  # Use basic scraping for faster results
        )
        
        # Display results
        print(f"\nConfidence Score: {result.confidence_score:.2f}")
        print(f"Sources Found: {len(result.search_results)}")
        print(f"Processing Time: {result.metadata.get('processing_time', 0):.2f} seconds")
        
        print("\nGemini Analysis:")
        print("-" * 40)
        print(result.gemini_response[:500] + "..." if len(result.gemini_response) > 500 else result.gemini_response)
        
        if result.search_results:
            print("\nTop Sources:")
            print("-" * 40)
            for i, source in enumerate(result.search_results[:3], 1):
                print(f"{i}. {source.title}")
                print(f"   URL: {source.url}")
                if source.content:
                    print(f"   Content Preview: {source.content[:100]}...")
                print()
        
    finally:
        analyzer.cleanup()


def example_advanced_analysis():
    """Advanced analysis with Selenium"""
    print("=" * 60)
    print("ADVANCED ANALYSIS EXAMPLE (with Selenium)")
    print("=" * 60)
    
    analyzer = IntelligentAnalyzer(
        max_search_results=3,
        timeout=45,
        enable_javascript=True
    )
    
    try:
        # Analyze a prompt that might require JavaScript rendering
        prompt = "How do modern web applications handle real-time data updates?"
        print(f"Analyzing: {prompt}")
        
        result = analyzer.analyze_prompt(
            prompt=prompt,
            enable_search=True,
            enable_scraping=True,
            use_selenium=True  # Use Selenium for JavaScript-heavy sites
        )
        
        # Export results in different formats
        print(f"\nConfidence Score: {result.confidence_score:.2f}")
        
        # JSON export
        json_result = analyzer.export_result(result, 'json')
        print(f"\nJSON Export Preview:")
        print(json_result[:300] + "..." if len(json_result) > 300 else json_result)
        
        # Markdown export
        md_result = analyzer.export_result(result, 'markdown')
        print(f"\nMarkdown Export Preview:")
        print(md_result[:400] + "..." if len(md_result) > 400 else md_result)
        
    finally:
        analyzer.cleanup()


def example_custom_search():
    """Custom search and analysis"""
    print("=" * 60)
    print("CUSTOM SEARCH EXAMPLE")
    print("=" * 60)
    
    analyzer = IntelligentAnalyzer(max_search_results=7)
    
    try:
        # Perform custom search
        query = "machine learning deployment best practices 2024"
        print(f"Searching for: {query}")
        
        search_results = analyzer.google_search(query, num_results=5)
        print(f"Found {len(search_results)} search results")
        
        # Scrape specific URLs
        if search_results:
            urls = [result.url for result in search_results[:3]]
            print(f"Scraping {len(urls)} URLs...")
            
            scraped_content = analyzer.scrape_urls_parallel(urls, use_selenium=False)
            
            # Analyze with context
            gemini_response = analyzer.analyze_with_gemini(
                prompt="Summarize the best practices for machine learning deployment based on the provided sources",
                context_data=scraped_content
            )
            
            print("\nAnalysis Result:")
            print("-" * 40)
            print(gemini_response)
            
            # Show scraped content summary
            print(f"\nScraped Content Summary:")
            print("-" * 40)
            for i, content in enumerate(scraped_content, 1):
                print(f"{i}. URL: {content.get('url', 'Unknown')}")
                print(f"   Status: {'Success' if 'content' in content else 'Failed'}")
                if 'content' in content:
                    print(f"   Content Length: {len(content['content'])} chars")
                if 'error' in content:
                    print(f"   Error: {content['error']}")
                print()
        
    finally:
        analyzer.cleanup()


def example_context_manager():
    """Using analyzer as context manager"""
    print("=" * 60)
    print("CONTEXT MANAGER EXAMPLE")
    print("=" * 60)
    
    # Using with statement for automatic cleanup
    with IntelligentAnalyzer(max_search_results=3) as analyzer:
        prompt = "What are the security considerations for cloud-native applications?"
        print(f"Analyzing: {prompt}")
        
        result = analyzer.analyze_prompt(
            prompt=prompt,
            enable_search=True,
            enable_scraping=True
        )
        
        print(f"Analysis completed with confidence: {result.confidence_score:.2f}")
        print(f"Found {len(result.search_results)} sources")
        
        # Save results to file
        output_file = "analysis_result.md"
        md_content = analyzer.export_result(result, 'markdown')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"Results saved to: {output_file}")


def main():
    """Main function to run all examples"""
    print("IntelligentAnalyzer Examples")
    print("=" * 60)
    
    # Check if API key is set
    if not os.getenv('GEMINI_API_KEY'):
        print("ERROR: GEMINI_API_KEY environment variable not set!")
        print("Please set your Gemini API key before running examples.")
        return
    
    try:
        # Run examples
        example_basic_analysis()
        input("\nPress Enter to continue to advanced example...")
        
        example_advanced_analysis()
        input("\nPress Enter to continue to custom search example...")
        
        example_custom_search()
        input("\nPress Enter to continue to context manager example...")
        
        example_context_manager()
        
        print("\nAll examples completed successfully!")
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user.")
    except Exception as e:
        print(f"\nError running examples: {e}")


if __name__ == "__main__":
    main()