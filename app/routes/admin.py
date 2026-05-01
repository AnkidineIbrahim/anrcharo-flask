from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, jsonify, current_app)
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.models.photo import Photo
from app.models.models import Reservation, Testimonial, Setting
from app.utils.upload import (save_image_local, save_image_cloudinary,
                               delete_image_local, delete_image_cloudinary,
                               allowed_file)
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

# ════════════════════════════════════════════════════
#  AUTH
# ════════════════════════════════════════════════════
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=True)
            next_page = request.args.get('next')
            flash('Bienvenue dans votre espace admin !', 'success')
            return redirect(next_page or url_for('admin.dashboard'))
        flash('Identifiants incorrects.', 'danger')

    return render_template('admin/login.html')

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous êtes déconnecté.', 'info')
    return redirect(url_for('admin.login'))

# ════════════════════════════════════════════════════
#  DASHBOARD
# ════════════════════════════════════════════════════
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    stats = {
        'photos':       Photo.query.count(),
        'reservations': Reservation.query.count(),
        'new_resa':     Reservation.query.filter_by(status='nouveau').count(),
        'testimonials': Testimonial.query.count(),
    }
    recent_resa = Reservation.query.order_by(Reservation.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, recent_resa=recent_resa)

# ════════════════════════════════════════════════════
#  PHOTOS
# ════════════════════════════════════════════════════
@admin_bp.route('/photos')
@login_required
def photos():
    cat = request.args.get('cat', 'all')
    query = Photo.query
    if cat != 'all':
        query = query.filter_by(category=cat)
    photos = query.order_by(Photo.sort_order, Photo.created_at.desc()).all()
    return render_template('admin/photos.html',
        photos=photos,
        categories=Photo.CATEGORIES,
        current_cat=cat,
    )

@admin_bp.route('/photos/upload', methods=['GET', 'POST'])
@login_required
def photo_upload():
    if request.method == 'POST':
        files     = request.files.getlist('photos')
        category  = request.form.get('category', 'portrait')
        title     = request.form.get('title', '').strip()
        is_featured = request.form.get('is_featured') == 'on'

        if not files or not files[0].filename:
            flash('Aucun fichier sélectionné.', 'danger')
            return redirect(request.url)

        uploaded = 0
        for f in files:
            if not allowed_file(f.filename):
                continue
            try:
                auto_title = title or f.filename.rsplit('.', 1)[0].replace('-', ' ').replace('_', ' ').title()

                if current_app.config['USE_CLOUDINARY']:
                    import cloudinary
                    cloudinary.config(
                        cloud_name=current_app.config['CLOUDINARY_CLOUD_NAME'],
                        api_key=current_app.config['CLOUDINARY_API_KEY'],
                        api_secret=current_app.config['CLOUDINARY_API_SECRET'],
                    )
                    pub_id, url, thumb = save_image_cloudinary(f)
                    photo = Photo(title=auto_title, category=category,
                                  filename=pub_id, url=url, thumbnail=thumb,
                                  is_featured=is_featured)
                else:
                    filename = save_image_local(f)
                    photo = Photo(title=auto_title, category=category,
                                  filename=filename, is_featured=is_featured)

                db.session.add(photo)
                uploaded += 1
            except Exception as e:
                flash(f'Erreur pour {f.filename} : {e}', 'danger')

        db.session.commit()
        flash(f'{uploaded} photo(s) uploadée(s) avec succès !', 'success')
        return redirect(url_for('admin.photos'))

    return render_template('admin/photo_upload.html', categories=Photo.CATEGORIES)

@admin_bp.route('/photos/<int:photo_id>/edit', methods=['GET', 'POST'])
@login_required
def photo_edit(photo_id):
    photo = Photo.query.get_or_404(photo_id)

    if request.method == 'POST':
        photo.title       = request.form.get('title', photo.title).strip()
        photo.category    = request.form.get('category', photo.category)
        photo.description = request.form.get('description', '').strip()
        photo.is_featured = request.form.get('is_featured') == 'on'
        photo.is_visible  = request.form.get('is_visible') == 'on'
        photo.sort_order  = int(request.form.get('sort_order', 0))
        db.session.commit()
        flash('Photo mise à jour.', 'success')
        return redirect(url_for('admin.photos'))

    return render_template('admin/photo_edit.html', photo=photo, categories=Photo.CATEGORIES)

@admin_bp.route('/photos/<int:photo_id>/delete', methods=['POST'])
@login_required
def photo_delete(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if photo.url:
        delete_image_cloudinary(photo.filename)
    else:
        delete_image_local(photo.filename)
    db.session.delete(photo)
    db.session.commit()
    flash('Photo supprimée.', 'success')
    return redirect(url_for('admin.photos'))

@admin_bp.route('/photos/<int:photo_id>/toggle', methods=['POST'])
@login_required
def photo_toggle(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    photo.is_visible = not photo.is_visible
    db.session.commit()
    return jsonify({'visible': photo.is_visible})

# ════════════════════════════════════════════════════
#  RESERVATIONS
# ════════════════════════════════════════════════════
@admin_bp.route('/reservations')
@login_required
def reservations():
    status = request.args.get('status', 'all')
    query  = Reservation.query
    if status != 'all':
        query = query.filter_by(status=status)
    resas = query.order_by(Reservation.created_at.desc()).all()
    return render_template('admin/reservations.html',
        reservations=resas,
        current_status=status,
        statuses=Reservation.STATUS,
    )

@admin_bp.route('/reservations/<int:resa_id>')
@login_required
def reservation_detail(resa_id):
    resa = Reservation.query.get_or_404(resa_id)
    return render_template('admin/reservation_detail.html', resa=resa,
                           statuses=Reservation.STATUS)

@admin_bp.route('/reservations/<int:resa_id>/update', methods=['POST'])
@login_required
def reservation_update(resa_id):
    resa = Reservation.query.get_or_404(resa_id)
    resa.status     = request.form.get('status', resa.status)
    resa.note_admin = request.form.get('note_admin', '').strip()
    resa.updated_at = datetime.utcnow()
    db.session.commit()
    flash('Réservation mise à jour.', 'success')
    return redirect(url_for('admin.reservation_detail', resa_id=resa_id))

@admin_bp.route('/reservations/<int:resa_id>/delete', methods=['POST'])
@login_required
def reservation_delete(resa_id):
    resa = Reservation.query.get_or_404(resa_id)
    db.session.delete(resa)
    db.session.commit()
    flash('Réservation supprimée.', 'success')
    return redirect(url_for('admin.reservations'))

# ════════════════════════════════════════════════════
#  TÉMOIGNAGES
# ════════════════════════════════════════════════════
@admin_bp.route('/testimonials')
@login_required
def testimonials():
    items = Testimonial.query.order_by(Testimonial.sort_order, Testimonial.created_at.desc()).all()
    return render_template('admin/testimonials.html', testimonials=items)

@admin_bp.route('/testimonials/add', methods=['GET', 'POST'])
@login_required
def testimonial_add():
    if request.method == 'POST':
        t = Testimonial(
            author_name = request.form.get('author_name', '').strip(),
            author_role = request.form.get('author_role', '').strip(),
            content     = request.form.get('content', '').strip(),
            rating      = int(request.form.get('rating', 5)),
            is_visible  = request.form.get('is_visible') == 'on',
            sort_order  = int(request.form.get('sort_order', 0)),
        )
        db.session.add(t)
        db.session.commit()
        flash('Témoignage ajouté.', 'success')
        return redirect(url_for('admin.testimonials'))
    return render_template('admin/testimonial_form.html', t=None)

@admin_bp.route('/testimonials/<int:t_id>/edit', methods=['GET', 'POST'])
@login_required
def testimonial_edit(t_id):
    t = Testimonial.query.get_or_404(t_id)
    if request.method == 'POST':
        t.author_name = request.form.get('author_name', '').strip()
        t.author_role = request.form.get('author_role', '').strip()
        t.content     = request.form.get('content', '').strip()
        t.rating      = int(request.form.get('rating', 5))
        t.is_visible  = request.form.get('is_visible') == 'on'
        t.sort_order  = int(request.form.get('sort_order', 0))
        db.session.commit()
        flash('Témoignage mis à jour.', 'success')
        return redirect(url_for('admin.testimonials'))
    return render_template('admin/testimonial_form.html', t=t)

@admin_bp.route('/testimonials/<int:t_id>/delete', methods=['POST'])
@login_required
def testimonial_delete(t_id):
    t = Testimonial.query.get_or_404(t_id)
    db.session.delete(t)
    db.session.commit()
    flash('Témoignage supprimé.', 'success')
    return redirect(url_for('admin.testimonials'))

# ════════════════════════════════════════════════════
#  PARAMÈTRES
# ════════════════════════════════════════════════════
@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        for key in request.form:
            s = Setting.query.filter_by(key=key).first()
            if s:
                s.value = request.form[key].strip()
        db.session.commit()
        flash('Paramètres sauvegardés.', 'success')
        return redirect(url_for('admin.settings'))

    all_settings = Setting.query.order_by(Setting.key).all()
    return render_template('admin/settings.html', settings=all_settings)

# ════════════════════════════════════════════════════
#  COMPTE
# ════════════════════════════════════════════════════
@admin_bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'change_password':
            current_pw  = request.form.get('current_password')
            new_pw      = request.form.get('new_password')
            confirm_pw  = request.form.get('confirm_password')

            if not current_user.check_password(current_pw):
                flash('Mot de passe actuel incorrect.', 'danger')
            elif new_pw != confirm_pw:
                flash('Les mots de passe ne correspondent pas.', 'danger')
            elif len(new_pw) < 8:
                flash('Le mot de passe doit contenir au moins 8 caractères.', 'danger')
            else:
                current_user.set_password(new_pw)
                db.session.commit()
                flash('Mot de passe mis à jour.', 'success')

        elif action == 'change_email':
            new_email = request.form.get('new_email', '').strip()
            if new_email:
                current_user.email = new_email
                db.session.commit()
                flash('Email mis à jour.', 'success')

    return render_template('admin/account.html')
