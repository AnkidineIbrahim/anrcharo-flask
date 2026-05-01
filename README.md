# 📸 Anrcharo Photographe — Flask + PostgreSQL

Site web de photographe professionnel avec espace admin complet.

---

## 🗂️ Structure du projet

```
anrcharo-flask/
├── wsgi.py                  ← Point d'entrée Gunicorn (Railway)
├── run.py                   ← Dev local
├── init_db.py               ← Initialisation BDD + admin
├── config.py                ← Configuration (dev/prod)
├── Procfile                 ← Commandes Railway
├── railway.json             ← Config Railway
├── requirements.txt
├── .env.example             ← Variables d'environnement
└── app/
    ├── __init__.py          ← Factory Flask
    ├── models/
    │   ├── user.py          ← Modèle utilisateur admin
    │   ├── photo.py         ← Modèle photos
    │   └── models.py        ← Réservations, Témoignages, Settings
    ├── routes/
    │   ├── public.py        ← Routes publiques
    │   ├── admin.py         ← Routes admin (protégées)
    │   └── api.py           ← API JSON (portfolio AJAX)
    ├── utils/
    │   └── upload.py        ← Gestion upload images
    ├── templates/
    │   ├── public/
    │   │   └── index.html   ← Site public
    │   └── admin/
    │       ├── base.html    ← Layout admin
    │       ├── login.html
    │       ├── dashboard.html
    │       ├── photos.html
    │       ├── photo_upload.html
    │       ├── photo_edit.html
    │       ├── reservations.html
    │       ├── reservation_detail.html
    │       ├── testimonials.html
    │       ├── testimonial_form.html
    │       ├── settings.html
    │       └── account.html
    └── static/
        ├── css/style.css
        ├── js/main.js
        ├── icons/           ← Logo + favicons
        └── images/          ← Photos (local dev)
```

---

## 🚀 Déploiement sur Railway

### Étape 1 — Préparer le dépôt GitHub

```bash
git init
git add .
git commit -m "Initial commit — Anrcharo Photographe"
git remote add origin https://github.com/VOTRE_USER/anrcharo.git
git push -u origin main
```

### Étape 2 — Créer le projet sur Railway

1. Allez sur [railway.app](https://railway.app) → **New Project**
2. Choisissez **Deploy from GitHub repo**
3. Sélectionnez votre dépôt

### Étape 3 — Ajouter PostgreSQL

Dans votre projet Railway :
1. Cliquez **+ New** → **Database** → **PostgreSQL**
2. Railway génère automatiquement `DATABASE_URL`

### Étape 4 — Configurer les variables d'environnement

Dans Railway → votre service Flask → **Variables** :

| Variable | Valeur |
|---|---|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | Une clé aléatoire longue (ex: `openssl rand -hex 32`) |
| `ADMIN_USERNAME` | `admin` |
| `ADMIN_EMAIL` | `votre@email.com` |
| `ADMIN_PASSWORD` | Votre mot de passe sécurisé |

> `DATABASE_URL` est ajouté automatiquement par Railway via le plugin PostgreSQL.

### Étape 5 — Déployer

Railway lance automatiquement :
1. `pip install -r requirements.txt`
2. `python init_db.py` (via `release` dans Procfile)
3. `gunicorn wsgi:app`

---

## 💻 Développement local

```bash
# 1. Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer les variables
cp .env.example .env
# Éditez .env selon vos besoins

# 4. Initialiser la base de données
python init_db.py

# 5. Lancer le serveur
python run.py
```

Accès :
- **Site public** → http://localhost:5000
- **Admin** → http://localhost:5000/admin/login
- **Login par défaut** → `admin` / `Admin@2025!`

---

## 🖼️ Images en production (Cloudinary)

Sur Railway, le système de fichiers est éphémère : les images uploadées sont **perdues** au redémarrage. Utilisez **Cloudinary** (gratuit jusqu'à 25 GB) :

1. Créez un compte sur [cloudinary.com](https://cloudinary.com)
2. Ajoutez ces variables Railway :

| Variable | Valeur |
|---|---|
| `CLOUDINARY_CLOUD_NAME` | Votre cloud name |
| `CLOUDINARY_API_KEY` | Votre API key |
| `CLOUDINARY_API_SECRET` | Votre API secret |

L'app détecte automatiquement Cloudinary et l'utilise pour tous les uploads.

---

## 🔐 Accès admin

- URL : `/admin/login`
- Changer le mot de passe : `/admin/account`

## 📋 Fonctionnalités admin

| Section | Fonctionnalités |
|---|---|
| **Dashboard** | Stats globales, dernières réservations |
| **Photos** | Upload multiple, drag & drop, filtres par catégorie, édition, suppression |
| **Réservations** | Liste filtrée par statut, détail client, notes internes, envoi email |
| **Témoignages** | CRUD complet, ordre d'affichage, visibilité |
| **Paramètres** | Textes du site (hero, à propos, contact) |
| **Compte** | Changement mot de passe et email |
