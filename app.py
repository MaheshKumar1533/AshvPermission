"""
AshvPermission - Flask Web Application
Permission Letter Generator with Roll Number to Department Mapping
Supports UG (First Year & Senior) and PG (MBA/MCA) students
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, Response
from datetime import datetime
from department_mapper import DepartmentMapper, parse_roll_numbers
from config import (
    DEFAULT_SUBJECT, DEFAULT_BODY, DEFAULT_PLACE, HEADER_CONFIG,
    UG_DEPARTMENT_CODES
)

app = Flask(__name__)
app.secret_key = 'ashvpermission_secret_key_change_in_production'

# Initialize mapper
mapper = DepartmentMapper()


def get_header_config():
    """Get header config from session or default"""
    return session.get('header_config', HEADER_CONFIG.copy())


def get_defaults():
    """Get default values from session or config"""
    return {
        'subject': session.get('default_subject', DEFAULT_SUBJECT),
        'body': session.get('default_body', DEFAULT_BODY),
        'place': session.get('default_place', DEFAULT_PLACE)
    }


@app.context_processor
def inject_globals():
    """Inject global variables into all templates"""
    return {
        'current_year': datetime.now().year
    }


@app.route('/')
def index():
    """Home page with letter creation form"""
    defaults = get_defaults()
    return render_template('index.html',
        today=datetime.now().strftime('%Y-%m-%d'),
        default_place=defaults['place'],
        default_subject=defaults['subject'],
        default_body=defaults['body']
    )


@app.route('/preview-mapping', methods=['POST'])
def preview_mapping():
    """AJAX endpoint to preview department mapping"""
    data = request.get_json()
    
    # Handle unified roll numbers input
    roll_numbers = parse_roll_numbers(data.get('roll_numbers', ''))
    
    summary = mapper.get_unified_summary(roll_numbers)
    
    return jsonify(summary)


@app.route('/generate', methods=['POST'])
def generate():
    """Generate the permission letter"""
    # Get form data
    date_str = request.form.get('date', '')
    place = request.form.get('place', DEFAULT_PLACE)
    to = request.form.get('to', 'The Principal/Head of Department')
    subject = request.form.get('subject', '') or DEFAULT_SUBJECT
    body = request.form.get('body', '') or DEFAULT_BODY
    
    # Get unified roll numbers
    roll_numbers = parse_roll_numbers(request.form.get('roll_numbers', ''))
    
    # Validate
    if not roll_numbers:
        flash('Please enter at least one roll number', 'warning')
        return redirect(url_for('index'))
    
    # Parse date
    try:
        if date_str:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%B %d, %Y')
        else:
            formatted_date = datetime.now().strftime('%B %d, %Y')
    except:
        formatted_date = datetime.now().strftime('%B %d, %Y')
    
    # Get summary with unified approach
    summary = mapper.get_unified_summary(roll_numbers)
    
    # Store in session for download
    letter_data = {
        'date': formatted_date,
        'place': place,
        'to': to,
        'subject': subject,
        'body': body
    }
    session['letter_data'] = letter_data
    session['summary'] = summary
    
    return render_template('letter.html',
        header=get_header_config(),
        letter=letter_data,
        summary=summary
    )


@app.route('/download-html')
def download_html():
    """Download the letter as HTML file"""
    letter_data = session.get('letter_data')
    summary = session.get('summary')
    
    if not letter_data or not summary:
        flash('No letter data found. Please generate a letter first.', 'warning')
        return redirect(url_for('index'))
    
    html_content = render_template('letter_download.html',
        header=get_header_config(),
        letter=letter_data,
        summary=summary
    )
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'permission_letter_{timestamp}.html'
    
    return Response(
        html_content,
        mimetype='text/html',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )


@app.route('/settings')
def settings():
    """Settings page"""
    defaults = get_defaults()
    return render_template('settings.html',
        header=get_header_config(),
        default_place=defaults['place'],
        default_subject=defaults['subject'],
        default_body=defaults['body'],
        dept_codes=UG_DEPARTMENT_CODES
    )


@app.route('/save-settings', methods=['POST'])
def save_settings():
    """Save settings to session"""
    # Save header config
    session['header_config'] = {
        'institution_name': request.form.get('institution_name', HEADER_CONFIG['institution_name']),
        'institution_address': request.form.get('institution_address', HEADER_CONFIG['institution_address']),
        'institution_city': request.form.get('institution_city', HEADER_CONFIG['institution_city']),
        'institution_contact': request.form.get('institution_contact', HEADER_CONFIG['institution_contact']),
    }
    
    # Save defaults
    session['default_place'] = request.form.get('default_place', DEFAULT_PLACE)
    session['default_subject'] = request.form.get('default_subject', DEFAULT_SUBJECT)
    session['default_body'] = request.form.get('default_body', DEFAULT_BODY)
    
    flash('Settings saved successfully!', 'success')
    return redirect(url_for('settings'))


if __name__ == '__main__':
    print("=" * 50)
    print("🚀 AshvPermission - Permission Letter Generator")
    print("=" * 50)
    print("Starting Flask server...")
    print("Open http://127.0.0.1:5000 in your browser")
    print("=" * 50)
    app.run(debug=True, port=5000)
