import streamlit as st
import os
import tempfile
from pathlib import Path
from typing import Dict, Any

from src.processors.pitch_deck_processor import PitchDeckProcessor
from src.processors.additional_doc_processor import AdditionalDocProcessor
from src.processors.analysis_pipeline import AnalysisPipeline
from src.processors.ref_doc_processor import RefDocProcessor
from src.processors.qa_doc_processor import QADocProcessor
from src.agents.founder_simulation_agent import FounderSimulationAgent
from src.utils.output_manager import OutputManager
from src.utils.docx_converter import convert_founders_checklist_to_docx, is_docx_conversion_available

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Startup Document Processing Pipeline",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Startup Document Processing Pipeline")
    st.markdown("Upload and process startup pitch decks and additional documents using AI-powered extraction.")
    
    # Initialize session state
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = {}
    if 'company_name' not in st.session_state:
        st.session_state.company_name = None
    
    # Create two columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        pitch_deck_section()
    
    with col2:
        additional_docs_section()
    
    # Analysis section
    analysis_section()
    
    # Founder simulation section (shows after analysis completion)
    founder_simulation_section()
    
    # Display results below
    display_results()

def pitch_deck_section():
    """Pitch deck upload and processing section"""
    st.header("🎯 Pitch Deck Upload")
    st.markdown("Upload your startup pitch deck (PDF or PowerPoint) for AI-powered analysis.")
    
    uploaded_file = st.file_uploader(
        "Choose a pitch deck file",
        type=['pdf', 'ppt', 'pptx'],
        help="Upload your startup pitch deck in PDF or PowerPoint format",
        key="pitch_deck_uploader"
    )
    
    if uploaded_file is not None:
        # Display file info
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / (1024*1024):.2f} MB",
            "File type": uploaded_file.type
        }
        
        st.write("**File Details:**")
        for key, value in file_details.items():
            st.write(f"- **{key}:** {value}")
        
        # Process button
        if st.button("🚀 Process Pitch Deck", type="primary", key="process_pitch_deck"):
            process_pitch_deck(uploaded_file)

def additional_docs_section():
    """Additional documents upload section"""
    st.header("📄 Additional Documents")
    st.markdown("Upload additional documents like call transcripts, founder updates, emails, etc.")
    
    uploaded_files = st.file_uploader(
        "Choose additional document files",
        type=['pdf', 'doc', 'docx', 'txt'],
        accept_multiple_files=True,
        help="Upload call transcripts, founder updates, emails, and other documents",
        key="additional_docs_uploader"
    )
    
    if uploaded_files:
        st.write(f"**{len(uploaded_files)} file(s) selected:**")
        for file in uploaded_files:
            st.write(f"- {file.name} ({file.size / (1024*1024):.2f} MB)")
        
        # Check if we have a company name from pitch deck processing
        company_name = get_company_name_from_session()
        if not company_name:
            st.warning("⚠️ Please process a pitch deck first to determine the company name, or the documents will be saved under a fallback name.")
        
        # Process button
        if st.button("📝 Process Additional Documents", type="primary", key="process_additional_docs"):
            process_additional_docs(uploaded_files)

def analysis_section():
    """Analysis pipeline section"""
    st.header("🧠 AI Analysis")
    st.markdown("Run comprehensive analysis using multiple AI agents on your processed documents.")
    
    # Check if we have a processed pitch deck (minimum requirement)
    company_name = get_company_name_from_session()
    if not company_name:
        st.info("ℹ️ Please process a pitch deck first before running analysis.")
        return
    
    # Check if company directory exists
    company_dir = Path("outputs") / company_name
    if not company_dir.exists():
        st.warning("⚠️ Company directory not found. Please process documents first.")
        return
    
    # Check for required files
    pitch_deck_file = company_dir / "pitch_deck.md"
    if not pitch_deck_file.exists():
        st.warning("⚠️ Pitch deck analysis file not found. Please process the pitch deck first.")
        return
    
    # Show available documents
    with st.expander("📋 Available Documents for Analysis"):
        st.write(f"**Company:** {company_name}")
        st.write(f"**Company Directory:** {company_dir}")
        
        # Check what documents are available
        docs_available = []
        if pitch_deck_file.exists():
            docs_available.append("✅ Pitch Deck Analysis")
        
        public_data_file = company_dir / "public_data.md"
        if public_data_file.exists():
            docs_available.append("✅ Public Data Analysis")
        else:
            docs_available.append("⚠️ Public Data Analysis (not available)")
        
        additional_docs_dir = company_dir / "additional_docs"
        if additional_docs_dir.exists() and list(additional_docs_dir.glob("*.md")):
            additional_files = list(additional_docs_dir.glob("*.md"))
            docs_available.append(f"✅ Additional Documents ({len(additional_files)} files)")
        else:
            docs_available.append("⚠️ Additional Documents (not available)")
        
        for doc in docs_available:
            st.write(f"- {doc}")
    
    # Analysis button
    if st.button("🚀 Run Multi-Agent Analysis", type="primary", key="run_analysis"):
        run_analysis(company_name, str(company_dir))

def run_analysis(company_name: str, company_dir: str):
    """Run the multi-agent analysis pipeline"""
    with st.spinner("🧠 Running multi-agent analysis... This may take several minutes."):
        try:
            # Create progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Initializing analysis pipeline...")
            progress_bar.progress(10)
            
            # Initialize the analysis pipeline
            pipeline = AnalysisPipeline(company_dir=company_dir, use_real_llm=True)
            
            status_text.text("Discovering and initializing AI agents...")
            progress_bar.progress(25)
            
            # Show discovered agents
            agent_names = list(pipeline.agents.keys())
            st.info(f"🤖 Discovered {len(agent_names)} AI agents: {', '.join([name.title() for name in agent_names])}")
            
            status_text.text("Running multi-agent analysis...")
            progress_bar.progress(50)
            
            # Run the analysis pipeline
            results = pipeline.run_pipeline()
            
            progress_bar.progress(100)
            status_text.text("Analysis complete!")
            
            # Update session state
            if results:
                st.session_state.processing_status['analysis'] = {
                    'status': 'success',
                    'company_name': company_name,
                    'results': results,
                    'analysis_dir': str(pipeline.analysis_dir),
                    'agents_run': list(results.keys()),
                    'successful_agents': [name for name, result in results.items() if "error" not in result],
                    'failed_agents': [name for name, result in results.items() if "error" in result]
                }
                
                successful_count = len(st.session_state.processing_status['analysis']['successful_agents'])
                failed_count = len(st.session_state.processing_status['analysis']['failed_agents'])
                
                st.success(f"✅ Analysis completed successfully!")
                st.info(f"📊 Results: {successful_count} agents succeeded, {failed_count} agents failed")
                st.info(f"**Analysis Directory:** {pipeline.analysis_dir}")
                
                # Show generated files
                analysis_files = list(pipeline.analysis_dir.glob("*.md"))
                if analysis_files:
                    st.write("**Generated Analysis Files:**")
                    for file_path in analysis_files:
                        st.write(f"- ✅ {file_path.name}")
            else:
                st.error("❌ Analysis failed to produce results")
                st.session_state.processing_status['analysis'] = {
                    'status': 'failed',
                    'error': 'No results generated'
                }
                
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
            st.session_state.processing_status['analysis'] = {
                'status': 'failed',
                'error': str(e)
            }

def process_pitch_deck(uploaded_file):
    """Process uploaded pitch deck"""
    with st.spinner("🔄 Processing pitch deck... This may take a few minutes."):
        try:
            # Save uploaded file temporarily
            temp_path = save_temp_file(uploaded_file)
            
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Converting file to images...")
            progress_bar.progress(25)
            
            # Process using PitchDeckProcessor
            processor = PitchDeckProcessor()
            
            status_text.text("Extracting metadata and table of contents...")
            progress_bar.progress(50)
            
            result = processor.process(temp_path, "outputs")
            
            status_text.text("Performing topic-based extraction...")
            progress_bar.progress(75)
            
            # Clean up temp file
            os.unlink(temp_path)
            
            progress_bar.progress(100)
            status_text.text("Processing complete!")
            
            # Update session state
            if result['status'] == 'success':
                st.session_state.processing_status['pitch_deck'] = result
                st.session_state.company_name = result.get('company_name')
                
                st.success(f"✅ Pitch deck processed successfully!")
                st.info(f"**Company:** {result['company_name']}")
                st.info(f"**Output Directory:** {result['output_dir']}")
                
                # Display metadata if available
                if result.get('metadata'):
                    with st.expander("📊 Extracted Company Information"):
                        metadata = result['metadata']
                        if metadata.get('sector'):
                            st.write(f"**Sector:** {metadata['sector']}")
                        if metadata.get('sub_sector'):
                            st.write(f"**Sub-sector:** {metadata['sub_sector']}")
                        if metadata.get('website'):
                            st.write(f"**Website:** {metadata['website']}")
            else:
                st.error(f"❌ Error processing pitch deck: {result.get('error', 'Unknown error')}")
                st.session_state.processing_status['pitch_deck'] = result
                
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            st.session_state.processing_status['pitch_deck'] = {
                'status': 'failed',
                'error': str(e)
            }

def process_additional_docs(uploaded_files):
    """Process uploaded additional documents"""
    # Get company name from pitch deck processing or use fallback
    company_name = get_company_name_from_session()
    if not company_name:
        company_name = OutputManager.generate_fallback_name()
        st.info(f"Using fallback company name: {company_name}")
    
    # Create company directory
    company_dir = OutputManager.create_company_dir(company_name)
    
    # Create progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    results = []
    processor = AdditionalDocProcessor()
    
    for i, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing {uploaded_file.name}... ({i+1}/{len(uploaded_files)})")
        
        try:
            # Save file temporarily
            temp_path = save_temp_file(uploaded_file)
            
            # Process the document
            result = processor.process(temp_path, company_dir)
            results.append(result)
            
            # Clean up temp file
            os.unlink(temp_path)
            
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
            results.append({
                'status': 'failed', 
                'filename': uploaded_file.name, 
                'error': str(e)
            })
        
        progress_bar.progress((i + 1) / len(uploaded_files))
    
    # Update session state
    st.session_state.processing_status['additional_docs'] = results
    
    # Display results
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] != 'success']
    
    if successful:
        st.success(f"✅ Successfully processed {len(successful)} document(s)")
    
    if failed:
        st.error(f"❌ Failed to process {len(failed)} document(s)")
        with st.expander("View errors"):
            for result in failed:
                st.write(f"**{result['filename']}:** {result.get('error', 'Unknown error')}")
    
    status_text.text("All documents processed!")

def founder_simulation_section():
    """Founder simulation section - shows after analysis completion"""
    # Only show if analysis has been completed successfully
    if ('analysis' not in st.session_state.processing_status or 
        st.session_state.processing_status['analysis'].get('status') != 'success'):
        return
    
    company_name = get_company_name_from_session()
    if not company_name:
        return
    
    # Check if founders-checklist.md exists
    company_dir = Path("outputs") / company_name
    checklist_file = company_dir / "founders-checklist.md"
    
    if not checklist_file.exists():
        st.warning("⚠️ founders-checklist.md not found. Cannot proceed with founder simulation.")
        return
    
    st.header("🎭 Founder Simulation")
    st.markdown("Simulate founder responses to the investment questionnaire using AI or upload direct Q&A responses.")
    
    # Two options for founder simulation
    simulation_option = st.radio(
        "Choose simulation method:",
        [
            "📚 Upload Reference Documents for AI Simulation",
            "📝 Upload Direct Q&A Document"
        ],
        help="Choose how you want to generate founder responses"
    )
    
    if simulation_option == "📚 Upload Reference Documents for AI Simulation":
        reference_documents_section(company_name, str(company_dir))
    else:
        direct_qa_section(company_name, str(company_dir))

def reference_documents_section(company_name: str, company_dir: str):
    """Handle reference documents upload and processing"""
    st.subheader("📚 Reference Documents Upload")
    st.markdown("Upload documents like investment memos, company updates, or founder interviews for AI simulation.")
    
    uploaded_files = st.file_uploader(
        "Choose reference document files",
        type=['pdf', 'doc', 'docx', 'txt'],
        accept_multiple_files=True,
        help="Upload reference documents for AI-powered founder response simulation",
        key="ref_docs_uploader"
    )
    
    if uploaded_files:
        st.write(f"**{len(uploaded_files)} reference document(s) selected:**")
        for file in uploaded_files:
            st.write(f"- {file.name} ({file.size / (1024*1024):.2f} MB)")
        
        # Show existing ref-data files if any
        ref_data_dir = Path(company_dir) / "ref-data"
        if ref_data_dir.exists():
            existing_files = list(ref_data_dir.glob("*.md"))
            if existing_files:
                with st.expander("📋 Existing Reference Documents"):
                    for file in existing_files:
                        st.write(f"- {file.name}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📤 Process Reference Documents", type="primary", key="process_ref_docs"):
                process_reference_documents(uploaded_files, company_dir)
        
        with col2:
            # Check if we have processed ref documents and can run simulation
            if ref_data_dir.exists() and list(ref_data_dir.glob("*.md")):
                if st.button("🤖 Run AI Simulation", type="secondary", key="run_ai_simulation"):
                    run_founder_simulation(company_dir)

def direct_qa_section(company_name: str, company_dir: str):
    """Handle direct Q&A document upload and processing"""
    st.subheader("📝 Direct Q&A Document Upload")
    st.markdown("Upload a document containing question-answer pairs already answered by the founder.")
    
    uploaded_file = st.file_uploader(
        "Choose Q&A document file",
        type=['pdf', 'doc', 'docx', 'txt'],
        help="Upload a document with founder's direct responses to questions",
        key="qa_doc_uploader"
    )
    
    if uploaded_file:
        st.write(f"**Selected file:** {uploaded_file.name} ({uploaded_file.size / (1024*1024):.2f} MB)")
        
        if st.button("📝 Process Q&A Document", type="primary", key="process_qa_doc"):
            process_qa_document(uploaded_file, company_dir)

def process_reference_documents(uploaded_files, company_dir: str):
    """Process uploaded reference documents"""
    with st.spinner("🔄 Processing reference documents..."):
        try:
            processor = RefDocProcessor()
            result = processor.process_reference_documents(uploaded_files, company_dir)
            
            if result.success:
                st.success(f"✅ Successfully processed {result.metadata['successful_files']} reference documents!")
                st.info(f"📁 Documents saved to: {result.output_file}")
                
                # Update session state
                st.session_state.processing_status['ref_docs'] = {
                    'status': 'success',
                    'result': result,
                    'ref_data_dir': result.output_file
                }
                
                if result.metadata['failed_files'] > 0:
                    st.warning(f"⚠️ {result.metadata['failed_files']} files failed to process")
                    with st.expander("View failed files"):
                        for failed in result.metadata['failed_file_details']:
                            st.write(f"**{failed['filename']}:** {failed['error']}")
                
            else:
                st.error(f"❌ Reference document processing failed: {result.error_message}")
                st.session_state.processing_status['ref_docs'] = {
                    'status': 'failed',
                    'error': result.error_message
                }
                
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")

def process_qa_document(uploaded_file, company_dir: str):
    """Process uploaded Q&A document"""
    with st.spinner("🔄 Processing Q&A document..."):
        try:
            processor = QADocProcessor()
            result = processor.process_qa_document(uploaded_file, company_dir)
            
            if result.success:
                st.success(f"✅ Q&A document processed successfully!")
                st.info(f"📄 Output saved to: {result.output_file}")
                
                # Update session state
                st.session_state.processing_status['qa_simulation'] = {
                    'status': 'success',
                    'result': result,
                    'output_file': result.output_file,
                    'simulation_type': 'direct_qa'
                }
                
                # Show some stats
                if result.metadata:
                    st.write("**Processing Summary:**")
                    st.write(f"- Q&A pairs extracted: {result.metadata.get('qa_pairs_extracted', 0)}")
                    st.write(f"- Responses generated: {result.metadata.get('responses_generated', 0)}")
                
            else:
                st.error(f"❌ Q&A document processing failed: {result.error_message}")
                st.session_state.processing_status['qa_simulation'] = {
                    'status': 'failed',
                    'error': result.error_message
                }
                
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")

def run_founder_simulation(company_dir: str):
    """Run AI-powered founder simulation"""
    with st.spinner("🤖 Running AI founder simulation... This may take several minutes."):
        try:
            agent = FounderSimulationAgent()
            result = agent.process_simulation(company_dir)
            
            if result.success:
                st.success(f"✅ Founder simulation completed successfully!")
                st.info(f"📄 Output saved to: {result.output_file}")
                
                # Update session state
                st.session_state.processing_status['ai_simulation'] = {
                    'status': 'success',
                    'result': result,
                    'output_file': result.output_file,
                    'simulation_type': 'ai_simulation'
                }
                
                # Show simulation stats
                if result.metadata:
                    st.write("**Simulation Summary:**")
                    st.write(f"- Reference documents used: {result.metadata.get('reference_doc_count', 0)}")
                    st.write(f"- Questions answered: {result.metadata.get('questions_answered', 0)}")
                    st.write(f"- Average confidence: {result.metadata.get('average_confidence', 0):.1%}")
                
            else:
                st.error(f"❌ Founder simulation failed: {result.error_message}")
                st.session_state.processing_status['ai_simulation'] = {
                    'status': 'failed',
                    'error': result.error_message
                }
                
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")

def display_results():
    """Display processing results and output file links"""
    if st.session_state.processing_status:
        st.header("📋 Processing Results")
        
        # Display pitch deck results
        if 'pitch_deck' in st.session_state.processing_status:
            display_pitch_deck_results()
        
        # Display additional docs results
        if 'additional_docs' in st.session_state.processing_status:
            display_additional_docs_results()
        
        # Display analysis results
        if 'analysis' in st.session_state.processing_status:
            display_analysis_results()
        
        # Display founder simulation results
        if 'ai_simulation' in st.session_state.processing_status:
            display_ai_simulation_results()
        
        if 'qa_simulation' in st.session_state.processing_status:
            display_qa_simulation_results()

def display_pitch_deck_results():
    """Display pitch deck processing results"""
    result = st.session_state.processing_status['pitch_deck']
    
    with st.expander("🎯 Pitch Deck Results", expanded=True):
        if result['status'] == 'success':
            st.success("Pitch deck processed successfully!")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Company:** {result['company_name']}")
                st.write(f"**Output Directory:** {result['output_dir']}")
            
            with col2:
                if result.get('files_created'):
                    st.write("**Files Created:**")
                    for file_path in result['files_created']:
                        if os.path.exists(file_path):
                            filename = os.path.basename(file_path)
                            st.write(f"- ✅ {filename}")
                        else:
                            filename = os.path.basename(file_path)
                            st.write(f"- ❌ {filename} (not found)")
            
            # Provide download links if possible
            if result.get('output_dir') and os.path.exists(result['output_dir']):
                st.write("**📁 Access your files at:**")
                st.code(result['output_dir'])
                
        else:
            st.error(f"Processing failed: {result.get('error', 'Unknown error')}")

def display_additional_docs_results():
    """Display additional documents processing results"""
    results = st.session_state.processing_status['additional_docs']
    
    with st.expander("📄 Additional Documents Results", expanded=True):
        successful = [r for r in results if r['status'] == 'success']
        failed = [r for r in results if r['status'] != 'success']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**✅ Successfully Processed:**")
            for result in successful:
                st.write(f"- {result['filename']}")
        
        with col2:
            if failed:
                st.write("**❌ Failed to Process:**")
                for result in failed:
                    st.write(f"- {result['filename']}")

def display_analysis_results():
    """Display analysis results"""
    result = st.session_state.processing_status['analysis']
    
    with st.expander("🧠 AI Analysis Results", expanded=True):
        if result['status'] == 'success':
            st.success("Multi-agent analysis completed successfully!")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Company:** {result['company_name']}")
                st.write(f"**Agents Run:** {len(result['agents_run'])}")
                st.write(f"**Successful:** {len(result['successful_agents'])}")
                st.write(f"**Failed:** {len(result['failed_agents'])}")
            
            with col2:
                st.write(f"**Analysis Directory:** {result['analysis_dir']}")
                
                # Show generated files
                analysis_dir = Path(result['analysis_dir'])
                if analysis_dir.exists():
                    analysis_files = list(analysis_dir.glob("*.md"))
                    if analysis_files:
                        st.write("**Generated Files:**")
                        for file_path in analysis_files:
                            st.write(f"- ✅ {file_path.name}")
            
            # Show agent details
            if result.get('successful_agents'):
                st.write("**✅ Successful Agents:**")
                for agent in result['successful_agents']:
                    st.write(f"- {agent.title()} Analysis Agent")
            
            if result.get('failed_agents'):
                st.write("**❌ Failed Agents:**")
                for agent in result['failed_agents']:
                    st.write(f"- {agent.title()} Analysis Agent")
            
            # Check for questionnaire file and provide download
            check_and_display_questionnaire_download(result.get('company_name'), result['analysis_dir'])
            
            # Provide access information
            st.write("**📁 Access your analysis files at:**")
            st.code(result['analysis_dir'])
                
        else:
            st.error(f"Analysis failed: {result.get('error', 'Unknown error')}")

def check_and_display_questionnaire_download(company_name: str, analysis_dir: str):
    """Check for questionnaire file and display download options"""
    if not company_name or not analysis_dir:
        return
    
    # Look for questionnaire file in company directory (parent of analysis_dir)
    company_dir = Path(analysis_dir).parent
    questionnaire_file = company_dir / "founders-checklist.md"
    
    if questionnaire_file.exists():
        st.write("**📋 Founder Investment Questionnaire Available**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Read file content for download
            with open(questionnaire_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            st.download_button(
                label="📋 Download Questionnaire (Markdown)",
                data=content,
                file_name=f"{company_name}-founders-checklist.md",
                mime="text/markdown",
                help="Download the questionnaire as a Markdown file"
            )
        
        with col2:
            # DOCX download option
            if is_docx_conversion_available():
                if st.button("📄 Generate & Download DOCX", help="Convert and download as Word document"):
                    try:
                        with st.spinner("Converting to DOCX..."):
                            docx_file = convert_founders_checklist_to_docx(str(questionnaire_file))
                            
                            # Read DOCX file for download
                            with open(docx_file, 'rb') as f:
                                docx_content = f.read()
                            
                            st.download_button(
                                label="💾 Download DOCX File",
                                data=docx_content,
                                file_name=f"{company_name}-founders-checklist.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                            
                            st.success("✅ DOCX file generated successfully!")
                            
                    except Exception as e:
                        st.error(f"❌ DOCX conversion failed: {e}")
            else:
                st.info("📄 DOCX conversion requires python-docx package")
                st.code("pip install python-docx")
        
        # Show file info
        file_size = questionnaire_file.stat().st_size
        st.write(f"**File Info:** {file_size:,} bytes, Modified: {questionnaire_file.stat().st_mtime}")
        
    else:
        st.info("📋 Questionnaire not yet generated. Run analysis to create it.")

def display_ai_simulation_results():
    """Display AI simulation results"""
    result = st.session_state.processing_status['ai_simulation']
    
    with st.expander("🤖 AI Founder Simulation Results", expanded=True):
        if result['status'] == 'success':
            st.success("AI founder simulation completed successfully!")
            
            simulation_result = result['result']
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Simulation Type:** AI-Powered")
                st.write(f"**Output File:** {simulation_result.output_file}")
                st.write(f"**Processing Time:** {simulation_result.processing_time:.1f}s")
            
            with col2:
                if simulation_result.metadata:
                    st.write(f"**Reference Documents:** {simulation_result.metadata.get('reference_doc_count', 0)}")
                    st.write(f"**Questions Answered:** {simulation_result.metadata.get('questions_answered', 0)}")
                    st.write(f"**Average Confidence:** {simulation_result.metadata.get('average_confidence', 0):.1%}")
            
            # Provide download link
            if simulation_result.output_file and os.path.exists(simulation_result.output_file):
                with open(simulation_result.output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                st.download_button(
                    label="📋 Download Founder Responses",
                    data=content,
                    file_name="ans-founders-checklist.md",
                    mime="text/markdown",
                    help="Download the AI-generated founder responses"
                )
                
                st.write("**📁 Access your file at:**")
                st.code(simulation_result.output_file)
        else:
            st.error(f"AI simulation failed: {result.get('error', 'Unknown error')}")

def display_qa_simulation_results():
    """Display Q&A simulation results"""
    result = st.session_state.processing_status['qa_simulation']
    
    with st.expander("📝 Q&A Document Processing Results", expanded=True):
        if result['status'] == 'success':
            st.success("Q&A document processed successfully!")
            
            simulation_result = result['result']
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Simulation Type:** Direct Q&A Upload")
                st.write(f"**Output File:** {simulation_result.output_file}")
                st.write(f"**Processing Time:** {simulation_result.processing_time:.1f}s")
            
            with col2:
                if simulation_result.metadata:
                    st.write(f"**Q&A Pairs Extracted:** {simulation_result.metadata.get('qa_pairs_extracted', 0)}")
                    st.write(f"**Responses Generated:** {simulation_result.metadata.get('responses_generated', 0)}")
                    st.write(f"**Source Document:** {simulation_result.metadata.get('source_document', 'Unknown')}")
            
            # Provide download link
            if simulation_result.output_file and os.path.exists(simulation_result.output_file):
                with open(simulation_result.output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                st.download_button(
                    label="📋 Download Founder Responses",
                    data=content,
                    file_name="ans-founders-checklist.md",
                    mime="text/markdown",
                    help="Download the processed founder responses"
                )
                
                st.write("**📁 Access your file at:**")
                st.code(simulation_result.output_file)
        else:
            st.error(f"Q&A processing failed: {result.get('error', 'Unknown error')}")

def save_temp_file(uploaded_file) -> str:
    """Save uploaded file to temporary location"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        return tmp_file.name

def get_company_name_from_session() -> str | None:
    """Get company name from session state"""
    if st.session_state.company_name:
        return st.session_state.company_name
    
    # Try to get from pitch deck results
    if 'pitch_deck' in st.session_state.processing_status:
        result = st.session_state.processing_status['pitch_deck']
        if result.get('status') == 'success' and result.get('company_name'):
            return result['company_name']
    
    return None

# Add sidebar with information
def add_sidebar():
    """Add sidebar with application information"""
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This application processes startup documents using AI:
        
        **Pitch Deck Processing:**
        - Extracts company metadata
        - Generates table of contents
        - Performs topic-based analysis
        - Saves structured markdown output
        
        **Additional Documents:**
        - Processes transcripts, emails, updates
        - Structures content using AI
        - Converts to readable markdown format
        
        **Supported Formats:**
        - PDF files
        - PowerPoint (.ppt, .pptx)
        - Word documents (.doc, .docx)
        - Text files (.txt)
        """)
        
        st.header("🔧 Settings")
        if st.button("🗑️ Clear All Results"):
            st.session_state.processing_status = {}
            st.session_state.company_name = None
            st.rerun()

if __name__ == "__main__":
    add_sidebar()
    main()