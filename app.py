"""
AshvPermission - Flask Web Application
Permission Letter Generator with Roll Number to Department Mapping
Supports UG (First Year & Senior) and PG (MBA/MCA) students
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, Response
from functools import wraps
from datetime import datetime, timezone, timedelta
from department_mapper import DepartmentMapper, parse_roll_numbers
from config import (
    DEFAULT_SUBJECT, DEFAULT_BODY, DEFAULT_PLACE, HEADER_CONFIG,
    UG_DEPARTMENT_CODES, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
)
from models import db, Letter, RollNumber

app = Flask(__name__)
app.secret_key = 'ashvpermission_secret_key_change_in_production'

IST = timezone(timedelta(hours=5, minutes=30))

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

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
        'current_year': datetime.now(IST).year,
        'is_admin': session.get('is_admin', False)
    }

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Please log in as an administrator to access this page.', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    """Home page with letter creation form"""
    defaults = get_defaults()
    return render_template('index.html',
        today=datetime.now(IST).strftime('%Y-%m-%d'),
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
            formatted_date = datetime.now(IST).strftime('%B %d, %Y')
    except:
        formatted_date = datetime.now(IST).strftime('%B %d, %Y')
    
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
    # Save letter to database
    new_letter = Letter(
        date=letter_data['date'],
        place=letter_data['place'],
        to_address=letter_data['to'],
        subject=letter_data['subject'],
        body=letter_data['body']
    )
    db.session.add(new_letter)
    db.session.commit()
    
    # Save roll numbers
    for dept, info in summary['departments'].items():
        for roll in info['roll_numbers']:
            rn = RollNumber(roll_no=roll, letter_id=new_letter.id)
            db.session.add(rn)
    db.session.commit()

    # Add reference number to letter_data for templates
    letter_data['reference_no'] = new_letter.reference_no
    
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
    
    timestamp = datetime.now(IST).strftime('%Y%m%d_%H%M%S')
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

# --- ADMIN ROUTES ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'admin':
            session['is_admin'] = True
            flash('Admin logged in successfully.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            
    return render_template('admin/login.html', header=get_header_config())

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    letters = Letter.query.order_by(
        db.case(
            (Letter.status == 'pending', 0),
            else_=1
        ),
        Letter.created_at.desc()
    ).all()
    return render_template('admin/dashboard.html', letters=letters, header=get_header_config())

@app.route('/admin/search')
@admin_required
def admin_search():
    query_roll = request.args.get('roll_no', '').strip().upper()
    results = []
    
    if query_roll:
        # Find all roll numbers that match (exact match)
        roll_records = RollNumber.query.filter_by(roll_no=query_roll).all()
        
        # Get associated letters, ordered by date
        for record in roll_records:
            if record.letter:
                results.append(record.letter)
                
        # Sort by date descending
        results.sort(key=lambda x: x.date, reverse=True)
        
    return render_template('admin/search.html', 
                          query_roll=query_roll, 
                          results=results, 
                          header=get_header_config())

@app.route('/admin/letter/<int:letter_id>')
@admin_required
def admin_letter_detail(letter_id):
    letter = Letter.query.get_or_404(letter_id)
    return render_template('admin/letter_detail.html', letter=letter, header=get_header_config())

@app.route('/admin/letter/<int:letter_id>/print')
@admin_required
def admin_print_letter(letter_id):
    letter = Letter.query.get_or_404(letter_id)
    
    letter_data = {
        'date': letter.date,
        'place': letter.place,
        'to': letter.to_address,
        'subject': letter.subject,
        'body': letter.body,
        'reference_no': letter.reference_no
    }
    
    roll_numbers = [r.roll_no for r in letter.roll_numbers]
    summary = mapper.get_unified_summary(roll_numbers)
    
    return render_template('letter.html',
        header=get_header_config(),
        letter=letter_data,
        summary=summary
    )

@app.route('/admin/letter/<int:letter_id>/verify', methods=['POST'])
@admin_required
def admin_verify_letter(letter_id):
    letter = Letter.query.get_or_404(letter_id)
    letter.status = 'verified'
    db.session.commit()
    flash(f'Letter {letter.reference_no} marked as verified.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/letter/<int:letter_id>/reject', methods=['POST'])
@admin_required
def admin_reject_letter(letter_id):
    letter = Letter.query.get_or_404(letter_id)
    letter.status = 'rejected'
    db.session.commit()
    flash(f'Letter {letter.reference_no} marked as rejected.', 'warning')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/verified-dates')
@admin_required
def admin_verified_dates():
    # Fetch all letters that are verified
    verified_letters = Letter.query.filter_by(status='verified').order_by(Letter.date.desc()).all()
    dates_data = {}
    for letter in verified_letters:
        d = letter.date
        if d not in dates_data:
            dates_data[d] = set()
        for r in letter.roll_numbers:
            dates_data[d].add(r.roll_no)
            
    # Sort the dates for display if necessary
    sorted_dates = sorted(dates_data.keys(), reverse=True)
    
    return render_template('admin/verified_dates.html', dates_data=dates_data, sorted_dates=sorted_dates, header=get_header_config())


if __name__ == '__main__':
    print("=" * 50)
    print("🚀 AshvPermission - Permission Letter Generator")
    print("=" * 50)
    print("Starting Flask server...")
    print("Open http://127.0.0.1:5000 in your browser")
    print("=" * 50)
    app.run(debug=True, port=5000)
