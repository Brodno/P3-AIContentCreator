"""
Google Drive Loader - Read context files from Google Drive
Supports both local files (development) and Google Drive (production)
"""
import os
import json
import streamlit as st
from pathlib import Path

# Try to import Google Drive API (optional for local development)
try:
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False
    print("⚠️ Google Drive API not available - using local files only")

class DriveLoader:
    """
    Context loader that works with both local files and Google Drive
    """

    def __init__(self):
        self.use_drive = False
        self.service = None
        self.folder_id = None

        # Check if running on Streamlit Cloud (secrets available)
        if hasattr(st, 'secrets') and 'google_drive' in st.secrets:
            self._init_drive()
        else:
            print("📁 Using local files (development mode)")

    def _init_drive(self):
        """Initialize Google Drive API connection"""
        if not GOOGLE_DRIVE_AVAILABLE:
            print("❌ Google Drive API not installed")
            return

        try:
            # Get credentials from Streamlit secrets
            creds_dict = dict(st.secrets['google_drive'])
            self.folder_id = st.secrets['drive_folder_id']

            # Create credentials
            SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
            creds = service_account.Credentials.from_service_account_info(
                creds_dict, scopes=SCOPES)

            # Build service
            self.service = build('drive', 'v3', credentials=creds)
            self.use_drive = True
            print("✅ Google Drive API initialized")

        except Exception as e:
            print(f"❌ Failed to init Google Drive: {e}")
            self.use_drive = False

    def read_file(self, relative_path):
        """
        Read file from Google Drive or local filesystem

        Args:
            relative_path: Path relative to project root (e.g. "_KONTEKST/persona.md")

        Returns:
            str: File content
        """
        if self.use_drive:
            return self._read_from_drive(relative_path)
        else:
            return self._read_from_local(relative_path)

    def _read_from_drive(self, relative_path):
        """Read file from Google Drive"""
        try:
            # Find file in Drive
            file_id = self._find_file_in_drive(relative_path)

            if not file_id:
                raise FileNotFoundError(f"File not found in Drive: {relative_path}")

            # Download file content
            request = self.service.files().get_media(fileId=file_id)
            content = request.execute()

            return content.decode('utf-8')

        except Exception as e:
            print(f"❌ Error reading from Drive ({relative_path}): {e}")
            # Fallback to local
            return self._read_from_local(relative_path)

    def _find_file_in_drive(self, relative_path):
        """Find file ID in Google Drive by path"""
        try:
            # Split path into parts
            parts = relative_path.replace('\\', '/').split('/')

            current_folder_id = self.folder_id

            # Navigate through folders
            for i, part in enumerate(parts):
                is_last = (i == len(parts) - 1)

                # Search in current folder
                if is_last:
                    # It's a file
                    query = f"name='{part}' and '{current_folder_id}' in parents and trashed=false"
                    mime_type = None
                else:
                    # It's a folder
                    query = f"name='{part}' and '{current_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
                    mime_type = 'application/vnd.google-apps.folder'

                results = self.service.files().list(
                    q=query,
                    fields='files(id, name)',
                    pageSize=1
                ).execute()

                files = results.get('files', [])

                if not files:
                    return None

                if is_last:
                    return files[0]['id']
                else:
                    current_folder_id = files[0]['id']

            return None

        except Exception as e:
            print(f"❌ Error finding file in Drive: {e}")
            return None

    def _read_from_local(self, relative_path):
        """Read file from local filesystem"""
        # Try multiple base paths (for different environments)
        base_paths = [
            Path(__file__).parent.parent.parent.parent,  # Project root (4 levels up)
            Path.cwd(),  # Current working directory
            Path.cwd().parent,
        ]

        for base_path in base_paths:
            file_path = base_path / relative_path
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()

        raise FileNotFoundError(f"File not found locally: {relative_path}")

    def list_files(self, folder_path=""):
        """
        List files in a folder

        Args:
            folder_path: Path relative to project root (e.g. "_KONTEKST")

        Returns:
            list: List of filenames
        """
        if self.use_drive:
            return self._list_files_in_drive(folder_path)
        else:
            return self._list_files_local(folder_path)

    def _list_files_in_drive(self, folder_path):
        """List files in Google Drive folder"""
        try:
            folder_id = self._find_file_in_drive(folder_path) if folder_path else self.folder_id

            if not folder_id:
                return []

            results = self.service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields='files(id, name, mimeType)',
                pageSize=100
            ).execute()

            files = results.get('files', [])
            return [f['name'] for f in files if f['mimeType'] != 'application/vnd.google-apps.folder']

        except Exception as e:
            print(f"❌ Error listing files in Drive: {e}")
            return []

    def _list_files_local(self, folder_path):
        """List files in local folder"""
        base_paths = [
            Path(__file__).parent.parent.parent.parent,
            Path.cwd(),
        ]

        for base_path in base_paths:
            folder = base_path / folder_path if folder_path else base_path
            if folder.exists() and folder.is_dir():
                return [f.name for f in folder.iterdir() if f.is_file()]

        return []


# Global instance
_loader = None

def get_loader():
    """Get global DriveLoader instance"""
    global _loader
    if _loader is None:
        _loader = DriveLoader()
    return _loader


# Convenience functions
def read_context_file(filename):
    """Read file from _KONTEKST folder"""
    loader = get_loader()
    return loader.read_file(f"_KONTEKST/{filename}")


def read_team_file(filename):
    """Read file from _ZESPOL folder"""
    loader = get_loader()
    return loader.read_file(f"_ZESPOL/{filename}")


def read_index_file():
    """Read INDEX_POSTOW.md"""
    loader = get_loader()
    return loader.read_file("MARKETING/05_PUBLIKACJE/INDEX_POSTOW.md")


# Test
if __name__ == "__main__":
    loader = DriveLoader()

    print("\n📁 Testing file read...")
    try:
        content = loader.read_file("_KONTEKST/persona.md")
        print(f"✅ Read {len(content)} characters from persona.md")
        print(f"First 100 chars: {content[:100]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
