"""
Firebase Storage Manager for binary file storage (PDFs)

This module provides a manager for storing and retrieving PDF files
in Firebase Storage with signed URL generation for secure access.
"""

import os
from datetime import timedelta
from typing import Optional
from firebase_admin import credentials, initialize_app, storage
import firebase_admin


class FirebaseStorageManager:
    """Manages Firebase Storage for PDF files"""

    def __init__(self):
        self.enabled = os.getenv("USE_FIRESTORE", "false").lower() == "true"

        if self.enabled:
            try:
                # Initialize Firebase Admin if not already done
                if not firebase_admin._apps:
                    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                    project_id = os.getenv("GCP_PROJECT_ID")

                    if not project_id:
                        raise ValueError("GCP_PROJECT_ID environment variable is required")

                    storage_bucket = f"{project_id}.appspot.com"

                    if cred_path and os.path.exists(cred_path):
                        # Use service account credentials
                        cred = credentials.Certificate(cred_path)
                        initialize_app(cred, {
                            'storageBucket': storage_bucket
                        })
                        print(f"✅ Firebase Admin initialized with service account")
                    else:
                        # Use application default credentials
                        initialize_app(options={
                            'storageBucket': storage_bucket
                        })
                        print(f"✅ Firebase Admin initialized with default credentials")

                self.bucket = storage.bucket()
                print(f"✅ Firebase Storage initialized (bucket: {storage_bucket})")
            except Exception as e:
                print(f"❌ Failed to initialize Firebase Storage: {e}")
                self.bucket = None
                self.enabled = False
        else:
            print("ℹ️ Firebase Storage disabled (USE_FIRESTORE=false)")
            self.bucket = None

    def upload_pdf(self, company_name: str, pdf_content: bytes, filename: str) -> Optional[str]:
        """
        Upload PDF to Firebase Storage

        Args:
            company_name: Sanitized company name
            pdf_content: PDF binary content
            filename: e.g., "investment-memo.pdf"

        Returns:
            Download URL or None if upload fails
        """
        if not self.enabled or not self.bucket:
            print("⚠️ Firebase Storage not enabled, skipping PDF upload")
            return None

        try:
            blob_path = f"pdfs/{company_name}/{filename}"
            blob = self.bucket.blob(blob_path)

            # Upload PDF content
            blob.upload_from_string(pdf_content, content_type='application/pdf')

            # Generate signed URL (expires in 7 days)
            url = blob.generate_signed_url(expiration=timedelta(days=7))

            print(f"✅ Uploaded PDF: {blob_path}")
            return url
        except Exception as e:
            print(f"❌ Failed to upload PDF: {e}")
            return None

    def get_pdf_url(self, company_name: str, filename: str) -> Optional[str]:
        """
        Get signed download URL for existing PDF

        Args:
            company_name: Sanitized company name
            filename: e.g., "investment-memo.pdf"

        Returns:
            Signed download URL or None if not found
        """
        if not self.enabled or not self.bucket:
            return None

        try:
            blob_path = f"pdfs/{company_name}/{filename}"
            blob = self.bucket.blob(blob_path)

            if not blob.exists():
                print(f"ℹ️ PDF not found in Firebase Storage: {blob_path}")
                return None

            # Generate signed URL (expires in 7 days)
            url = blob.generate_signed_url(expiration=timedelta(days=7))
            print(f"✅ Generated signed URL for: {blob_path}")
            return url
        except Exception as e:
            print(f"❌ Failed to get PDF URL: {e}")
            return None

    def delete_pdf(self, company_name: str, filename: str) -> bool:
        """
        Delete PDF from Firebase Storage

        Args:
            company_name: Sanitized company name
            filename: e.g., "investment-memo.pdf"

        Returns:
            True if deleted successfully, False otherwise
        """
        if not self.enabled or not self.bucket:
            return False

        try:
            blob_path = f"pdfs/{company_name}/{filename}"
            blob = self.bucket.blob(blob_path)

            if blob.exists():
                blob.delete()
                print(f"🗑️ Deleted PDF: {blob_path}")
                return True
            else:
                print(f"ℹ️ PDF not found, nothing to delete: {blob_path}")
                return False
        except Exception as e:
            print(f"❌ Failed to delete PDF: {e}")
            return False


# Global instance
firebase_storage = FirebaseStorageManager()
