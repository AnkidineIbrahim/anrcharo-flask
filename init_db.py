"""
Script d'initialisation de la base de données.
Lance : python init_db.py

Crée les tables, le compte admin par défaut et les paramètres.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models.user import User
from app.models.models import Setting
from app.models.photo import Photo

def init_db():
    app = create_app(os.environ.get('FLASK_ENV', 'development'))

    with app.app_context():
        print("⏳ Création des tables…")
        db.create_all()
        print("✅ Tables créées.")

        # ── Admin par défaut ─────────────────────────────
        if not User.query.first():
            admin = User(
                username = os.environ.get('ADMIN_USERNAME', 'admin'),
                email    = os.environ.get('ADMIN_EMAIL', 'admin@anrcharo.com'),
                is_admin = True,
            )
            admin.set_password(os.environ.get('ADMIN_PASSWORD', 'Admin@2025!'))
            db.session.add(admin)
            print(f"✅ Admin créé : {admin.username} / mot de passe : Admin@2025!")
            print("⚠️  Changez le mot de passe immédiatement dans /admin/account")
        else:
            print("ℹ️  Admin déjà existant, ignoré.")

        # ── Paramètres par défaut ────────────────────────
        existing_keys = {s.key for s in Setting.query.all()}
        added = 0
        for key, (value, label) in Setting.DEFAULTS.items():
            if key not in existing_keys:
                db.session.add(Setting(key=key, value=value, label=label))
                added += 1
        db.session.commit()
        print(f"✅ {added} paramètre(s) ajouté(s).")
        print("\n🚀 Base de données prête !")
        print("   Accès admin : /admin/login")

if __name__ == '__main__':
    init_db()
