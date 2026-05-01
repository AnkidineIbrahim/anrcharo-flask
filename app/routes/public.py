from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app import db
from app.models.photo import Photo
from app.models.models import Reservation, Testimonial, Setting
from datetime import date

public_bp = Blueprint('public', __name__)

# ─── HOME ───────────────────────────────────────────────────────
@public_bp.route('/')
def index():
    hero_photos   = Photo.query.filter_by(is_featured=True, is_visible=True)\
                               .order_by(Photo.sort_order).limit(1).all()
    testimonials  = Testimonial.query.filter_by(is_visible=True)\
                                     .order_by(Testimonial.sort_order).limit(3).all()
    portfolio_cats = Photo.CATEGORIES
    settings = {s.key: s.value for s in Setting.query.all()}

    return render_template('public/index.html',
        hero_photos=hero_photos,
        testimonials=testimonials,
        portfolio_cats=portfolio_cats,
        settings=settings,
    )

# ─── PORTFOLIO (JSON pour filtre AJAX) ──────────────────────────
@public_bp.route('/portfolio')
def portfolio():
    cat = request.args.get('cat', 'all')
    query = Photo.query.filter_by(is_visible=True)
    if cat != 'all':
        query = query.filter_by(category=cat)
    photos = query.order_by(Photo.sort_order, Photo.created_at.desc()).all()
    return jsonify([p.to_dict() for p in photos])

# ─── RESERVATION ────────────────────────────────────────────────
@public_bp.route('/reserver', methods=['POST'])
def reserver():
    data = request.form
    try:
        date_event = None
        if data.get('date'):
            date_event = date.fromisoformat(data['date'])

        reservation = Reservation(
            prenom     = data.get('prenom', '').strip(),
            nom        = data.get('nom', '').strip(),
            email      = data.get('email', '').strip(),
            telephone  = data.get('telephone', '').strip(),
            type_prest = data.get('type', '').strip(),
            date_event = date_event,
            lieu       = data.get('lieu', '').strip(),
            message    = data.get('message', '').strip(),
            status     = 'nouveau',
        )

        if not reservation.prenom or not reservation.email or not reservation.type_prest:
            return jsonify({'success': False, 'message': 'Veuillez remplir tous les champs obligatoires.'}), 400

        db.session.add(reservation)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Votre demande a bien été envoyée !'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Une erreur est survenue. Veuillez réessayer.'}), 500
