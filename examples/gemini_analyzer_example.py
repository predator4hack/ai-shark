#!/usr/bin/env python3
"""
Example script demonstrating the GeminiAnalyzer functionality.

This script shows how to use the GeminiAnalyzer to analyze slide images
and extract structured information using Google's Gemini Pro Vision API.
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analyzers.gemini_analyzer import GeminiAnalyzer
from models.data_models import SlideImage


def create_sample_slide() -> SlideImage:
    """Create a sample slide image for testing."""
    # Create a sample slide with some text and shapes
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fallback to basic if not available
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except (OSError, IOError):
        # Fallback to default font
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Add title
    draw.text((50, 50), "TechCorp - Market Analysis", fill='black', font=font_large)
    
    # Add some bullet points
    draw.text((50, 150), "• Total Addressable Market: $10B", fill='black', font=font_medium)
    draw.text((50, 190), "• Current Market Share: 5%", fill='black', font=font_medium)
    draw.text((50, 230), "• Projected Growth: 25% CAGR", fill='black', font=font_medium)
    
    # Add a simple chart representation
    draw.rectangle([50, 300, 400, 500], outline='black', width=2)
    draw.text((200, 280), "Revenue Growth Chart", fill='black', font=font_medium)
    
    # Draw simple bars
    draw.rectangle([80, 450, 120, 470], fill='blue')
    draw.text((85, 475), "2021", fill='black', font=font_small)
    
    draw.rectangle([150, 420, 190, 470], fill='blue')
    draw.text((155, 475), "2022", fill='black', font=font_small)
    
    draw.rectangle([220, 380, 260, 470], fill='blue')
    draw.text((225, 475), "2023", fill='black', font=font_small)
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return SlideImage(
        slide_number=1,
        image_data=img_bytes.getvalue(),
        image_format='PNG',
        original_size=(800, 600)
    )


def main():
    """Main function to demonstrate GeminiAnalyzer usage."""
    print("GeminiAnalyzer Example")
    print("=" * 50)
    
    # Check if API key is available
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ No GOOGLE_API_KEY environment variable found.")
        print("Please set your Google API key to run this example:")
        print("export GOOGLE_API_KEY='your-api-key-here'")
        return
    
    try:
        # Initialize the analyzer
        print("🔧 Initializing GeminiAnalyzer...")
        analyzer = GeminiAnalyzer(api_key=api_key)
        
        # Test connection
        print("🔗 Testing API connection...")
        if analyzer.test_connection():
            print("✅ API connection successful!")
        else:
            print("❌ API connection failed!")
            return
        
        # Create a sample slide
        print("🖼️  Creating sample slide...")
        sample_slide = create_sample_slide()
        print(f"   Created slide {sample_slide.slide_number} ({sample_slide.image_format}, {sample_slide.original_size})")
        
        # Analyze the slide
        print("🤖 Analyzing slide with Gemini...")
        analysis = analyzer.analyze_slide(sample_slide)
        
        # Display results
        print("\n📊 Analysis Results:")
        print("-" * 30)
        print(f"Slide Number: {analysis.slide_number}")
        print(f"Heading: {analysis.heading}")
        print(f"Processing Time: {analysis.processing_time:.2f} seconds")
        print(f"Confidence Score: {analysis.confidence_score}")
        
        if analysis.image_descriptions:
            print("\n🖼️  Image Descriptions:")
            for i, desc in enumerate(analysis.image_descriptions, 1):
                print(f"  {i}. {desc}")
        
        if analysis.chart_table_data:
            print("\n📈 Chart/Table Data:")
            for i, data in enumerate(analysis.chart_table_data, 1):
                print(f"  {i}. {data}")
        
        if analysis.interpretation:
            print(f"\n💡 Interpretation:")
            print(f"   {analysis.interpretation}")
        
        if analysis.errors:
            print(f"\n⚠️  Errors:")
            for error in analysis.errors:
                print(f"   - {error}")
        
        print(f"\n✅ Analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return


if __name__ == "__main__":
    main()