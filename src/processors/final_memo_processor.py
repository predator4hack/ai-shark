"""
Final Memo Processor for AI-Shark Multi-Agent System

Handles business logic for final investment memo generation including
file discovery, content loading, and memo processing.
"""

import os
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from src.agents.final_memo_agent import FinalMemoAgent, create_final_memo_agent
from src.models.final_memo_models import (
    FinalMemoRequest, FinalMemoResult, FinalMemoConfig, 
    AgentAnalysisDiscovery, AgentWeight
)
from src.utils.output_manager import OutputManager
from src.utils.pdf_generator import convert_markdown_to_pdf, is_pdf_generation_available

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class FinalMemoProcessor:
    """
    Handles final memo generation business logic and file operations
    """
    
    def __init__(self, config: Optional[FinalMemoConfig] = None):
        """
        Initialize the Final Memo Processor
        
        Args:
            config: Optional configuration for memo generation
        """
        self.config = config or FinalMemoConfig()
        self.agent = create_final_memo_agent(self.config)
        logger.info("Initialized FinalMemoProcessor")
    
    def discover_analysis_files(self, company_dir: str) -> List[AgentAnalysisDiscovery]:
        """
        Dynamically discover analysis files in the analysis directory
        
        Args:
            company_dir: Path to the company's output directory
            
        Returns:
            List of discovered analysis files with metadata
        """
        try:
            company_path = Path(company_dir)
            analysis_dir = company_path / "analysis"
            
            if not analysis_dir.exists():
                logger.warning(f"Analysis directory not found: {analysis_dir}")
                return []
            
            discovered_files = []
            
            # Look for markdown files in analysis directory
            for file_path in analysis_dir.glob("*.md"):
                if file_path.name == "analysis_summary.md":
                    continue  # Skip summary file
                
                try:
                    # Extract agent name from filename
                    agent_name = self._format_agent_name(file_path.stem)
                    
                    # Get file metadata
                    stat = file_path.stat()
                    
                    # Read preview of content
                    content_preview = self._get_content_preview(file_path)
                    
                    discovery = AgentAnalysisDiscovery(
                        agent_name=agent_name,
                        file_name=file_path.name,
                        file_path=str(file_path),
                        content_preview=content_preview,
                        file_size=stat.st_size,
                        last_modified=datetime.fromtimestamp(stat.st_mtime),
                        available=True
                    )
                    
                    discovered_files.append(discovery)
                    logger.debug(f"Discovered analysis file: {agent_name} ({file_path.name})")
                    
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
                    # Add as unavailable file
                    discovery = AgentAnalysisDiscovery(
                        agent_name=self._format_agent_name(file_path.stem),
                        file_name=file_path.name,
                        file_path=str(file_path),
                        content_preview="Error reading file",
                        available=False
                    )
                    discovered_files.append(discovery)
            
            logger.info(f"Discovered {len(discovered_files)} analysis files in {analysis_dir}")
            return discovered_files
            
        except Exception as e:
            logger.error(f"Error discovering analysis files: {e}")
            return []
    
    def _format_agent_name(self, file_stem: str) -> str:
        """
        Format agent name from file stem for display
        
        Args:
            file_stem: File name without extension (e.g., "business_analysis")
            
        Returns:
            Formatted agent name (e.g., "Business Analysis")
        """
        # Replace underscores with spaces and title case
        formatted = file_stem.replace("_", " ").title()
        
        # Handle the "Analysis" word specifically to maintain proper formatting
        if formatted.endswith(" Analysis"):
            return formatted
        elif " Analysis " in formatted:
            return formatted
        else:
            # If it doesn't contain "Analysis", keep as is
            return formatted
    
    def _get_content_preview(self, file_path: Path, max_chars: int = 200) -> str:
        """
        Get a preview of file content
        
        Args:
            file_path: Path to the file
            max_chars: Maximum characters to include in preview
            
        Returns:
            Content preview string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(max_chars)
                if len(content) == max_chars:
                    content += "..."
                return content.strip()
        except Exception as e:
            logger.error(f"Error reading preview from {file_path}: {e}")
            return "Error reading file content"
    
    def load_analysis_content(self, analysis_dir: str) -> Dict[str, str]:
        """
        Load content from all analysis files
        
        Args:
            analysis_dir: Path to analysis directory
            
        Returns:
            Dictionary mapping agent names to their analysis content
        """
        analysis_content = {}
        analysis_path = Path(analysis_dir)
        
        if not analysis_path.exists():
            logger.warning(f"Analysis directory not found: {analysis_path}")
            return analysis_content
        
        try:
            for file_path in analysis_path.glob("*.md"):
                if file_path.name == "analysis_summary.md":
                    continue  # Skip summary file
                
                try:
                    agent_name = self._format_agent_name(file_path.stem)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    analysis_content[agent_name] = content
                    logger.debug(f"Loaded analysis content for {agent_name}: {len(content)} chars")
                    
                except Exception as e:
                    logger.error(f"Error loading content from {file_path}: {e}")
                    agent_name = self._format_agent_name(file_path.stem)
                    analysis_content[agent_name] = "No data available - error reading file"
            
            logger.info(f"Loaded content for {len(analysis_content)} agents")
            return analysis_content
            
        except Exception as e:
            logger.error(f"Error loading analysis content: {e}")
            return analysis_content
    
    def load_founders_checklist(self, company_dir: str) -> Optional[str]:
        """
        Load content from ans-founders-checklist.md
        
        Args:
            company_dir: Path to company directory
            
        Returns:
            Founders checklist content or None if not found
        """
        try:
            company_path = Path(company_dir)
            checklist_file = company_path / "ans-founders-checklist.md"
            
            if not checklist_file.exists():
                logger.error(f"Founders checklist not found: {checklist_file}")
                return None
            
            with open(checklist_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"Loaded founders checklist: {len(content)} characters")
            return content
            
        except Exception as e:
            logger.error(f"Error loading founders checklist: {e}")
            return None
    
    def create_memo_request(self, 
                          company_dir: str, 
                          agent_weights: Dict[str, int]) -> Optional[FinalMemoRequest]:
        """
        Create a FinalMemoRequest from company directory and agent weights
        
        Args:
            company_dir: Path to company directory
            agent_weights: Dictionary mapping agent names to weights
            
        Returns:
            Validated FinalMemoRequest or None if creation fails
        """
        try:
            # Load founders checklist
            founders_content = self.load_founders_checklist(company_dir)
            if not founders_content:
                raise ValueError("ans-founders-checklist.md not found or empty")
            
            # Load analysis content
            analysis_dir = str(Path(company_dir) / "analysis")
            analysis_content = self.load_analysis_content(analysis_dir)
            
            # Create agent weight objects
            agents = []
            for agent_name, weight in agent_weights.items():
                content = analysis_content.get(agent_name, "No data available")
                agent_weight = AgentWeight(
                    agent_name=agent_name,
                    weight=weight,
                    analysis=content
                )
                agents.append(agent_weight)
            
            # Extract company name from directory path
            company_name = Path(company_dir).name
            
            # Create and validate request
            request = FinalMemoRequest(
                agents=agents,
                founders_checklist_content=founders_content,
                company_name=company_name,
                company_dir=company_dir
            )
            
            logger.info(f"Created memo request for {company_name} with {len(agents)} agents")
            return request
            
        except Exception as e:
            logger.error(f"Error creating memo request: {e}")
            return None
    
    def generate_memo(self, company_dir: str, agent_weights: Dict[str, int]) -> FinalMemoResult:
        """
        Main method to generate final investment memo
        
        Args:
            company_dir: Path to company directory
            agent_weights: Dictionary mapping agent names to weights (must sum to 100)
            
        Returns:
            FinalMemoResult with success/failure information
        """
        try:
            logger.info(f"Starting memo generation for {company_dir}")
            
            # Create memo request
            request = self.create_memo_request(company_dir, agent_weights)
            if not request:
                return FinalMemoResult(
                    success=False,
                    error_message="Failed to create memo request. Check that ans-founders-checklist.md exists and analysis files are available."
                )
            
            # Generate memo using agent
            result = self.agent.generate_final_memo(request)
            
            if result.success:
                # Save memo to file
                output_file = self._save_memo_file(result.memo_content, company_dir, request.company_name)
                result.output_file = output_file
                
                # Generate PDF version if possible
                pdf_file = self._generate_pdf_version(result.memo_content, company_dir, request.company_name)
                if pdf_file:
                    result.pdf_file = pdf_file
                
                logger.info(f"Successfully generated memo: {output_file}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error generating memo: {str(e)}"
            logger.error(error_msg)
            
            return FinalMemoResult(
                success=False,
                error_message=error_msg,
                processing_time=0.0
            )
    
    def _save_memo_file(self, memo_content: str, company_dir: str, company_name: str) -> str:
        """
        Save memo content to markdown file
        
        Args:
            memo_content: Generated memo content
            company_dir: Company directory path
            company_name: Company name for filename
            
        Returns:
            Path to saved file
        """
        try:
            company_path = Path(company_dir)
            output_file = company_path / "investment-memo.md"
            
            # Ensure directory exists
            company_path.mkdir(parents=True, exist_ok=True)
            
            # Write memo content
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(memo_content)
            
            logger.info(f"Saved memo to: {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error saving memo file: {e}")
            raise
    
    def _generate_pdf_version(self, memo_content: str, company_dir: str, company_name: str) -> Optional[str]:
        """
        Generate PDF version of the memo
        
        Args:
            memo_content: Generated memo content
            company_dir: Company directory path
            company_name: Company name for filename
            
        Returns:
            Path to generated PDF file or None if generation failed
        """
        if not is_pdf_generation_available():
            logger.info("PDF generation not available - skipping PDF creation")
            return None
        
        try:
            company_path = Path(company_dir)
            pdf_file = company_path / "investment-memo.pdf"
            
            # Generate PDF
            success = convert_markdown_to_pdf(
                memo_content, 
                str(pdf_file), 
                f"Investment Memo - {company_name}"
            )
            
            if success:
                logger.info(f"Generated PDF version: {pdf_file}")
                return str(pdf_file)
            else:
                logger.warning("PDF generation failed")
                return None
                
        except Exception as e:
            logger.error(f"Error generating PDF version: {e}")
            return None
    
    def check_prerequisites(self, company_dir: str) -> Tuple[bool, List[str]]:
        """
        Check if all prerequisites are met for memo generation
        
        Args:
            company_dir: Path to company directory
            
        Returns:
            Tuple of (all_met, list_of_issues)
        """
        issues = []
        company_path = Path(company_dir)
        
        # Check if company directory exists
        if not company_path.exists():
            issues.append(f"Company directory does not exist: {company_dir}")
            return False, issues
        
        # Check for founders checklist
        checklist_file = company_path / "ans-founders-checklist.md"
        if not checklist_file.exists():
            issues.append("ans-founders-checklist.md not found. Please complete founder simulation first.")
        
        # Check for analysis directory
        analysis_dir = company_path / "analysis"
        if not analysis_dir.exists():
            issues.append("Analysis directory not found. Please run multi-agent analysis first.")
        else:
            # Check for analysis files
            analysis_files = list(analysis_dir.glob("*.md"))
            analysis_files = [f for f in analysis_files if f.name != "analysis_summary.md"]
            
            if not analysis_files:
                issues.append("No analysis files found. Please run multi-agent analysis first.")
        
        all_met = len(issues) == 0
        return all_met, issues
    
    def get_available_agents(self, company_dir: str) -> List[str]:
        """
        Get list of available agent names for weight input
        
        Args:
            company_dir: Path to company directory
            
        Returns:
            List of formatted agent names
        """
        discovered = self.discover_analysis_files(company_dir)
        available_agents = [d.agent_name for d in discovered if d.available]
        return sorted(available_agents)


def create_final_memo_processor(config: Optional[FinalMemoConfig] = None) -> FinalMemoProcessor:
    """
    Factory function to create FinalMemoProcessor instance
    
    Args:
        config: Optional configuration for memo generation
        
    Returns:
        Configured FinalMemoProcessor instance
    """
    return FinalMemoProcessor(config=config)