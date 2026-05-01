from app import db
from datetime import datetime

class Photo(db.Model):
    __tablename__ = 'photos'

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    category    = db.Column(db.String(50), nullable=False)   # mariage, portrait, commercial, paysage, shooting
    filename    = db.Column(db.String(255), nullable=False)  # local ou Cloudinary public_id
    url         = db.Column(db.String(500))                  # URL Cloudinary (ou None si local)
    thumbnail   = db.Column(db.String(500))                  # URL thumbnail
    is_featured = db.Column(db.Boolean, default=False)       # Affichée en hero/accueil
    is_visible  = db.Column(db.Boolean, default=True)
    sort_order  = db.Column(db.Integer, default=0)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    CATEGORIES = ['mariage', 'portrait', 'commercial', 'paysage', 'shooting']

    @property
    def image_url(self):
        if self.url:
            return self.url
        from flask import url_for
        return url_for('static', filename=f'images/{self.filename}')

    @property
    def thumb_url(self):
        if self.thumbnail:
            return self.thumbnail
        return self.image_url

    def to_dict(self):
        return {
            'id':         self.id,
            'title':      self.title,
            'category':   self.category,
            'image_url':  self.image_url,
            'thumb_url':  self.thumb_url,
            'is_featured': self.is_featured,
            'sort_order': self.sort_order,
        }

    def __repr__(self):
        return f'<Photo {self.title} [{self.category}]>'
