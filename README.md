# # archivault

**archivault** est la plateforme de référence pour la digitalisation de l'administration et de la gestion documentaire sécurisée en Afrique. Conçu pour s'exécuter de manière résiliente en environnement **intranet** comme sur serveur dédié/VPS, le système offre une gestion fine du cycle de vie des documents, un contrôle hiérarchique strict, une indexation plein texte (OCR) et un système d'audit log inaltérable assurant une traçabilité totale conforme aux exigences réglementaires.

---

## 🚀 Fonctionnalités Clés

### 📂 1. Gestion Documentaire & Classement Intelligent

- **Classement Hybride :** Classement manuel ou automatique basé sur des règles strictes (par Thématique, Catégorie, Date, Type, Cellule, Responsable). _Règle métier : Une catégorie appartient obligatoirement à une thématique._
- **Support Universel de Fichiers :** Prise en charge de tous les formats (Textes, PDF, Word, Excel, PowerPoint, Images, Audios, Vidéos).
- **Gestion des Métadonnées Personnalisées :** Ajout dynamique de champs spécifiques selon la nature du document avec gestion multilingue du contenu des métadonnées (ex: Titre en FR et en EN).
- **Importation et Catégorisation en Masse :** Téléchargement groupé de documents avec routage automatique selon le type de fichier ou pré-mappage via un manifeste (JSON/XML).
- **Système de Versioning (GED) :** Historique linéaire des versions d’un document (mises à jour, remplacements, corrections) associant à chaque itération son auteur et son horodatage précis.
- **Favoris & Raccourcis :** Accès rapide aux documents clés et dossiers fréquents par profil utilisateur.

### 🔍 2. Moteur de Recherche Avancé & OCR

- **Recherche Plein Texte (OCR) :** Reconnaissance optique de caractères permettant de chercher directement des mots-clés au sein du contenu des images et des fichiers PDF numérisés.
- **Recherche Combinée :** Indexation croisée combinant le contenu textuel brut, les métadonnées spécifiques, les tags libres et les catégories.
- **Opérateurs Logiques :** Support des requêtes complexes via opérateurs booléens (`AND`, `OR`, `NOT`).

### ⚙️ 3. Circuits de Validation & Historique de Circulation

- **Workflows Configurables :** Définition de circuits de validation hiérarchiques personnalisés (ex : Initiateur → Chef de division → Directeur avant l'archivage définitif).
- **Génération Automatique :** Production automatisée des fiches de circulation et des documents d'accompagnement.
- **Traçabilité de Circulation :** Historique complet des transferts, avis et validations d'un document au sein de l'organisation.

### 🛡️ 4. Sécurité, Droits d'Accès Fins (ACL) & Signature

- **Contrôle d'Accès Matriciel :** Association fine de chaque document à un ou plusieurs profils d'utilisateurs avec niveaux de permissions restrictifs (Lecture seule, Modification, Impression, Téléchargement interdit).
- **Héritage Dynamique des Permissions :** Le responsable ou superviseur d'une cellule hérite automatiquement des droits d'accès sur l'ensemble des documents produits ou assignés à sa cellule.
- **Signature Électronique :** Module intégré permettant la signature numérique et l'authentification de l'intégrité des documents officiels.

### 👁️ 5. Gouvernance, Audit Log Inaltérable & Cycle de vie

- **Journalisation Globale (Audit Log) :** Suivi distinct de l'historique documentaire. Chaque événement système (Connexion, Déconnexion, Création, Modification unitaire/masse, Consultation, Téléchargement, Impression, Suppression unitaire/masse) est consigné de manière inaltérable (IP, User-Agent, Deltas avant/après).
- **Plan de Conservation Réglementaire :** Définition des cycles de vie des documents (ex : conservation active de 5 ans en cellule, transfert automatique en archivage définitif, ou suppression définitive après 10 ans).

### 🌐 6. Expérience Utilisateur & Infrastructure

- **Mode Intranet Autonome :** Optimisé pour fonctionner sans accès Internet, idéal pour la souveraineté des données des institutions et infrastructures locales.
- **Tableaux de Bord Rôles-Dépendants :** Statistiques personnalisées, alertes de conservation et raccourcis de tâches adaptés selon le niveau de responsabilité.
- **Notifications Intelligentes :** Système d'alertes en temps réel (via Sidebar, e-mail ou push internes) pour les validations en attente, arrivées de documents, ou échéances de conservation.
- **Architecture Multilingue Natio-Prête :** Prise en charge initiale complète du Français et de l'Anglais, conçue pour l'intégration facile de nouvelles langues.
- **Sauvegardes Automatisées :** Routine interne de snapshots réguliers de la base de données et du stockage de fichiers (Volume `media`).

---

## 🛠️ Architecture Technique

L'application adopte une séparation stricte des responsabilités (SOC) via une architecture orientée services sous Django :

- **Backend :** Django 4.2+ / Django Rest Framework (DRF)
- _Contrôle d'accès :_ `DRFRoleRequiredMixin` & `RoleRequiredMixin` couplés à l'énumération `RoleUtilisateur` (`SUPERADMIN`, `ADMIN`, `SUPERVISEUR`, `RESPONSABLE`, `GESTIONNAIRE`).
- _Couche Métier :_ Centralisation des logiques complexes dans des classes `Services` (ex: `UserService`, `AuditService`).
- _Vues Communes :_ Héritage de structures génériques robustes (`BaseAPIView` pour les endpoints REST synchrone/asynchrone, `BaseCRUDView` pour le rendu des interfaces web).

- **Base de données :** PostgreSQL ou MySQL (avec support natif des champs `JSONField` pour l'audit et les métadonnées).
- **Indexation & OCR :** Intégration d'outils d'extraction textuelle (ex: Tesseract OCR / Celery pour les tâches asynchrones).
- **Serveur Web & Déploiement :** Docker (Multi-containers), Nginx (Configuré pour la gestion des gros volumes d'upload de fichiers - `client_max_body_size`).

---

## 📂 Structure du Projet (Aperçu)

```plaintext
archivault/
│
├── apps/
│   ├── users/                 # Gestion des comptes, rôles et permissions
│   │   ├── models.py          # Utilisateur, RoleUtilisateur
│   │   └── api/views/         # UserAPIView (Gestion full API unitaire et masse)
│   │
│   ├── circulation/           # Moteur des circuits, documents et Audit Log
│   │   ├── models.py          # AuditLog, ActionAudit, StatutAudit
│   │   ├── services/          # AuditService.py (Enregistrement thread-safe)
│   │   └── api/views/         # AuditLogAPIView, AuditLogManagementView (Filtres avancés)
│   │
│   └── notifications/         # Centre de notifications et alertes
│       ├── models.py          # Notification (Liaison GenericForeignKey vers Tâches/Circulations)
│       └── api/views/         # NotificationAPIView (Marquage, traçabilité hiérarchique)
│
├── config/                    # Configurations globales et Mixins réutilisables
│   ├── api/                   # BaseAPIView.py
│   ├── mixins/                # drf_permissions.py
│   └── settings.py
│
├── static/js/                 # Contrôleurs front-end asynchrones (Architecture modulaire)
└── templates/                 # Interfaces utilisateur HTML5 / Bootstrap
```

---

## 🔧 Installation & Configuration en Développement

### 1. Clonage et Environnement Virtuel

```bash
git clone https://github.com/noumecha/archivault.git
cd archivault

python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
pip install -r requirements.txt

```

### 2. Variables d'Environnement (`.env`)

Créez un fichier `.env` à la racine du projet :

```env
DEBUG=True
SECRET_KEY=votre_cle_secrete_ici
DB_NAME=votre_db_name
DB_USER=votre_user_db
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432

```

### 3. Migrations et Initialisation

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Créez le premier SUPERADMIN
python manage.py runserver

```

---

## 🐳 Déploiement via Docker & Nginx (Production / Intranet)

Le projet intègre une configuration Docker optimisée pour l'environnement Intranet :

```bash
# Construction et lancement des conteneurs en mode détaché
docker-compose up -d --build

```

### Ajustement Nginx impératif (Gros fichiers)

Pour éviter l'erreur `413 Request Entity Too Large` lors de l'importation de fichiers volumineux ou en masse, vérifiez que le fichier de configuration de votre serveur Nginx (`nginx.conf`) contient :

```nginx
client_max_body_size 100M; # Ajuster selon la taille maximale des vidéos/audios acceptée

```

---

## 📊 Focus Sécurité : Le Module d'Audit

Toutes les modifications de données critiques, suppressions en masse de notifications, ou changements de statut des utilisateurs (`is_active`) passent par une transaction atomique sécurisée et génèrent une entrée immédiate dans le journal d'audit :

```python
# Exemple de structure d'un log généré automatiquement
{
    "utilisateur": "admin_principal",
    "action": "modification",
    "objet_label": "[Utilisateur] Jean Dupont",
    "details": {
        "champ": "is_active",
        "avant": true,
        "apres": false
    },
    "ip_address": "127.0.0.1",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "statut": "success"
}

```

L'interface de supervision d'audit embarque un système de filtrage de pointe : recherche par opérateur, par type d'action, par module applicatif (`ContentType`), par ID d'élément spécifique et par plages de dates cumulables.

---

## 🔮 Prochainement (Coming Soon)

- 🧠 **Intégration d'Intelligence Artificielle :** Analyse prédictive des documents, suggestions automatiques de métadonnées et de tags lors du téléversement, et résumé de texte automatisé des circuits de circulation denses.
- 🌍 **Support Multilingue Étendu :** Traduction complète de l'interface vers d'autres langues régionales et internationales.

## run redis on local

# installation

- docker run -d --name local-redis -p 6379:6379 redis:7-alpine

# runinng the worker and the broker (2 other terminals)

- celery -A config beat --loglevel=info --pidfile=
- celery -A config worker --loglevel=info -P solo
