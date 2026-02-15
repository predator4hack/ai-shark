"""
Firestore Database Manager

Provides abstraction layer for Firestore database operations including:
- Company management (CRUD operations)
- Source document storage with content hashing
- Analysis result caching and validation
- Job tracking

This manager follows the same pattern as StorageManager for consistency.
"""

import os
import hashlib
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter


class DatabaseBackend(ABC):
    """Abstract database interface for flexibility"""

    @abstractmethod
    def save_company(self, company_data: Dict) -> str:
        """Save company and return company_id"""
        pass

    @abstractmethod
    def get_company_by_url(self, website: str) -> Optional[Dict]:
        """Retrieve company by website URL"""
        pass

    @abstractmethod
    def save_analysis(self, company_id: str, agent_type: str, analysis_data: Dict) -> None:
        """Save agent analysis result"""
        pass

    @abstractmethod
    def get_analysis(self, company_id: str, agent_type: str) -> Optional[Dict]:
        """Get specific agent analysis"""
        pass

    @abstractmethod
    def check_analysis_valid(self, company_id: str, agent_type: str,
                            current_source_hashes: Dict) -> bool:
        """Check if cached analysis is still valid"""
        pass

    @abstractmethod
    def save_source_document(self, company_id: str, doc_type: str,
                            content: str, metadata: Dict) -> None:
        """Save pitch deck or public data"""
        pass

    @abstractmethod
    def get_source_document(self, company_id: str, doc_type: str) -> Optional[Dict]:
        """Get source document with hash"""
        pass

    @abstractmethod
    def update_processing_status(self, company_id: str, status_updates: Dict) -> None:
        """Update processing status flags"""
        pass


class FirestoreBackend(DatabaseBackend):
    """Firestore implementation of database backend"""

    def __init__(self, project_id: Optional[str] = None):
        """
        Initialize Firestore client

        Args:
            project_id: GCP project ID (optional, uses default if not provided)
        """
        self.db = firestore.Client(project=project_id)
        self.companies = self.db.collection('companies')
        self.jobs = self.db.collection('jobs')
        print(f"✅ Firestore client initialized for project: {project_id or 'default'}")

    def _generate_company_id(self, website: str) -> str:
        """
        Generate deterministic company ID from website URL

        Args:
            website: Company website URL

        Returns:
            16-character SHA-256 hash of the website
        """
        return hashlib.sha256(website.encode()).hexdigest()[:16]

    def _calculate_content_hash(self, content: str) -> str:
        """
        Calculate SHA-256 hash of content for change detection

        Args:
            content: Content to hash

        Returns:
            Full SHA-256 hash
        """
        return hashlib.sha256(content.encode()).hexdigest()

    def save_company(self, company_data: Dict) -> str:
        """
        Save or update company document

        Args:
            company_data: {
                "company_name": str,
                "website": str,
                "sector": str,
                "sub_sector": str,
                "table_of_contents": dict,
                ...
            }

        Returns:
            company_id
        """
        website = company_data.get('website')
        if not website:
            raise ValueError("Website URL is required to save company")

        company_id = self._generate_company_id(website)

        # Check if company exists
        company_ref = self.companies.document(company_id)
        existing = company_ref.get()

        if existing.exists:
            # Update existing company
            update_data = {**company_data}
            update_data['updated_at'] = firestore.SERVER_TIMESTAMP
            company_ref.update(update_data)
            print(f"📝 Updated existing company: {company_data.get('company_name')} (ID: {company_id})")
        else:
            # Create new company
            create_data = {
                'company_id': company_id,
                **company_data,
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP,
                'processing_status': {
                    'pitch_deck_processed': False,
                    'public_data_scraped': False,
                    'analyses_complete': [],
                    'questionnaire_generated': False,
                    'qa_responses_submitted': False,
                    'memo_generated': False
                }
            }
            company_ref.set(create_data)
            print(f"✨ Created new company: {company_data.get('company_name')} (ID: {company_id})")

        return company_id

    def get_company_by_url(self, website: str) -> Optional[Dict]:
        """
        Retrieve company by website URL

        Args:
            website: Company website URL

        Returns:
            Company data dict or None if not found
        """
        company_id = self._generate_company_id(website)
        company_ref = self.companies.document(company_id)
        doc = company_ref.get()

        if doc.exists:
            data = doc.to_dict()
            data['company_id'] = company_id
            return data
        return None

    def save_source_document(self, company_id: str, doc_type: str,
                            content: str, metadata: Dict) -> None:
        """
        Save source document with content hash

        Args:
            company_id: Company identifier
            doc_type: "pitch_deck" | "public_data"
            content: Markdown content
            metadata: Additional metadata
        """
        content_hash = self._calculate_content_hash(content)

        doc_ref = (self.companies.document(company_id)
                  .collection('source_documents')
                  .document(doc_type))

        doc_ref.set({
            'content': content,
            'content_hash': content_hash,
            'uploaded_at': firestore.SERVER_TIMESTAMP,
            'metadata': metadata
        })

        # Update company processing status
        status_field = f'processing_status.{doc_type}_processed'
        self.companies.document(company_id).update({
            status_field: True,
            'updated_at': firestore.SERVER_TIMESTAMP
        })

        print(f"💾 Saved {doc_type} for company {company_id} (hash: {content_hash[:8]}...)")

    def get_source_document(self, company_id: str, doc_type: str) -> Optional[Dict]:
        """
        Get source document with hash

        Args:
            company_id: Company identifier
            doc_type: "pitch_deck" | "public_data"

        Returns:
            Document data dict or None if not found
        """
        doc_ref = (self.companies.document(company_id)
                  .collection('source_documents')
                  .document(doc_type))
        doc = doc_ref.get()

        return doc.to_dict() if doc.exists else None

    def save_analysis(self, company_id: str, agent_type: str,
                     analysis_data: Dict) -> None:
        """
        Save agent analysis with source hashes

        Args:
            company_id: Company identifier
            agent_type: "business" | "market" | "tech" | "risk"
            analysis_data: {
                "markdown_analysis": str,
                "processing_time": float,
                "agent_name": str,
                "source_hashes": {...}
            }
        """
        analysis_ref = (self.companies.document(company_id)
                       .collection('analyses')
                       .document(agent_type))

        analysis_ref.set({
            'agent_type': agent_type,
            **analysis_data,
            'created_at': firestore.SERVER_TIMESTAMP,
            'status': 'completed'
        })

        # Update company's analyses_complete list
        self.companies.document(company_id).update({
            'processing_status.analyses_complete': firestore.ArrayUnion([agent_type]),
            'last_analysis_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        })

        print(f"✅ Saved {agent_type} analysis for company {company_id}")

    def get_analysis(self, company_id: str, agent_type: str) -> Optional[Dict]:
        """
        Get specific agent analysis

        Args:
            company_id: Company identifier
            agent_type: "business" | "market" | "tech" | "risk"

        Returns:
            Analysis data dict or None if not found
        """
        analysis_ref = (self.companies.document(company_id)
                       .collection('analyses')
                       .document(agent_type))
        doc = analysis_ref.get()

        return doc.to_dict() if doc.exists else None

    def check_analysis_valid(self, company_id: str, agent_type: str,
                            current_source_hashes: Dict) -> bool:
        """
        Check if cached analysis is still valid based on source hashes

        Args:
            company_id: Company identifier
            agent_type: Agent to check
            current_source_hashes: {
                "pitch_deck_hash": str,
                "public_data_hash": str
            }

        Returns:
            True if analysis is valid and can be reused
        """
        analysis = self.get_analysis(company_id, agent_type)

        if not analysis:
            return False

        # Compare source hashes
        cached_hashes = analysis.get('source_hashes', {})

        for key, current_hash in current_source_hashes.items():
            if cached_hashes.get(key) != current_hash:
                print(f"🔄 Cache invalidated for {agent_type}: {key} changed")
                return False  # Source changed, invalidate cache

        return True

    def get_required_agents(self, company_id: str,
                           requested_agents: List[str]) -> List[str]:
        """
        Determine which agents need to run based on cache validity

        Args:
            company_id: Company identifier
            requested_agents: List of agent types requested

        Returns:
            List of agents that need to run (cache miss or invalid)
        """
        # Get current source document hashes
        pitch_deck = self.get_source_document(company_id, 'pitch_deck')
        public_data = self.get_source_document(company_id, 'public_data')

        current_hashes = {
            'pitch_deck_hash': pitch_deck.get('content_hash') if pitch_deck else '',
            'public_data_hash': public_data.get('content_hash') if public_data else ''
        }

        agents_to_run = []

        for agent_type in requested_agents:
            if not self.check_analysis_valid(company_id, agent_type, current_hashes):
                agents_to_run.append(agent_type)

        return agents_to_run

    def _calculate_agents_hash(self, agent_types: List[str]) -> str:
        """
        Generate deterministic hash from sorted agent list

        Args:
            agent_types: List of agent type identifiers

        Returns:
            16-character SHA-256 hash of sorted, comma-joined agent types
        """
        # Sort agents to ensure deterministic hash
        sorted_agents = sorted(agent_types)
        agents_string = ','.join(sorted_agents)
        return hashlib.sha256(agents_string.encode()).hexdigest()[:16]

    def save_questionnaire(self, company_id: str, agents: List[str],
                          questionnaire_data: Dict) -> str:
        """
        Save questionnaire to Firestore with agent combination hash

        Args:
            company_id: Company identifier
            agents: List of agent types used for generation
            questionnaire_data: {
                "content": str (markdown content),
                "processing_time": float,
                "source_hashes": {...},
                "metadata": {...}
            }

        Returns:
            agents_hash used as document ID
        """
        agents_hash = self._calculate_agents_hash(agents)

        questionnaire_ref = (self.companies.document(company_id)
                            .collection('questionnaires')
                            .document(agents_hash))

        questionnaire_ref.set({
            'agents_hash': agents_hash,
            'generated_from_agents': sorted(agents),
            'content': questionnaire_data['content'],
            'processing_time': questionnaire_data.get('processing_time', 0),
            'source_hashes': questionnaire_data.get('source_hashes', {}),
            'created_at': firestore.SERVER_TIMESTAMP,
            'metadata': questionnaire_data.get('metadata', {})
        })

        # Update company processing status
        self.companies.document(company_id).update({
            'processing_status.questionnaire_generated': True,
            'processing_status.questionnaire_agents_hash': agents_hash,
            'last_questionnaire_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        })

        print(f"✅ Saved questionnaire for company {company_id} (hash: {agents_hash})")
        return agents_hash

    def get_questionnaire(self, company_id: str, agents: List[str]) -> Optional[Dict]:
        """
        Get cached questionnaire for specific agent combination

        Args:
            company_id: Company identifier
            agents: List of agent types

        Returns:
            Questionnaire data dict or None if not found
        """
        agents_hash = self._calculate_agents_hash(agents)

        questionnaire_ref = (self.companies.document(company_id)
                            .collection('questionnaires')
                            .document(agents_hash))
        doc = questionnaire_ref.get()

        if doc.exists:
            data = doc.to_dict()
            data['agents_hash'] = agents_hash
            return data
        return None

    def check_questionnaire_valid(self, company_id: str, agents: List[str],
                                  current_source_hashes: Dict) -> bool:
        """
        Check if cached questionnaire is still valid

        Validates:
        1. Questionnaire exists for this agent combination
        2. Source documents haven't changed (hash comparison)

        Args:
            company_id: Company identifier
            agents: List of agent types
            current_source_hashes: Current hashes of pitch_deck and public_data

        Returns:
            True if cached questionnaire is valid and can be reused
        """
        questionnaire = self.get_questionnaire(company_id, agents)

        if not questionnaire:
            print(f"   Cache MISS: No questionnaire for agents {sorted(agents)}")
            return False

        # Validate agent list matches
        cached_agents = set(questionnaire.get('generated_from_agents', []))
        requested_agents = set(agents)

        if cached_agents != requested_agents:
            print(f"   Cache MISS: Agent mismatch (cached: {cached_agents}, requested: {requested_agents})")
            return False

        # Compare source hashes
        cached_hashes = questionnaire.get('source_hashes', {})

        for key, current_hash in current_source_hashes.items():
            if cached_hashes.get(key) != current_hash:
                print(f"   Cache INVALIDATED: {key} changed")
                print(f"      Cached: {cached_hashes.get(key, 'N/A')[:8]}...")
                print(f"      Current: {current_hash[:8]}...")
                return False

        print(f"   ✅ Cache HIT: Valid questionnaire found (agents: {sorted(agents)})")
        return True

    def update_processing_status(self, company_id: str,
                                status_updates: Dict) -> None:
        """
        Update processing status flags

        Args:
            company_id: Company identifier
            status_updates: Dict of status fields to update
        """
        updates = {
            f'processing_status.{key}': value
            for key, value in status_updates.items()
        }
        updates['updated_at'] = firestore.SERVER_TIMESTAMP

        self.companies.document(company_id).update(updates)

    def invalidate_analyses(self, company_id: str) -> None:
        """
        Delete all cached analyses when source documents change

        Args:
            company_id: Company identifier
        """
        analyses_ref = self.companies.document(company_id).collection('analyses')

        # Delete all analysis documents
        deleted_count = 0
        for doc in analyses_ref.stream():
            doc.reference.delete()
            deleted_count += 1

        # Reset processing status
        self.companies.document(company_id).update({
            'processing_status.analyses_complete': [],
            'last_analysis_at': None,
            'updated_at': firestore.SERVER_TIMESTAMP
        })

        print(f"🗑️ Invalidated {deleted_count} cached analyses for company {company_id}")

    # Job management methods
    def save_job(self, job_data: Dict) -> None:
        """
        Save job to Firestore

        Args:
            job_data: Job data dictionary
        """
        job_id = job_data['job_id']
        self.jobs.document(job_id).set(job_data)

    def get_job(self, job_id: str) -> Optional[Dict]:
        """
        Get job by ID

        Args:
            job_id: Job identifier

        Returns:
            Job data dict or None if not found
        """
        doc = self.jobs.document(job_id).get()
        return doc.to_dict() if doc.exists else None

    def update_job(self, job_id: str, updates: Dict) -> None:
        """
        Update job fields

        Args:
            job_id: Job identifier
            updates: Fields to update
        """
        self.jobs.document(job_id).update({
            **updates,
            'updated_at': firestore.SERVER_TIMESTAMP
        })


class FirestoreManager:
    """
    Main Firestore interface with environment detection
    Similar to StorageManager pattern
    """

    def __init__(self):
        use_firestore = os.getenv("USE_FIRESTORE", "false").lower() == "true"

        if use_firestore:
            project_id = os.getenv("GCP_PROJECT_ID")
            if not project_id:
                print("⚠️ Warning: GCP_PROJECT_ID not set, using default project")

            try:
                self.backend = FirestoreBackend(project_id)
                self.enabled = True
            except Exception as e:
                print(f"❌ Failed to initialize Firestore: {e}")
                print("⚠️ Falling back to file-based storage")
                self.backend = None
                self.enabled = False
        else:
            print("ℹ️ Firestore disabled (USE_FIRESTORE=false)")
            self.backend = None
            self.enabled = False

    # Delegate all methods to backend
    def save_company(self, company_data: Dict) -> str:
        if not self.enabled:
            raise RuntimeError("Firestore is not enabled")
        return self.backend.save_company(company_data)

    def get_company_by_url(self, website: str) -> Optional[Dict]:
        if not self.enabled:
            return None
        return self.backend.get_company_by_url(website)

    def save_source_document(self, company_id: str, doc_type: str,
                            content: str, metadata: Dict) -> None:
        if not self.enabled:
            raise RuntimeError("Firestore is not enabled")
        return self.backend.save_source_document(company_id, doc_type, content, metadata)

    def get_source_document(self, company_id: str, doc_type: str) -> Optional[Dict]:
        if not self.enabled:
            return None
        return self.backend.get_source_document(company_id, doc_type)

    def save_analysis(self, company_id: str, agent_type: str,
                     analysis_data: Dict) -> None:
        if not self.enabled:
            raise RuntimeError("Firestore is not enabled")
        return self.backend.save_analysis(company_id, agent_type, analysis_data)

    def get_analysis(self, company_id: str, agent_type: str) -> Optional[Dict]:
        if not self.enabled:
            return None
        return self.backend.get_analysis(company_id, agent_type)

    def check_analysis_valid(self, company_id: str, agent_type: str,
                            current_source_hashes: Dict) -> bool:
        if not self.enabled:
            return False
        return self.backend.check_analysis_valid(company_id, agent_type, current_source_hashes)

    def get_required_agents(self, company_id: str,
                           requested_agents: List[str]) -> List[str]:
        if not self.enabled:
            return requested_agents  # Run all if Firestore disabled
        return self.backend.get_required_agents(company_id, requested_agents)

    def update_processing_status(self, company_id: str,
                                status_updates: Dict) -> None:
        if not self.enabled:
            return
        return self.backend.update_processing_status(company_id, status_updates)

    def invalidate_analyses(self, company_id: str) -> None:
        if not self.enabled:
            return
        return self.backend.invalidate_analyses(company_id)

    def save_job(self, job_data: Dict) -> None:
        if not self.enabled:
            return
        return self.backend.save_job(job_data)

    def get_job(self, job_id: str) -> Optional[Dict]:
        if not self.enabled:
            return None
        return self.backend.get_job(job_id)

    def update_job(self, job_id: str, updates: Dict) -> None:
        if not self.enabled:
            return
        return self.backend.update_job(job_id, updates)

    def save_questionnaire(self, company_id: str, agents: List[str],
                          questionnaire_data: Dict) -> str:
        if not self.enabled:
            raise RuntimeError("Firestore is not enabled")
        return self.backend.save_questionnaire(company_id, agents, questionnaire_data)

    def get_questionnaire(self, company_id: str, agents: List[str]) -> Optional[Dict]:
        if not self.enabled:
            return None
        return self.backend.get_questionnaire(company_id, agents)

    def check_questionnaire_valid(self, company_id: str, agents: List[str],
                                  current_source_hashes: Dict) -> bool:
        if not self.enabled:
            return False
        return self.backend.check_questionnaire_valid(company_id, agents, current_source_hashes)


# Global instance (similar to storage_manager pattern)
firestore_db = FirestoreManager()
