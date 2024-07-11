import os
import requests
from urllib.parse import urljoin
import time
import random
import json


class PDFDownloader:
    def __init__(self, download_path, base_url):
        self.download_path = download_path
        self.base_url = base_url
        self.metadata = []
    def download_pdf(self, url, metadata):
        """Downloads a PDF from a given URL and saves it locally, along with metadata."""
        try:
            full_url = urljoin(self.base_url, url)
            response = requests.get(full_url)
            response.raise_for_status()  # Raise HTTPError for bad responses
            filename = os.path.join(self.download_path, os.path.basename(url))
            
            # Check if file already exists
            if os.path.exists(filename):
                print(f"File {filename} already exists. Skipping download.")
                
            else:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded: {filename}")
            
            # Collect metadata in the specified format
            metadata_entry = {
                "filename": filename,
                "company_name": metadata["company_name"],
                "company_code": metadata["company_code"],
                "file_timestamp": metadata["file_timestamp"],
                "document_name": metadata["document_name"]
            }
            self.metadata.append(metadata_entry)
        except requests.RequestException as e:
            print(f"Failed to download {url}: {e}")
    def save_metadata(self, file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=4)