from app import db
from datetime import datetime

# ─── RESERVATION ────────────────────────────────────────────────
class Reservation(db.Model):
    __tablename__ = 'reservations'

    STATUS = ['nouveau', 'en_attente', 'confirme', 'annule']

    id          = db.Column(db.Integer, primary_key=True)
    prenom      = db.Column(db.String(80), nullable=False)
    nom         = db.Column(db.String(80), nullable=False)
    email       = db.Column(db.String(120), nullable=False)
    telephone   = db.Column(db.String(30))
    type_prest  = db.Column(db.String(60), nullable=False)
    date_event  = db.Column(db.Date)
    lieu        = db.Column(db.String(150))
    message     = db.Column(db.Text)
    status      = db.Column(db.String(20), default='nouveau')
    note_admin  = db.Column(db.Text)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def full_name(self):
        return f'{self.prenom} {self.nom}'

    @property
    def status_label(self):
        labels = {
            'nouveau':     'Nouveau',
            'en_attente':  'En attente',
            'confirme':    'Confirmé',
            'annule':      'Annulé',
        }
        return labels.get(self.status, self.status)

    @property
    def status_color(self):
        colors = {
            'nouveau':    'blue',
            'en_attente': 'yellow',
            'confirme':   'green',
            'annule':     'red',
        }
        return colors.get(self.status, 'gray')

    def __repr__(self):
        return f'<Reservation {self.full_name} — {self.type_prest}>'


# ─── TESTIMONIAL ────────────────────────────────────────────────
class Testimonial(db.Model):
    __tablename__ = 'testimonials'

    id          = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(120), nullable=False)
    author_role = db.Column(db.String(120))         # ex: "Mariage — Moroni"
    content     = db.Column(db.Text, nullable=False)
    rating      = db.Column(db.Integer, default=5)  # 1–5
    is_visible  = db.Column(db.Boolean, default=True)
    sort_order  = db.Column(db.Integer, default=0)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Testimonial {self.author_name}>'


# ─── SETTINGS ───────────────────────────────────────────────────
class Setting(db.Model):
    __tablename__ = 'settings'

    id    = db.Column(db.Integer, primary_key=True)
    key   = db.Column(db.String(80), unique=True, nullable=False)
    value = db.Column(db.Text)
    label = db.Column(db.String(150))   # human-readable label for admin UI

    DEFAULTS = {
        'site_title':       ('Anrcharo Photographe', 'Titre du site'),
        'hero_title':       ('Capturer l\'instant parfait', 'Titre Hero'),
        'hero_subtitle':    ('Mariage, portrait, commercial, paysage et shooting — chaque cliché raconte votre histoire.', 'Sous-titre Hero'),
        'about_text_1':     ('Passionné de photographie depuis mes premiers déclenchements, je mets mon œil et mon expertise au service de vos moments les plus précieux.', 'À propos paragraphe 1'),
        'about_text_2':     ('Spécialisé dans la photographie de mariage, portrait, commerciale, paysage et shooting, j\'apporte une vision moderne à chaque projet.', 'À propos paragraphe 2'),
        'experience_years': ('5+', 'Années d\'expérience'),
        'stat_seances':     ('500+', 'Stat — Séances'),
        'stat_mariages':    ('150+', 'Stat — Mariages'),
        'phone':            ('+269 435 51 49', 'Téléphone'),
        'facebook_url':     ('https://www.facebook.com/anrcharophotographe', 'Facebook URL'),
        'location':         ('Comores — Disponible partout', 'Localisation'),
    }

    def __repr__(self):
        return f'<Setting {self.key}={self.value}>'
