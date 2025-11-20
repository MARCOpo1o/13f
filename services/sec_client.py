"""
SEC EDGAR API Client.
Handles all interactions with the SEC's official data APIs.

Best Practices:
- Single Responsibility: Only handles SEC API communication
- Error Handling: Graceful failures with informative messages
- Rate Limiting: Respects SEC's 10 requests/second limit
- Type Hints: Clear function signatures
"""

import time
import requests
from typing import List, Dict, Optional
import sys
import os
from functools import lru_cache

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class SECClient:
    """
    Client for interacting with SEC EDGAR APIs.
    
    Attributes:
        session: Persistent HTTP session for efficient requests
        request_count: Track requests for rate limiting
        last_request_time: Track time for rate limiting
    """
    
    def __init__(self):
        """Initialize SEC client with proper headers and rate limiting."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.SEC_USER_AGENT,
            'Accept': '*/*'
        })
        self.request_count = 0
        self.last_request_time = time.time()
    
    def _rate_limit(self) -> None:
        """
        Enforce SEC rate limit of 10 requests per second.
        Sleeps if necessary to stay within limits.
        """
        self.request_count += 1
        
        if self.request_count >= config.SEC_RATE_LIMIT_REQUESTS:
            elapsed = time.time() - self.last_request_time
            
            if elapsed < config.SEC_RATE_LIMIT_PERIOD:
                sleep_time = config.SEC_RATE_LIMIT_PERIOD - elapsed
                time.sleep(sleep_time)
            
            self.request_count = 0
            self.last_request_time = time.time()
    
    def get_company_submissions(self, cik: str) -> Optional[Dict]:
        """
        Get all submissions for a company by CIK.
        
        Args:
            cik: Central Index Key (10-digit string)
            
        Returns:
            JSON response with filing history, or None if error
            
        Raises:
            ValueError: If CIK format is invalid
        """
        # Validate and pad CIK
        try:
            cik_padded = str(cik).zfill(10)
        except ValueError:
            raise ValueError(f"Invalid CIK format: {cik}")
        
        url = f"{config.SEC_API_BASE_URL}/submissions/CIK{cik_padded}.json"
        
        self._rate_limit()
        
        try:
            response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching submissions for CIK {cik}: {e}")
            return None
    
    def get_latest_13f_filings(self, cik: str, count: int = 2) -> List[Dict]:
        """
        Get the latest N 13F-HR filings for a CIK.
        
        Args:
            cik: Central Index Key
            count: Number of filings to retrieve (default: 2)
            
        Returns:
            List of filing metadata dictionaries
        """
        submissions = self.get_company_submissions(cik)
        
        if not submissions:
            return []
        
        filings = submissions.get('filings', {}).get('recent', {})
        
        filing_list = []
        forms = filings.get('form', [])
        
        for i in range(len(forms)):
            if forms[i] == '13F-HR':
                filing_list.append({
                    'accessionNumber': filings['accessionNumber'][i],
                    'filingDate': filings['filingDate'][i],
                    'reportDate': filings['reportDate'][i],
                })
                
                if len(filing_list) >= count:
                    break
        
        return filing_list
    
    def get_infotable_url(self, cik: str, accession_number: str) -> str:
        """
        Dynamically find the InfoTable XML URL for a specific filing.
        
        Args:
            cik: Central Index Key
            accession_number: SEC accession number (with dashes)
            
        Returns:
            Full URL to the InfoTable XML file
        """
        cik_clean = str(cik).lstrip('0')
        accession_clean = accession_number.replace('-', '')
        
        base_url = f"{config.SEC_ARCHIVES_BASE_URL}/{cik_clean}/{accession_clean}"
        
        # Try to find the correct XML file from the index
        try:
            index_url = f"{base_url}/index.json"
            self._rate_limit()
            
            response = self.session.get(index_url, timeout=config.REQUEST_TIMEOUT)
            if response.status_code == 200:
                files = response.json().get('directory', {}).get('item', [])
                
                # Strategy 1: Look for 'infotable.xml' or similar
                for file in files:
                    name = file['name']
                    if name.lower() == 'infotable.xml':
                        return f"{base_url}/{name}"
                
                # Strategy 2: Look for any XML that isn't the primary document
                # (Primary doc is usually the cover page)
                for file in files:
                    name = file['name']
                    if name.endswith('.xml') and 'primary' not in name.lower() and 'cover' not in name.lower():
                        return f"{base_url}/{name}"
                        
                # Strategy 3: If only one XML exists, use it
                xml_files = [f['name'] for f in files if f['name'].endswith('.xml')]
                if len(xml_files) == 1:
                    return f"{base_url}/{xml_files[0]}"

        except Exception as e:
            print(f"Warning: Could not resolve dynamic URL for {accession_number}: {e}")
        
        # Fallback: Default to standard naming
        return f"{base_url}/infotable.xml"
    
    def download_xml(self, url: str) -> Optional[str]:
        """
        Download XML content from a URL.
        
        Args:
            url: Full URL to XML file
            
        Returns:
            XML content as string, or None if error
        """
        self._rate_limit()
        
        try:
            response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error downloading XML from {url}: {e}")
            return None
    
    @lru_cache(maxsize=32)
    def get_fund_filings(self, cik: str) -> tuple[Optional[str], Optional[str], Optional[Dict]]:
        """
        Get the latest two 13F InfoTable XML files for a fund.
        Cached to improve performance for repeated searches.
        
        This is the main method that combines all steps:
        1. Get latest 2 filing metadata
        2. Download both InfoTable XML files
        3. Return the XML content and metadata
        
        Args:
            cik: Central Index Key of the fund
            
        Returns:
            Tuple of (current_xml, prior_xml, metadata)
            Returns (None, None, None) if any step fails
        """
        # Get filing metadata
        filings = self.get_latest_13f_filings(cik, count=2)
        
        if len(filings) < 2:
            print(f"Error: Found only {len(filings)} filings, need 2")
            return None, None, None
        
        # Get XML URLs
        current_url = self.get_infotable_url(cik, filings[0]['accessionNumber'])
        prior_url = self.get_infotable_url(cik, filings[1]['accessionNumber'])
        
        # Download XML files
        current_xml = self.download_xml(current_url)
        prior_xml = self.download_xml(prior_url)
        
        if not current_xml or not prior_xml:
            print("Error: Failed to download XML files")
            return None, None, None
        
        # Prepare metadata
        metadata = {
            'current_date': filings[0]['filingDate'],
            'prior_date': filings[1]['filingDate'],
            'current_report_date': filings[0]['reportDate'],
            'prior_report_date': filings[1]['reportDate'],
        }
        
        return current_xml, prior_xml, metadata

