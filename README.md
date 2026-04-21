# HRControl - Gestion des Ressources Humaines

**Auteur : Baabo Luendo Daniella**

**Slogan : "Gérez vos ressources humaines simplement."**

Application SaaS complète de gestion RH permettant la gestion des candidats, l'évaluation, la transformation en employés, la gestion des employés, l'onboarding, l'analyse des talents, le turnover et un dashboard global.

---

## 🏗️ Architecture

### Backend
- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Base de données**: SQLite (hrcontrol.db)

### Frontend
- **HTML5**
- **CSS3** (Thème sombre violet)
- **JavaScript** (Vanilla)

---

## 📁 Structure du Projet

```
HRControl/
├── backend/
│   ├── main.py              # Point d'entrée FastAPI avec CORS
│   ├── models.py            # Modèles de base de données
│   ├── candidates.py        # Routes pour les candidats
│   ├── employees.py         # Routes pour les employés
│   ├── onboarding.py        # Routes pour l'onboarding
│   └── dashboard.py         # Route pour le dashboard
├── frontend/
│   ├── index.html           # Structure HTML complète
│   ├── style.css            # Styles CSS (thème violet)
│   └── app.js               # Logique JavaScript
├── requirements.txt         # Dépendances Python
└── README.md               # Ce fichier
```

---

## 🚀 Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Naviguer vers le répertoire du projet**
   ```bash
   cd HRControl
   ```

2. **Créer un environnement virtuel (recommandé)**
   ```bash
   python -m venv venv
   ```

3. **Activer l'environnement virtuel**
   
   **Windows:**
   ```bash
   venv\Scripts\activate
   ```
   
   **Linux/Mac:**
   ```bash
   source venv/bin/activate
   ```

4. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Lancement de l'Application

### 1. Démarrer le Backend (FastAPI)

```bash
cd backend
python main.py
```

Le backend sera accessible sur: **http://127.0.0.1:8000**

API Documentation disponible sur: **http://127.0.0.1:8000/docs**

### 2. Ouvrir le Frontend

Ouvrez simplement le fichier `frontend/index.html` dans votre navigateur web.

Ou utilisez un serveur HTTP local:
```bash
cd frontend
python -m http.server 8080
```

Puis accédez à: **http://localhost:8080**

---

## 📊 Fonctionnalités

### 1. Candidats
- ✅ Créer un candidat (nom, email)
- ✅ Voir les détails d'un candidat
- ✅ Évaluer un candidat (score 0-100, commentaire)
- ✅ Changer le statut (ANALYSE, ENTRETIEN, ACCEPTÉ, REJETÉ)
- ✅ Transformer un candidat accepté en employé
- ✅ Supprimer un candidat

### 2. Employés
- ✅ Créer un employé avec informations complètes:
  - Nom, Email, Date d'embauche, Statut
  - Date de naissance, Statut familial
  - Poste, Département, Niveau
  - Salaire base, Prime, Transport, Assurance
  - Autres avantages
- ✅ Voir les détails d'un employé
- ✅ Supprimer un employé

### 3. Onboarding
- ✅ Checklist pour chaque employé:
  - Contrat signé
  - Email créé
  - Matériel attribué
  - Formation complétée
- ✅ Calcul automatique du % de progression

### 4. Dashboard
- ✅ Total des candidats
- ✅ Total des employés
- ✅ Candidats approuvés
- ✅ % moyen d'onboarding

---

## 🗄️ Base de Données

### Tables

#### **Candidate**
- id
- name
- email
- statut (ANALYSE, ENTRETIEN, ACCEPTÉ, REJETÉ)
- score (0-100)
- commentaire
- created_at

#### **Employee**
- id
- name
- email
- date_embauche
- statut (ACTIF, CONGE, FORMATION)
- date_naissance
- statut_familial (célibataire, marié, divorcé, veuf, en couple)
- poste
- departement
- niveau (junior, intermédiaire, senior, directeur)
- salaire_base
- prime
- transport
- assurance
- autres_avantages
- created_at

#### **Onboarding**
- id
- employee_id
- contrat_signe (bool)
- email_cree (bool)
- materiel_attribue (bool)
- formation_completee (bool)

---

## 🔌 API Routes

### Candidats
- `POST /api/candidates` - Créer un candidat
- `GET /api/candidates` - Lister tous les candidats
- `PUT /api/candidates/{id}/status` - Modifier le statut
- `PUT /api/candidates/{id}/evaluate` - Évaluer un candidat
- `DELETE /api/candidates/{id}` - Supprimer un candidat

### Employés
- `POST /api/employees` - Créer un employé
- `GET /api/employees` - Lister tous les employés
- `GET /api/employees/{id}` - Voir détails d'un employé
- `PUT /api/employees/{id}` - Modifier un employé
- `DELETE /api/employees/{id}` - Supprimer un employé

### Onboarding
- `GET /api/onboarding` - Lister tous les onboardings
- `GET /api/onboarding/{employee_id}` - Voir onboarding d'un employé
- `PUT /api/onboarding/{employee_id}` - Mettre à jour l'onboarding

### Dashboard
- `GET /api/dashboard` - Statistiques globales

---

## 🎨 Design

- **Thème**: Fond sombre violet dégradé
- **Couleurs**: Violet (#6b46c1, #9f7aea, #b794f4)
- **Style**: Moderne avec cartes (cards), boutons stylisés
- **Responsive**: Adapté mobile et desktop

---

## 💡 Workflow RH Complet

1. **Créer candidat** → Entrer nom et email
2. **Voir détails** → Consulter informations
3. **Évaluer candidat** → Attribuer score et commentaire
4. **Changer statut** → ANALYSE → ENTRETIEN → ACCEPTÉ/REJETÉ
5. **Approuver** → Si ACCEPTÉ, bouton "Créer employé" apparaît
6. **Créer employé** → Transformation automatique avec suppression du candidat
7. **Gérer employé** → Informations complètes (salaire, avantages, etc.)
8. **Suivre onboarding** → Checklist avec progression %
9. **Dashboard** → Vue globale des statistiques

---

## 🔒 Persistance des Données

- Toutes les données sont stockées dans **hrcontrol.db** (SQLite)
- Aucune donnée n'est perdue après rafraîchissement
- La base de données est créée automatiquement au premier lancement
- Les données persistent entre les sessions

---

## 🛠️ Technologies Utilisées

### Backend
- FastAPI 0.104.1
- Uvicorn 0.24.0
- SQLAlchemy 2.0.23
- Pydantic 2.5.0

### Frontend
- HTML5
- CSS3 (Flexbox, Grid, Gradients)
- JavaScript ES6+ (Fetch API, Async/Await)

---

## 📝 Notes Importantes

- Aucune donnée fake/mock - tout est persisté en base de données
- API JSON uniquement
- CORS activé pour permettre les requêtes depuis le frontend
- Gestion des erreurs avec messages clairs
- Interface utilisateur réactive et intuitive

---

## 🐛 Dépannage

### Le backend ne démarre pas
- Vérifiez que le port 8000 n'est pas déjà utilisé
- Assurez-vous que toutes les dépendances sont installées
- Vérifiez que Python 3.8+ est installé

### Erreur de connexion à l'API
- Vérifiez que le backend est en cours d'exécution
- Vérifiez que l'URL dans `app.js` (API_URL) est correcte
- Assurez-vous que CORS est activé

### La base de données ne se crée pas
- Vérifiez les permissions d'écriture dans le dossier
- Le fichier `hrcontrol.db` sera créé dans le dossier backend

---

## 📄 Licence

Ce projet est fourni tel quel pour usage éducatif et professionnel.

---

**Développé avec ❤️ pour simplifier la gestion RH**
