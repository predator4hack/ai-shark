"""
Example demonstrating the Streamlit UI components for the VC Document Analyzer.

This example shows how to use the UI components independently and demonstrates
the complete user interface workflow.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.ui.streamlit_interface import StreamlitInterface, ProgressTracker
from src.models.data_models import SlideAnalysis, SlideImage
import tempfile
import time


def create_sample_analysis_results():
    """Create sample analysis results for demonstration."""
    return [
        SlideAnalysis(
            slide_number=1,
            heading="Company Overview",
            image_descriptions=[
                "Company logo prominently displayed",
                "Team photo showing 5 founders"
            ],
            chart_table_data=[
                "Founded in 2023",
                "Based in San Francisco, CA"
            ],
            interpretation="This slide introduces the company and founding team, establishing credibility and providing basic company information.",
            confidence_score=0.92,
            processing_time=1.2,
            errors=[]
        ),
        SlideAnalysis(
            slide_number=2,
            heading="Market Opportunity",
            image_descriptions=[
                "Large market size chart showing $50B TAM",
                "Growth trend graph showing 25% CAGR"
            ],
            chart_table_data=[
                "Total Addressable Market: $50B",
                "Serviceable Addressable Market: $5B",
                "Market growth rate: 25% annually"
            ],
            interpretation="This slide demonstrates a large and growing market opportunity, which is crucial for VC investment consideration.",
            confidence_score=0.88,
            processing_time=1.5,
            errors=[]
        ),
        SlideAnalysis(
            slide_number=3,
            heading="Financial Projections",
            image_descriptions=[],
            chart_table_data=[],
            interpretation="",
            confidence_score=0.0,
            processing_time=0.8,
            errors=["Unable to extract chart data", "Image quality too low"]
        )
    ]


def demonstrate_ui_components():
    """Demonstrate the UI components functionality."""
    print("🚀 VC Document Analyzer - UI Components Demo")
    print("=" * 50)
    
    # Initialize UI
    ui = StreamlitInterface()
    print("✅ StreamlitInterface initialized")
    
    # Create sample data
    sample_results = create_sample_analysis_results()
    print(f"✅ Created {len(sample_results)} sample analysis results")
    
    # Demonstrate message methods
    print("\n📢 Message Display Methods:")
    print("- Error messages: ui.show_error('Error message')")
    print("- Success messages: ui.show_success('Success message')")
    print("- Info messages: ui.show_info('Info message')")
    print("- Warning messages: ui.show_warning('Warning message')")
    
    # Demonstrate progress tracking
    print("\n📊 Progress Tracking:")
    print("- ProgressTracker can be used to show processing progress")
    print("- Updates progress bar and status text")
    print("- Supports increment and complete methods")
    
    # Demonstrate file validation logic
    print("\n📁 File Validation:")
    print("- Validates file size (max 10MB)")
    print("- Checks supported formats (PDF, PPTX, PNG, JPG, JPEG)")
    print("- Displays file information (name, size, type)")
    
    # Demonstrate results processing
    print("\n📈 Results Processing:")
    successful_slides = len([r for r in sample_results if not r.errors])
    failed_slides = len(sample_results) - successful_slides
    avg_confidence = sum(r.confidence_score for r in sample_results) / len(sample_results)
    
    print(f"- Total slides: {len(sample_results)}")
    print(f"- Successful: {successful_slides}")
    print(f"- Failed: {failed_slides}")
    print(f"- Average confidence: {avg_confidence:.2f}")
    
    # Show sample slide analysis
    print("\n📋 Sample Slide Analysis:")
    for i, analysis in enumerate(sample_results[:2]):  # Show first 2 slides
        print(f"\nSlide {analysis.slide_number}: {analysis.heading}")
        print(f"  Visual Elements: {len(analysis.image_descriptions)} items")
        print(f"  Chart Data: {len(analysis.chart_table_data)} items")
        print(f"  Interpretation: {analysis.interpretation[:100]}...")
        print(f"  Confidence: {analysis.confidence_score:.2f}")
        print(f"  Processing Time: {analysis.processing_time:.1f}s")
        if analysis.errors:
            print(f"  Errors: {len(analysis.errors)} error(s)")
    
    print("\n✅ UI Components demonstration complete!")


def demonstrate_workflow():
    """Demonstrate the complete workflow."""
    print("\n🔄 Complete Workflow Demonstration")
    print("=" * 50)
    
    print("1. 📁 File Upload")
    print("   - User selects a pitch deck file")
    print("   - System validates file size and format")
    print("   - File information is displayed")
    
    print("\n2. 🔧 Processing Initialization")
    print("   - Document processor is initialized")
    print("   - Gemini analyzer is set up")
    print("   - Output manager is prepared")
    print("   - API connection is tested")
    
    print("\n3. 📊 Document Processing")
    print("   - Slides are extracted from document")
    print("   - Each slide is converted to image format")
    print("   - Progress is shown to user")
    
    print("\n4. 🤖 AI Analysis")
    print("   - Each slide image is sent to Gemini API")
    print("   - AI extracts heading, descriptions, data, interpretation")
    print("   - Results are structured and validated")
    print("   - Progress updates for each slide")
    
    print("\n5. 💾 Results Saving")
    print("   - Analysis results are formatted as Markdown")
    print("   - Output file is saved with timestamp")
    print("   - Processing statistics are included")
    
    print("\n6. 📊 Results Display")
    print("   - Summary metrics are shown")
    print("   - Download button for full analysis")
    print("   - Slide-by-slide results with filtering")
    print("   - Error handling and user feedback")
    
    print("\n7. 🔄 Reset Option")
    print("   - User can analyze another document")
    print("   - Session state is cleared")
    print("   - Interface returns to upload state")


def demonstrate_error_handling():
    """Demonstrate error handling capabilities."""
    print("\n⚠️ Error Handling Demonstration")
    print("=" * 50)
    
    print("File Upload Errors:")
    print("- File too large (>10MB)")
    print("- Unsupported format")
    print("- Corrupted file")
    
    print("\nProcessing Errors:")
    print("- Document parsing failures")
    print("- API connection issues")
    print("- Rate limiting")
    print("- Authentication failures")
    
    print("\nUser Feedback:")
    print("- Clear error messages")
    print("- Actionable guidance")
    print("- Graceful degradation")
    print("- Partial results when possible")
    
    # Show error example
    error_analysis = sample_results = create_sample_analysis_results()[2]  # The one with errors
    print(f"\nExample Error Analysis:")
    print(f"- Slide {error_analysis.slide_number}: {len(error_analysis.errors)} errors")
    for error in error_analysis.errors:
        print(f"  • {error}")


def main():
    """Main demonstration function."""
    try:
        demonstrate_ui_components()
        demonstrate_workflow()
        demonstrate_error_handling()
        
        print("\n🎉 All demonstrations completed successfully!")
        print("\nTo run the actual Streamlit app:")
        print("  streamlit run streamlit_app.py")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())