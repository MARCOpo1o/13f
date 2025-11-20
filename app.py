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

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from services import SECClient, parse_13f_xml, compare_filings
from services.comparator import calculate_summary
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY

# Initialize SEC client globally to enable connection reuse and caching
sec_client = SECClient()


def login_required(f):
    """
    Decorator to protect routes requiring authentication.
    Redirects to login page if user is not authenticated.
    
    Can be bypassed in local development when:
    - DEBUG = True AND
    - DISABLE_AUTH_IN_DEV = True
    
    This never bypasses auth in production (when DEBUG=False).
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Bypass auth in local dev if flag is enabled
        if config.DEBUG and config.DISABLE_AUTH_IN_DEV:
            return f(*args, **kwargs)
        
        # Otherwise require authentication
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login with password authentication.
    
    GET: Display login form
    POST: Verify password and create session
    """
    if request.method == 'POST':
        password = request.form.get('password', '')
        
        # Verify password against secure hash (never store passwords in plaintext!)
        if check_password_hash(config.PASSWORD_HASH, password):
            session['authenticated'] = True
            session.permanent = True  # Session persists across browser restarts
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Incorrect password. Please try again.")
    
    # If already logged in, redirect to home
    if session.get('authenticated'):
        return redirect(url_for('index'))
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """
    Log out the user by clearing the session.
    """
    session.clear()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    """
    Render the home page with CIK input form.
    Requires authentication.
    
    Returns:
        HTML template with input form and examples
    """
    dev_mode_no_auth = config.DEBUG and config.DISABLE_AUTH_IN_DEV
    return render_template('index.html', 
                         examples=config.EXAMPLE_CIKS,
                         dev_mode_no_auth=dev_mode_no_auth)


@app.route('/compare', methods=['POST'])
@login_required
def compare():
    """
    Process CIK input, fetch filings, and display comparison results.
    Requires authentication.
    
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
        # Use global SEC client
        # client = SECClient()  <-- REMOVED: This was causing performance issues
        
        # Fetch filings
        current_xml, prior_xml, metadata = sec_client.get_fund_filings(cik)
        
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
        dev_mode_no_auth = config.DEBUG and config.DISABLE_AUTH_IN_DEV
        return render_template('results.html',
                             cik=cik,
                             comparison=comparison,
                             summary=summary,
                             metadata=metadata,
                             dev_mode_no_auth=dev_mode_no_auth)
    
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
        # Use global SEC client
        # client = SECClient() <-- REMOVED
        
        # Fetch filings
        current_xml, prior_xml, metadata = sec_client.get_fund_filings(cik)
        
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

