"""
13F Filing Comparator.
Compares two 13F filings and calculates position changes.

Best Practices:
- Single Responsibility: Only compares filings
- Type Hints: Clear function signatures
- Immutability: Doesn't modify input data
- Testable: Pure functions, no side effects
"""

from typing import Dict, List


def compare_filings(current: Dict, prior: Dict) -> List[Dict]:
    """
    Compare current and prior 13F filings to calculate position changes.
    
    Args:
        current: Dict of current positions (from parse_13f_xml)
        prior: Dict of prior positions (from parse_13f_xml)
        
    Returns:
        List of dictionaries with comparison data for each stock:
        [
            {
                'cusip': '...',
                'issuer': '...',
                'titleOfClass': '...',
                'prior_shares': 1000,
                'current_shares': 1500,
                'delta_shares': 500,
                'prior_value': 10000,
                'current_value': 15000,
                'percent_change': 50.0,
                'status': 'INCREASED'
            },
            ...
        ]
        
    Status values:
        - NEW: Position didn't exist before
        - EXITED: Position was closed
        - INCREASED: Shares increased
        - DECREASED: Shares decreased
        - UNCHANGED: Same number of shares
    """
    all_cusips = sorted(set(current.keys()) | set(prior.keys()))
    results = []
    
    # Calculate total portfolio values first
    total_current_value = sum((pos.get('value') or 0) for pos in current.values())
    total_prior_value = sum((pos.get('value') or 0) for pos in prior.values())
    
    for cusip in all_cusips:
        cur = current.get(cusip)
        prv = prior.get(cusip)
        
        # Get share counts
        cur_shares = cur["shares"] if cur else 0.0
        prv_shares = prv["shares"] if prv else 0.0
        delta_shares = cur_shares - prv_shares
        
        # Determine status
        if prv_shares == 0 and cur_shares > 0:
            status = "NEW"
        elif prv_shares > 0 and cur_shares == 0:
            status = "EXITED"
        elif delta_shares > 0:
            status = "INCREASED"
        elif delta_shares < 0:
            status = "DECREASED"
        else:
            status = "UNCHANGED"
        
        # Get company info (prefer current, fall back to prior)
        issuer = (cur or prv or {}).get("issuer", "")
        title = (cur or prv or {}).get("titleOfClass", "")
        
        # Get values
        cur_val = (cur or {}).get("value")
        prv_val = (prv or {}).get("value")
        
        # Calculate percentage change in value
        if prv_val and prv_val > 0:
            if cur_val:
                pct_change = ((cur_val - prv_val) / prv_val) * 100
            else:
                pct_change = -100.0  # Exited position
        elif cur_val and cur_val > 0:
            pct_change = None  # New position (can't calculate % from zero)
        else:
            pct_change = 0.0
            
        # Calculate portfolio percentages
        current_pct = (cur_val / total_current_value * 100) if cur_val and total_current_value else 0.0
        prior_pct = (prv_val / total_prior_value * 100) if prv_val and total_prior_value else 0.0
        change_in_portfolio_pct = current_pct - prior_pct
        
        # Build result row
        results.append({
            "cusip": cusip,
            "issuer": issuer,
            "titleOfClass": title,
            "prior_shares": int(prv_shares),
            "current_shares": int(cur_shares),
            "delta_shares": int(delta_shares),
            "prior_value": int(prv_val) if prv_val else None,
            "current_value": int(cur_val) if cur_val else None,
            "percent_change": round(pct_change, 2) if pct_change is not None else None,
            "status": status,
            "prior_percent_of_portfolio": round(prior_pct, 2),
            "current_percent_of_portfolio": round(current_pct, 2),
            "change_in_portfolio_pct": round(change_in_portfolio_pct, 2),
        })
    
    # Add TOTAL row
    results.append({
        "cusip": "TOTAL",
        "issuer": "Total Assets Under Management",
        "titleOfClass": "",
        "prior_shares": None,
        "current_shares": None,
        "delta_shares": None,
        "prior_value": int(total_prior_value),
        "current_value": int(total_current_value),
        "percent_change": round(((total_current_value - total_prior_value) / total_prior_value * 100), 2) if total_prior_value else 0.0,
        "status": "TOTAL",
        "prior_percent_of_portfolio": 100.0,
        "current_percent_of_portfolio": 100.0,
        "change_in_portfolio_pct": 0.0,
    })
    
    return results


def calculate_summary(comparison: List[Dict]) -> Dict:
    """
    Calculate summary statistics from comparison results.
    
    Args:
        comparison: List of comparison dictionaries from compare_filings
        
    Returns:
        Summary statistics dictionary:
        {
            'total_positions': 100,
            'new_positions': 10,
            'exited_positions': 5,
            'increased_positions': 30,
            'decreased_positions': 25,
            'unchanged_positions': 30,
            'total_current_value': 1000000000
        }
    """
    summary = {
        'total_positions': len(comparison),
        'new_positions': 0,
        'exited_positions': 0,
        'increased_positions': 0,
        'decreased_positions': 0,
        'unchanged_positions': 0,
        'total_current_value': 0,
    }
    
    for row in comparison:
        status = row['status']
        
        if status == 'NEW':
            summary['new_positions'] += 1
        elif status == 'EXITED':
            summary['exited_positions'] += 1
        elif status == 'INCREASED':
            summary['increased_positions'] += 1
        elif status == 'DECREASED':
            summary['decreased_positions'] += 1
        elif status == 'UNCHANGED':
            summary['unchanged_positions'] += 1
        
        if row['current_value']:
            summary['total_current_value'] += row['current_value']
    
    return summary

