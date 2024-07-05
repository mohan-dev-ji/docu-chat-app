# from flask import current_app as app
from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app, send_file
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from app import db
from app.models import User, PDF
from app import create_app
import os
from werkzeug.utils import secure_filename

print("Routes are being registered")

bp = Blueprint('main', __name__)

@bp.route('/upload_pdf', methods=['GET', 'POST'])
@login_required
def upload_pdf():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'pdf_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['pdf_file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            new_pdf = PDF(filename=filename, path=path, user_id=current_user.id)
            db.session.add(new_pdf)
            db.session.commit()
            flash('PDF uploaded successfully')
            return redirect(url_for('main.dashboard'))
    return render_template('upload_pdf.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'pdf'}

@bp.route('/')
@bp.route('/index')
def index():
    # print(f"Current working directory: {os.getcwd()}")
    # print(f"Template folder: {current_app.template_folder}")
    # print(f"Available templates: {os.listdir(current_app.template_folder)}")
    try:
        return render_template('index.html', title='Home')
    except Exception as e:
        current_app.logger.error(f"Error rendering index template: {str(e)}")
        return f"An error occurred: {str(e)}", 500

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user is not None:
            flash('Please use a different username.')
            return redirect(url_for('main.register'))
        user = User.query.filter_by(email=email).first()
        if user is not None:
            flash('Please use a different email address.')
            return redirect(url_for('main.register'))
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            flash('Invalid email or password')
            return redirect(url_for('main.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        return redirect(next_page)
    return render_template('login.html', title='Sign In')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'pdf_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['pdf_file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            new_pdf = PDF(filename=filename, path=path, user_id=current_user.id)
            db.session.add(new_pdf)
            db.session.commit()
            flash('PDF uploaded successfully')
            return redirect(url_for('main.dashboard'))
    
    user_pdfs = PDF.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', title='Dashboard', pdfs=user_pdfs)

@bp.route('/delete_pdf/<int:pdf_id>', methods=['POST'])
@login_required
def delete_pdf(pdf_id):
    pdf = PDF.query.get_or_404(pdf_id)
    if pdf.user_id != current_user.id:
        flash('You do not have permission to delete this PDF.')
        return redirect(url_for('main.dashboard'))
    
    # Delete the file from the filesystem
    if os.path.exists(pdf.path):
        os.remove(pdf.path)
    
    # Delete the database entry
    db.session.delete(pdf)
    db.session.commit()
    
    flash('PDF deleted successfully.')
    return redirect(url_for('main.dashboard'))

@bp.route('/pdf/<int:pdf_id>')
@login_required
def serve_pdf(pdf_id):
    pdf = PDF.query.get_or_404(pdf_id)
    if pdf.user_id != current_user.id:
        flash('You do not have permission to delete this PDF.')
        return redirect(url_for('main.dashboard'))
    return send_file(pdf.path, mimetype='application/pdf')

