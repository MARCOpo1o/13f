"""
13F Comparison Web Application.
Flask app for comparing hedge fund 13F filings.

Architecture: MVC Pattern
- Models: services/ (SEC client, XML parser, comparator)
- Views: templates/ (HTML templates)
- Controller: This file (Flask routes)

Best Practices:
- Separation of concerns
- Error handling at every layer
- User-friendly error messages
- Input validation
- RESTful routes
"""

from flask import Flask, render_template, request, jsonify
from services import SECClient, parse_13f_xml, compare_filings
from services.comparator import calculate_summary
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY


@app.route('/')
def index():
    """
    Render the home page with CIK input form.
    
    Returns:
        HTML template with input form and examples
    """
    return render_template('index.html', examples=config.EXAMPLE_CIKS)


@app.route('/compare', methods=['POST'])
def compare():
    """
    Process CIK input, fetch filings, and display comparison results.
    
    Returns:
        HTML template with comparison results or error page
    """
    # Get CIK from form
    cik = request.form.get('cik', '').strip()
    
    # Validate CIK
    if not cik:
        return render_template('index.html', 
                             error="Please enter a CIK",
                             examples=config.EXAMPLE_CIKS)
    
    # Clean CIK (remove dashes, spaces)
    cik = cik.replace('-', '').replace(' ', '')
    
    # Validate format (should be numeric)
    if not cik.isdigit():
        return render_template('index.html',
                             error=f"Invalid CIK format: '{cik}'. CIK should be numeric.",
                             examples=config.EXAMPLE_CIKS)
    
    try:
        # Initialize SEC client
        client = SECClient()
        
        # Fetch filings
        current_xml, prior_xml, metadata = client.get_fund_filings(cik)
        
        if not current_xml or not prior_xml:
            return render_template('index.html',
                                 error=f"Could not fetch 13F filings for CIK {cik}. "
                                       f"Make sure this is a valid 13F filer.",
                                 examples=config.EXAMPLE_CIKS)
        
        # Parse XML files
        try:
            current_positions = parse_13f_xml(current_xml)
            prior_positions = parse_13f_xml(prior_xml)
        except ValueError as e:
            return render_template('index.html',
                                 error=f"Error parsing XML: {str(e)}",
                                 examples=config.EXAMPLE_CIKS)
        
        # Compare filings
        comparison = compare_filings(current_positions, prior_positions)
        summary = calculate_summary(comparison)
        
        # Render results
        return render_template('results.html',
                             cik=cik,
                             comparison=comparison,
                             summary=summary,
                             metadata=metadata)
    
    except Exception as e:
        # Catch-all for unexpected errors
        return render_template('index.html',
                             error=f"Unexpected error: {str(e)}. Please try again.",
                             examples=config.EXAMPLE_CIKS)


@app.route('/api/compare/<cik>')
def api_compare(cik):
    """
    API endpoint for programmatic access.
    Returns JSON comparison data.
    
    Args:
        cik: Central Index Key in URL
        
    Returns:
        JSON response with comparison data or error
    """
    try:
        # Initialize SEC client
        client = SECClient()
        
        # Fetch filings
        current_xml, prior_xml, metadata = client.get_fund_filings(cik)
        
        if not current_xml or not prior_xml:
            return jsonify({
                'error': f'Could not fetch 13F filings for CIK {cik}'
            }), 404
        
        # Parse XML
        current_positions = parse_13f_xml(current_xml)
        prior_positions = parse_13f_xml(prior_xml)
        
        # Compare
        comparison = compare_filings(current_positions, prior_positions)
        summary = calculate_summary(comparison)
        
        return jsonify({
            'cik': cik,
            'metadata': metadata,
            'summary': summary,
            'comparison': comparison
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return render_template('index.html',
                         error="Page not found",
                         examples=config.EXAMPLE_CIKS), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return render_template('index.html',
                         error="Server error. Please try again later.",
                         examples=config.EXAMPLE_CIKS), 500


if __name__ == '__main__':
    print("="*60)
    print("13F Comparison Web App")
    print("="*60)
    print(f"Running on: http://{config.HOST}:{config.PORT}")
    print(f"Open in browser: http://localhost:{config.PORT}")
    print("="*60)
    print()
    
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )

