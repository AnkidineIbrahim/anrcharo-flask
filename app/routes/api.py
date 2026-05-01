from flask import Blueprint, jsonify, request
from flask_login import login_required
from app import db
from app.models.photo import Photo

api_bp = Blueprint('api', __name__)

@api_bp.route('/photos')
def get_photos():
    cat = request.args.get('cat', 'all')
    query = Photo.query.filter_by(is_visible=True)
    if cat != 'all':
        query = query.filter_by(category=cat)
    photos = query.order_by(Photo.sort_order, Photo.created_at.desc()).all()
    return jsonify([p.to_dict() for p in photos])

@api_bp.route('/photos/reorder', methods=['POST'])
@login_required
def reorder_photos():
    data = request.get_json()
    for item in data.get('order', []):
        p = Photo.query.get(item['id'])
        if p:
            p.sort_order = item['order']
    db.session.commit()
    return jsonify({'success': True})
