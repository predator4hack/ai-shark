"""
Public Data Extractors

This package contains all the specific data extractors that inherit from BaseExtractor.
Each extractor focuses on extracting a specific type of public data about companies.
"""

# Import all extractors here for easy discovery
from .products_services_extractor import ProductsServicesExtractor

# List of all available extractors for auto-discovery
AVAILABLE_EXTRACTORS = [
    ProductsServicesExtractor,
    # Future extractors will be added here:
    # NewsExtractor,
    # CompetitorExtractor, 
    # FounderExtractor,
]

__all__ = ['ProductsServicesExtractor', 'AVAILABLE_EXTRACTORS']