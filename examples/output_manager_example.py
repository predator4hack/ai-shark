#!/usr/bin/env python3
"""
Example usage of the OutputManager class.

This script demonstrates how to use the OutputManager to format and save
slide analysis results to structured Markdown files.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.output.output_manager import OutputManager
from src.models.data_models import SlideAnalysis


def create_sample_analyses():
    """Create sample slide analyses for demonstration."""
    
    # Sample slide 1 - Company overview
    slide1 = SlideAnalysis(
        slide_number=1,
        heading="Company Overview",
        image_descriptions=[
            "Company logo with modern design",
            "Team photo showing 5 founders",
            "Office location map"
        ],
        chart_table_data=[
            "Founded in 2020, 50 employees",
            "Headquarters in San Francisco"
        ],
        interpretation="This slide introduces TechCorp, a growing startup with a strong founding team and established presence in San Francisco. The company has scaled to 50 employees in just 4 years.",
        confidence_score=0.92,
        processing_time=2.1,
        errors=[]
    )
    
    # Sample slide 2 - Market analysis with some issues
    slide2 = SlideAnalysis(
        slide_number=2,
        heading="Market Analysis",
        image_descriptions=[
            "Market size chart (partially obscured)"
        ],
        chart_table_data=[
            "TAM: $50B (estimated)",
            "SAM: $5B",
            "Growth rate data unclear"
        ],
        interpretation="The slide presents market opportunity data, showing a large Total Addressable Market of $50B. However, some data points were difficult to extract due to image quality issues.",
        confidence_score=0.67,
        processing_time=3.5,
        errors=[
            "Chart partially obscured by watermark",
            "Growth rate numbers too small to read clearly"
        ]
    )
    
    # Sample slide 3 - Financial projections
    slide3 = SlideAnalysis(
        slide_number=3,
        heading="Financial Projections",
        image_descriptions=[
            "Revenue growth chart showing exponential curve",
            "Profit margin timeline"
        ],
        chart_table_data=[
            "2024 Revenue: $2M",
            "2025 Projected: $8M",
            "2026 Projected: $20M",
            "Break-even: Q3 2025"
        ],
        interpretation="Strong financial projections showing 4x revenue growth year-over-year. The company expects to reach break-even by Q3 2025, which is aggressive but achievable given the market opportunity.",
        confidence_score=0.88,
        processing_time=2.8,
        errors=[]
    )
    
    return [slide1, slide2, slide3]


def main():
    """Demonstrate OutputManager functionality."""
    
    print("🚀 OutputManager Example")
    print("=" * 50)
    
    # Create output manager
    output_manager = OutputManager(output_directory="example_outputs")
    print(f"📁 Output directory: {output_manager.output_directory}")
    
    # Create sample data
    analyses = create_sample_analyses()
    print(f"📊 Created {len(analyses)} sample slide analyses")
    
    # Add some processing statistics
    processing_stats = {
        "api_calls": 15,
        "total_tokens": 2500,
        "api_cost": 0.12,
        "processing_start": "2024-01-15T14:30:00",
        "processing_end": "2024-01-15T14:32:15"
    }
    
    # Save the analysis
    try:
        output_path = output_manager.save_analysis(
            results=analyses,
            original_filename="TechCorp_Pitch_Deck.pdf",
            processing_stats=processing_stats
        )
        
        print(f"✅ Analysis saved successfully!")
        print(f"📄 Output file: {output_path}")
        
        # Display some sample content
        print("\n📖 Sample content preview:")
        print("-" * 30)
        
        with open(output_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Show first 20 lines
            for i, line in enumerate(lines[:20]):
                print(f"{i+1:2d}: {line.rstrip()}")
            
            if len(lines) > 20:
                print(f"... ({len(lines) - 20} more lines)")
        
        # Show metadata example
        print(f"\n📈 Generated metadata:")
        metadata = output_manager.create_summary_metadata(
            analyses, "TechCorp_Pitch_Deck.pdf", processing_stats
        )
        
        for key, value in metadata.items():
            if key != 'processing_date':  # Skip the timestamp for cleaner output
                print(f"   {key}: {value}")
        
        # Demonstrate filename generation
        print(f"\n🏷️  Filename generation examples:")
        test_names = [
            "My Company Pitch.pdf",
            "startup<>deck:\"/\\|?*.pptx",
            "   ",
            "a" * 120 + ".pdf"
        ]
        
        for name in test_names:
            generated = output_manager.generate_filename(name)
            print(f"   '{name}' → '{generated}'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    print(f"\n🎉 Example completed successfully!")
    return 0


if __name__ == "__main__":
    exit(main())