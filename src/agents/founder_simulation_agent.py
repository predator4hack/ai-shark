"""
Founder Simulation Agent

AI agent that simulates founder responses based on reference documents
"""

import os
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

from ..models.founder_simulation_models import (
    FounderSimulationConfig, 
    SimulationResult, 
    QAEntry, 
    ReferenceDocument
)
from ..utils.founder_simulation_utils import (
    validate_founders_checklist_exists,
    load_all_markdown_files,
    load_founders_checklist,
    format_simulation_output,
    calculate_simulation_confidence
)
from ..utils.llm_manager import LLMManager
from ..utils.output_manager import OutputManager


class FounderSimulationAgent:
    """
    AI agent that simulates founder responses based on reference documents
    """
    
    def __init__(self, llm_manager: Optional[LLMManager] = None):
        """
        Initialize the Founder Simulation Agent
        
        Args:
            llm_manager: Optional LLM manager instance
        """
        self.agent_name = "FounderSimulationAgent"
        self.llm_manager = llm_manager or LLMManager()
        
    def process_simulation(self, company_dir: str, config: Optional[FounderSimulationConfig] = None) -> SimulationResult:
        """
        Main method to process founder simulation
        
        Args:
            company_dir: Path to company directory
            config: Optional simulation configuration
            
        Returns:
            SimulationResult with processing results
        """
        start_time = time.time()
        
        print(f"\n🤖 Starting Founder Simulation")
        print("=" * 50)
        print(f"Company Directory: {company_dir}")
        
        # Use default config if none provided
        if config is None:
            config = FounderSimulationConfig(
                company_dir=company_dir,
                simulation_type="reference_docs",
                use_real_llm=True
            )
        
        try:
            # Validate prerequisites
            if not validate_founders_checklist_exists(company_dir):
                return SimulationResult(
                    success=False,
                    error_message="founders-checklist.md not found. Please complete analysis pipeline first.",
                    processing_time=time.time() - start_time
                )
            
            # Load reference documents
            ref_data_dir = Path(company_dir) / "ref-data"
            reference_docs = self.load_reference_documents(str(ref_data_dir))
            
            if not reference_docs:
                return SimulationResult(
                    success=False,
                    error_message="No reference documents found in ref-data directory",
                    processing_time=time.time() - start_time
                )
            
            print(f"📚 Loaded {len(reference_docs)} reference documents")
            
            # Load founders checklist
            checklist_path = Path(company_dir) / "founders-checklist.md"
            checklist_questions = self.load_founders_checklist(str(checklist_path))
            
            if not checklist_questions:
                return SimulationResult(
                    success=False,
                    error_message="Could not extract questions from founders-checklist.md",
                    processing_time=time.time() - start_time
                )
            
            print(f"❓ Loaded {len(checklist_questions)} questions from checklist")
            
            # Generate simulated responses
            qa_entries = self.generate_simulated_responses(checklist_questions, reference_docs, config)
            
            if not qa_entries:
                return SimulationResult(
                    success=False,
                    error_message="Failed to generate any simulated responses",
                    processing_time=time.time() - start_time
                )
            
            print(f"💬 Generated {len(qa_entries)} simulated responses")
            
            # Save results
            output_path = Path(company_dir) / "ans-founders-checklist.md"
            success = self.save_simulation_results(qa_entries, str(output_path), reference_docs)
            
            processing_time = time.time() - start_time
            
            if success:
                confidence = calculate_simulation_confidence(qa_entries)
                
                print(f"✅ Founder simulation completed successfully!")
                print(f"📄 Output saved to: {output_path}")
                print(f"🎯 Average confidence: {confidence:.1%}")
                
                return SimulationResult(
                    success=True,
                    output_file=str(output_path),
                    processing_time=processing_time,
                    metadata={
                        'simulation_type': config.simulation_type,
                        'reference_doc_count': len(reference_docs),
                        'questions_answered': len(qa_entries),
                        'average_confidence': confidence,
                        'source_documents': [doc.filename for doc in reference_docs]
                    }
                )
            else:
                return SimulationResult(
                    success=False,
                    error_message="Failed to save simulation results",
                    processing_time=processing_time
                )
                
        except Exception as e:
            return SimulationResult(
                success=False,
                error_message=f"Simulation failed: {e}",
                processing_time=time.time() - start_time
            )
    
    def load_reference_documents(self, ref_data_dir: str) -> List[ReferenceDocument]:
        """
        Load all reference documents from ref-data directory
        
        Args:
            ref_data_dir: Path to ref-data directory
            
        Returns:
            List of ReferenceDocument objects
        """
        return load_all_markdown_files(ref_data_dir)
    
    def load_founders_checklist(self, checklist_path: str) -> List[str]:
        """
        Load questionnaire questions from founders checklist
        
        Args:
            checklist_path: Path to founders-checklist.md
            
        Returns:
            List of questions
        """
        return load_founders_checklist(checklist_path)
    
    def generate_simulated_responses(self, questions: List[str], 
                                   reference_docs: List[ReferenceDocument],
                                   config: FounderSimulationConfig) -> List[QAEntry]:
        """
        Generate simulated founder responses using LLM
        
        Args:
            questions: List of questions from founders checklist
            reference_docs: List of reference documents
            config: Simulation configuration
            
        Returns:
            List of QAEntry objects with simulated responses
        """
        print("🧠 Generating simulated responses using AI...")
        
        qa_entries = []
        
        # Prepare reference content summary
        ref_content = self._prepare_reference_content(reference_docs)
        
        # Process questions in batches to manage context window
        batch_size = 5  # Process 5 questions at a time
        for i in range(0, len(questions), batch_size):
            batch_questions = questions[i:i + batch_size]
            
            print(f"📝 Processing questions {i+1}-{min(i+batch_size, len(questions))} of {len(questions)}")
            
            try:
                batch_responses = self._generate_batch_responses(
                    batch_questions, 
                    ref_content, 
                    reference_docs,
                    config
                )
                qa_entries.extend(batch_responses)
                
            except Exception as e:
                print(f"⚠️ Error processing batch {i//batch_size + 1}: {e}")
                # Add fallback responses for failed batch
                for question in batch_questions:
                    qa_entries.append(QAEntry(
                        question=question,
                        answer="*Unable to generate response due to processing error*",
                        confidence=0.0,
                        source_documents=[]
                    ))
        
        return qa_entries
    
    def _prepare_reference_content(self, reference_docs: List[ReferenceDocument]) -> str:
        """
        Prepare reference content for LLM context
        
        Args:
            reference_docs: List of reference documents
            
        Returns:
            Formatted reference content string
        """
        content_parts = []
        
        for doc in reference_docs:
            # Limit content length to avoid context window issues
            content = doc.content
            if len(content) > 2000:  # Truncate very long documents
                content = content[:2000] + "...[truncated]"
            
            content_parts.append(f"=== {doc.filename} ===\n{content}\n")
        
        return "\n".join(content_parts)
    
    def _generate_batch_responses(self, questions: List[str], 
                                ref_content: str,
                                reference_docs: List[ReferenceDocument],
                                config: FounderSimulationConfig) -> List[QAEntry]:
        """
        Generate responses for a batch of questions
        
        Args:
            questions: Batch of questions to process
            ref_content: Reference content string
            reference_docs: List of reference documents
            config: Simulation configuration
            
        Returns:
            List of QAEntry objects
        """
        # Create the simulation prompt
        prompt = self._create_simulation_prompt(questions, ref_content)
        
        try:
            # Use LLM to generate responses
            if config.use_real_llm:
                response = self.llm_manager.generate_founder_responses(prompt)
            else:
                response = self._generate_mock_responses(questions)
            
            # Parse the response into QAEntry objects
            qa_entries = self._parse_llm_response(response, questions, reference_docs)
            
            return qa_entries
            
        except Exception as e:
            print(f"Error generating batch responses: {e}")
            # Return fallback responses
            return [QAEntry(
                question=q,
                answer="*Unable to generate response*",
                confidence=0.0,
                source_documents=[]
            ) for q in questions]
    
    def _create_simulation_prompt(self, questions: List[str], ref_content: str) -> str:
        """
        Create prompt for founder response simulation
        
        Args:
            questions: List of questions to answer
            ref_content: Reference document content
            
        Returns:
            Formatted prompt string
        """
        questions_text = "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions))
        
        prompt = f"""You are simulating a startup founder answering investor questions based on available company documents and information. 

REFERENCE DOCUMENTS:
{ref_content}

QUESTIONS TO ANSWER:
{questions_text}

INSTRUCTIONS:
- Answer each question as if you are the founder of this startup
- Base your answers on the information provided in the reference documents
- Be specific and cite relevant details from the documents when possible
- If information is not available in the documents, indicate this clearly
- Keep answers concise but informative (2-4 sentences each)
- Maintain a professional, confident founder tone

Please provide answers in the following format:
1. [Answer to question 1]
2. [Answer to question 2]
...and so on.

ANSWERS:"""

        return prompt
    
    def _parse_llm_response(self, response: str, questions: List[str], 
                          reference_docs: List[ReferenceDocument]) -> List[QAEntry]:
        """
        Parse LLM response into QAEntry objects
        
        Args:
            response: Raw LLM response
            questions: Original questions
            reference_docs: Reference documents for source attribution
            
        Returns:
            List of QAEntry objects
        """
        qa_entries = []
        source_doc_names = [doc.filename for doc in reference_docs]
        
        # Split response by numbered answers
        import re
        answer_pattern = r'(\d+)\.\s*(.*?)(?=\d+\.|$)'
        matches = re.findall(answer_pattern, response, re.DOTALL)
        
        for i, question in enumerate(questions):
            answer = "*No response generated*"
            confidence = 0.0
            
            # Find matching answer by number
            for num_str, answer_text in matches:
                if int(num_str) == i + 1:
                    answer = answer_text.strip()
                    confidence = 0.8  # Default confidence for LLM responses
                    break
            
            # Determine confidence based on answer quality
            if "*No response generated*" in answer or "*Unable to" in answer:
                confidence = 0.0
            elif "not available" in answer.lower() or "no information" in answer.lower():
                confidence = 0.3
            
            qa_entries.append(QAEntry(
                question=question,
                answer=answer,
                confidence=confidence,
                source_documents=source_doc_names if confidence > 0 else []
            ))
        
        return qa_entries
    
    def _generate_mock_responses(self, questions: List[str]) -> str:
        """
        Generate mock responses for testing (when use_real_llm=False)
        
        Args:
            questions: List of questions
            
        Returns:
            Mock response string
        """
        responses = []
        for i, question in enumerate(questions, 1):
            responses.append(f"{i}. This is a simulated response to the question about {question[:30]}...")
        
        return "\n".join(responses)
    
    def save_simulation_results(self, qa_entries: List[QAEntry], output_path: str, 
                              reference_docs: List[ReferenceDocument]) -> bool:
        """
        Save simulation results to ans-founders-checklist.md
        
        Args:
            qa_entries: List of QA entries
            output_path: Path to output file
            reference_docs: Reference documents for metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            metadata = {
                'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'simulation_type': 'AI Simulation',
                'source_documents': [doc.filename for doc in reference_docs],
                'source_doc_count': len(reference_docs)
            }
            
            markdown_content = format_simulation_output(qa_entries, metadata)
            
            return OutputManager.save_file(markdown_content, output_path)
            
        except Exception as e:
            print(f"Error saving simulation results: {e}")
            return False


def create_founder_simulation_agent(llm_manager: Optional[LLMManager] = None) -> FounderSimulationAgent:
    """
    Factory function to create a FounderSimulationAgent instance
    
    Args:
        llm_manager: Optional LLM manager instance
        
    Returns:
        Configured FounderSimulationAgent instance
    """
    return FounderSimulationAgent(llm_manager=llm_manager)