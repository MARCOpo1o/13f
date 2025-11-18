"""
XML Parser for 13F InfoTable files.
Extracts holdings data from SEC 13F XML format.

Best Practices:
- Single Responsibility: Only parses XML
- Error Handling: Handles malformed XML gracefully
- Type Hints: Clear return types
- Reusable: Can be used standalone or as part of larger system
"""

import xml.etree.ElementTree as ET
import re
from typing import Dict, Optional


def get_namespace(root: ET.Element) -> Optional[str]:
    """
    Extract XML namespace from root tag if present.
    
    Args:
        root: XML root element
        
    Returns:
        Namespace string or None
    """
    if root.tag.startswith("{"):
        return root.tag.split("}")[0].strip("{")
    return None


def find_text(elem: ET.Element, tag: str, ns: Optional[str]) -> Optional[str]:
    """
    Find child element text with or without namespace.
    
    Args:
        elem: Parent element
        tag: Tag name to find
        ns: Namespace (optional)
        
    Returns:
        Text content or None
    """
    if ns:
        child = elem.find("{" + ns + "}" + tag)
        if child is not None and child.text is not None:
            return child.text.strip()
    
    child = elem.find(tag)
    if child is not None and child.text is not None:
        return child.text.strip()
    
    return None


def parse_13f_xml(content: str) -> Dict[str, Dict]:
    """
    Parse a 13F InfoTable XML file and return holdings data.
    
    Args:
        content: XML content as string
        
    Returns:
        Dictionary keyed by CUSIP with holding details:
        {
            'CUSIP123': {
                'issuer': 'Company Name',
                'titleOfClass': 'COM',
                'cusip': 'CUSIP123',
                'value': 1000000.0,
                'shares': 50000.0
            },
            ...
        }
        
    Raises:
        ValueError: If XML is malformed and cannot be parsed
    """
    # Ensure content is a string
    if isinstance(content, bytes):
        content = content.decode('utf-8', errors='ignore')
    
    # Clean the content
    content = content.strip()
    content = content.replace('\ufeff', '')  # Remove BOM if present
    
    # Try to fix common XML issues from SEC filings
    if '<html' in content.lower() or '<?xml-stylesheet' in content:
        # Extract just the XML if wrapped in HTML/XSLT
        match = re.search(
            r'<informationTable[^>]*>.*</informationTable>', 
            content, 
            re.DOTALL | re.IGNORECASE
        )
        if match:
            content = match.group(0)
        else:
            # Try to find the XML declaration and start from there
            xml_start = content.find('<?xml')
            if xml_start > 0:
                content = content[xml_start:]
    
    # Parse the XML
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        # Try to recover from parse errors
        print(f"Warning: XML parse error: {e}")
        print("Attempting to recover...")
        
        # Remove problematic lines
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            if '<?xml-stylesheet' not in line and '<html' not in line.lower():
                cleaned_lines.append(line)
        content = '\n'.join(cleaned_lines)
        
        try:
            root = ET.fromstring(content)
        except ET.ParseError as e:
            raise ValueError(f"Cannot parse XML: {e}")
    
    # Get namespace
    ns = get_namespace(root)
    
    # Find all infoTable elements
    if ns:
        info_table_xpath = ".//{" + ns + "}infoTable"
    else:
        info_table_xpath = ".//infoTable"
    
    positions = {}
    
    # Extract holdings from each infoTable entry
    for it in root.findall(info_table_xpath):
        # Get basic info
        issuer = find_text(it, "nameOfIssuer", ns) or ""
        title = find_text(it, "titleOfClass", ns) or ""
        cusip = find_text(it, "cusip", ns)
        
        if not cusip:
            continue  # Skip entries without CUSIP
        
        cusip = cusip.strip()
        
        # Get value (dollar value in thousands)
        value_text = find_text(it, "value", ns)
        try:
            value = float(value_text.replace(",", "")) if value_text else None
        except (ValueError, AttributeError):
            value = None
        
        # Get shares
        shares = 0.0
        if ns:
            shrs_elem = it.find("{" + ns + "}shrsOrPrnAmt")
        else:
            shrs_elem = it.find("shrsOrPrnAmt")
        
        if shrs_elem is not None:
            sshPrnamt = find_text(shrs_elem, "sshPrnamt", ns)
            if sshPrnamt:
                try:
                    shares = float(sshPrnamt.replace(",", ""))
                except (ValueError, AttributeError):
                    shares = 0.0
        
        # Store position
        positions[cusip] = {
            "issuer": issuer,
            "titleOfClass": title,
            "cusip": cusip,
            "value": value,
            "shares": shares,
        }
    
    return positions

