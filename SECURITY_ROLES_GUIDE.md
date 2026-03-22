# 🔐 Système de Rôles et Permissions - Documentation

## 📋 Vue d'ensemble

Le système a été amélioré pour inclure :

1. **Authentification JWT sécurisée** - Tokens JWT au lieu de tokens simples
2. **Système de rôles** - Admin, Superviseur, Technicien, Opérateur
3. **Système de permissions** - Permissions granulaires basées sur les rôles
4. **Service email** - Envoi de notifications par email réelles
5. **Mots de passe hachés** - Utilisation de bcrypt pour le hachage des mots de passe

---

## 👥 Rôles et Permissions

### Admin
Accès complet à toutes les fonctionnalités :
- ✅ Gestion complète des utilisateurs
- ✅ Gestion complète des mini-grids
- ✅ Gestion complète des sites
- ✅ Gestion de la maintenance
- ✅ Gestion des alertes
- ✅ Envoi de notifications

### Superviseur
Gestion complète sauf les utilisateurs :
- ✅ Vue des utilisateurs
- ✅ Gestion des mini-grids
- ✅ Gestion des sites
- ✅ Gestion de la maintenance
- ✅ Gestion des alertes
- ✅ Vue des statistiques

### Technicien
Accès en lecture et maintenance :
- ✅ Vue des mini-grids et sites
- ✅ Gestion de la maintenance
- ✅ Vue des alertes
- ✅ Vue des statistiques
- ❌ Pas d'accès à la gestion des utilisateurs

### Opérateur
Accès en lecture seulement :
- ✅ Vue des mini-grids et sites
- ✅ Vue de la maintenance
- ✅ Vue des alertes
- ✅ Vue des statistiques
- ❌ Pas de modifications

---

## 🔑 Authentification

### Login
```bash
POST /auth/login
Content-Type: application/json

{
    "email": "admin@example.com",
    "mot_de_passe": "votre_mot_de_passe"
}
```

**Réponse (200 OK):**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "user": {
        "id": 1,
        "email": "admin@example.com",
        "role": "admin",
        "actif": true
    }
}
```

### Utiliser le Token
```bash
GET /utilisateurs
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Registrer un nouvel utilisateur
```bash
POST /auth/register
Content-Type: application/json

{
    "email": "technicien@example.com",
    "nom_complet": "Jean Technicien",
    "mot_de_passe": "password123",
    "role": "technicien"
}
```

---

## 📧 Service Email

### Configuration

Créez un fichier `.env` à la racine du projet :

```env
# JWT Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Configuration (Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
SENDER_NAME=Mini-Grid Management System
```

### Générer un App Password pour Gmail

1. Activez l'authentification double facteur sur votre compte Gmail
2. Allez à : https://myaccount.google.com/apppasswords
3. Sélectionnez "Mail" et "Windows Computer"
4. Copiez le mot de passe généré et collez-le dans `SENDER_PASSWORD`

### Envoyer une Notification par Email

```bash
POST /notifications/1/send-email
Authorization: Bearer [token]
```

**Réponse:**
```json
{
    "notification_id": 1,
    "emails_sent": 5,
    "total_recipients": 5
}
```

---

## 🔒 Sécurité

### Points clés

1. **JWT Expiration** - Les tokens expirent après 30 minutes (configurable)
2. **Hachage Bcrypt** - Les mots de passe sont hachés avec bcrypt
3. **Validation des Permissions** - Toutes les opérations sensibles nécessitent une permission
4. **Utilisateur Désactivé** - Les utilisateurs éventuellement désactivés ne peuvent pas se connecter

---

## 📝 Migration des Utilisateurs Existants

Exécutez le script `hash_passwords.py` pour hacher les mots de passe existants :

```bash
python hash_passwords.py
```

---

## 🧪 Endpoints Protégés par Permissions

| Endpoint | Permission Requise |
|----------|-------------------|
| `GET /utilisateurs` | MANAGE_USERS |
| `POST /utilisateurs` | MANAGE_USERS |
| `PATCH /utilisateurs/{id}` | (Admin ou self) |
| `DELETE /utilisateurs/{id}` | MANAGE_USERS |
| `POST /minigrids` | MANAGE_MINIGRIDS |
| `PATCH /minigrids/{id}` | MANAGE_MINIGRIDS |
| `DELETE /minigrids/{id}` | MANAGE_MINIGRIDS |
| `POST /notifications` | SEND_NOTIFICATIONS |
| `POST /notifications/{id}/send-email` | SEND_NOTIFICATIONS |

---

## ⚡ Changements dans le Code

### Nouveaux fichiers

1. **`app/enums.py`** - Énumérations des rôles et permissions
2. **`app/security.py`** - Gestion JWT et hachage de mots de passe
3. **`app/dependencies.py`** - Dépendances FastAPI pour les permissions
4. **`app/services/email_service.py`** - Service pour envoyer des emails
5. **`.env.example`** - Template de configuration

### Fichiers modifiés

1. **`app/models/utilisateur.py`** - Ajout de champs (actif, date_modification)
2. **`app/schemas/utilisateur.py`** - Mise à jour des schémas avec EmailStr
3. **`app/routers/auth.py`** - JWT et hachage des mots de passe
4. **`app/routers/utilisateur.py`** - Permissions et hachage des mots de passe
5. **`app/routers/notification_minigrid.py`** - Envoi d'emails
6. **`app/routers/minigrid.py`** - Ajout de permissions aux create/update/delete
7. **`requirements.txt`** - Nouvelles dépendances

---

## 🐛 Dépannage

### Question: Comment changer le rôle d'un utilisateur?

**Réponse:** Via l'endpoint `PATCH /utilisateurs/{id}` :

```bash
PATCH /utilisateurs/1
Authorization: Bearer [admin_token]
Content-Type: application/json

{
    "role": "superviseur"
}
```

### Question: Comment désactiver un utilisateur?

**Réponse:** Via l'endpoint `PATCH /utilisateurs/{id}` :

```bash
PATCH /utilisateurs/1
Authorization: Bearer [admin_token]
Content-Type: application/json

{
    "actif": false
}
```

### Question: Pourquoi je reçois l'erreur "Token invalide"?

**Réponse:** 
- Le token a expiré (après 30 minutes)
- Vous devez vous reconnecter
- Le token n'est pas au bon format (doit être au format `Bearer [token]`)

