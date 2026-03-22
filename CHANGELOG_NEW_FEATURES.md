# 🚀 Améliorations du Système de Gestion Mini-Grid

## 📦 Changements Effectués

Vous avez demandé une révision complète du système d'identification et des permissions des utilisateurs, ainsi qu'une intégration d'envoi d'emails. Voici ce qui a été fait :

### ✅ 1. Système de Rôles et Permissions

**Nouveaux rôles créés :**
- **Admin** - Accès complet à toutes les fonctionnalités
- **Superviseur** - Gestion complète sauf les utilisateurs
- **Technicien** - Accès en lecture + gestion de la maintenance
- **Opérateur** - Accès en lecture seulement

**Fichier:** [`app/enums.py`](app/enums.py)

```python
class RoleEnum(str, Enum):
    ADMIN = "admin"
    TECHNICIEN = "technicien"
    OPERATEUR = "operateur"
    SUPERVISEUR = "superviseur"
```

---

### ✅ 2. Authentification JWT Sécurisée

Remplacement des tokens simples par JWT (JSON Web Tokens) avec expiration.

**Fichier:** [`app/security.py`](app/security.py)

**Points clés:**
- JWT avec expiration après 30 minutes (configurable)
- Hachage des mots de passe avec bcrypt
- Validation de tokens

---

### ✅ 3. Système de Permissions

Les permissions sont automatiquement vérifiées basées sur le rôle de l'utilisateur.

**Fichier:** [`app/dependencies.py`](app/dependencies.py)

**Exemple d'utilisation dans les routers:**
```python
@router.post("/minigrids")
async def create_minigrid(
    payload: schemas.MiniGridCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.Utilisateur = Depends(
        require_permission(PermissionEnum.MANAGE_MINIGRIDS)
    )
):
    # Seuls les utilisateurs avec MANAGE_MINIGRIDS peuvent create
    ...
```

---

### ✅ 4. Service d'Email

Envoi de notifications par email réelles avec templates HTML.

**Fichier:** [`app/services/email_service.py`](app/services/email_service.py)

**Fonctionnalités:**
- Envoi d'emails via SMTP
- Templates HTML pour : alertes, maintenance, rapports, info
- Envoi de mails de bienvenue
- Support de multiples services (Gmail, SendGrid, Mailgun, etc.)

**Exemple:**
```python
EmailService.send_notification_email(
    recipient="technicien@example.com",
    notification_type="alerte",
    message="Tension anormale détectée",
    metadata={"Minigrid": "MG-001", "Voltage": "220V"}
)
```

---

### ✅ 5. Amélioration du Modèle Utilisateur

**Fichier:** [`app/models/utilisateur.py`](app/models/utilisateur.py)

**Changements:**
- Ajout champ `actif` (pour désactiver un utilisateur)
- Ajout champs `date_modification`
- Email unique
- Rôle utilisant l'enum

```python
class Utilisateur(Base):
    id = Column(BigInteger, primary_key=True)
    nom = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True, index=True)
    mot_de_passe = Column(Text, nullable=False)  # Hashed
    role = Column(Text, default=RoleEnum.TECHNICIEN)
    actif = Column(Boolean, default=True)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())
```

---

### ✅ 6. Authentification Améliorée

**Fichier:** [`app/routers/auth.py`](app/routers/auth.py)

**Nouvelles fonctionnalités:**
- Login avec JWT token
- Endpoint `/register` pour créer de nouveaux utilisateurs
- Validation de l'utilisateur (actif/inactif)
- Envoi d'email de bienvenue

```bash
# Login
POST /auth/login
{
    "email": "admin@example.com",
    "mot_de_passe": "password123"
}

# Register
POST /auth/register
{
    "email": "technicien@example.com",
    "nom_complet": "Jean Technicien",
    "mot_de_passe": "password123",
    "role": "technicien"
}
```

---

## 🔧 Configuration Email

### Étape 1 : Créer le fichier `.env`

```bash
# JWT Configuration
SECRET_KEY=votre-clé-secrète-très-longue-changez-ceci
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuration Email (Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=votre-email@gmail.com
SENDER_PASSWORD=votre-app-password
SENDER_NAME=Mini-Grid Management System
```

### Étape 2 : Générer un App Password (pour Gmail)

1. Activez l'authentification double facteur : https://accounts.google.com/signin/
2. Allez à https://myaccount.google.com/apppasswords
3. Sélectionnez "Mail" et "Windows Computer"
4. Copiez le mot de passe généré et collez-le dans `SENDER_PASSWORD`

### Étape 3 : Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## 🚀 Utilisation

### 1. Initialiser les utilisateurs de démonstration

```bash
python init_demo_users.py
```

**Utilisateurs créés :**
- `admin@minigrids.local` (admin123) - Admin
- `superviseur@minigrids.local` (superviseur123) - Superviseur
- `jean.technicien@minigrids.local` (tech123) - Technicien
- `marie.technicien@minigrids.local` (tech123) - Technicien  
- `operateur.sitea@minigrids.local` (op123) - Opérateur
- `operateur.siteb@minigrids.local` (op123) - Opérateur

### 2. Hacher les mots de passe existants (migration)

```bash
python hash_passwords.py
```

### 3. Lancer l'application

```bash
uvicorn app.main:app --reload
```

---

## 🧪 Tester les APIs

### Login avec cURL

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@minigrids.local",
    "mot_de_passe": "admin123"
  }'
```

**Réponse:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "admin@minigrids.local",
    "role": "admin",
    "actif": true
  }
}
```

### Utiliser le token

```bash
curl -X GET "http://localhost:8000/utilisateurs" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Créer une notification et l'envoyer par email

```bash
# 1. Créer la notification
curl -X POST "http://localhost:8000/notifications" \
  -H "Authorization: Bearer [token]" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Maintenance requise sur MG-001",
    "type": "maintenance",
    "destinataire": "technicien"
  }'

# 2. Envoyer par email
curl -X POST "http://localhost:8000/notifications/1/send-email" \
  -H "Authorization: Bearer [token]"
```

---

## 📁 Fichiers Créés/Modifiés

### ✨ Nouveaux fichiers
- `app/enums.py` - Énumérations des rôles et permissions
- `app/security.py` - JWT et hachage de mots de passe
- `app/dependencies.py` - Dépendances FastAPI pour les permissions
- `app/services/email_service.py` - Service d'envoi d'emails
- `.env.example` - Template de configuration
- `init_demo_users.py` - Initialiser les utilisateurs démo
- `hash_passwords.py` - Migrer les mots de passe existants
- `SECURITY_ROLES_GUIDE.md` - Documentation complète des rôles

### 📝 Fichiers modifiés
- `app/models/utilisateur.py` - Ajout champs actif, date_modification
- `app/schemas/utilisateur.py` - Utilisation de EmailStr
- `app/routers/auth.py` - JWT et registration
- `app/routers/utilisateur.py` - Permissions et hachage
- `app/routers/notification_minigrid.py` - Envoi email notifications
- `app/routers/minigrid.py` - Ajout permissions MANAGE_MINIGRIDS
- `requirements.txt` - Nouvelles dépendances

---

## ⚙️ Dépendances Ajoutées

```
python-jose[cryptography]>=3.3.0  # JWT
passlib[bcrypt]>=1.7.4             # Password hashing
python-multipart>=0.0.6            # Form parsing
pydantic-settings>=2.0              # Settings management
python-dotenv>=1.0.0                # .env support
aiosmtplib>=3.0.0                   # Async SMTP
email-validator>=2.0.0              # Email validation
```

---

## 🔒 Points de Sécurité

1. ✅ **JWT Tokens** - Expiration après 30 minutes
2. ✅ **Bcrypt Hashing** - Mots de passe sécurisés
3. ✅ **Permissions Granulaires** - Contrôle d'accès basé sur les rôles
4. ✅ **Utilisateur Désactivable** - Les utilisateurs peuvent être désactivés
5. ✅ **Email Unique** - Pas deux utilisateurs avec le même email
6. ✅ **SMTP Sécurisé** - Utilisation de TLS pour les emails

---

## 📚 Documentation Complète

Pour plus de détails, voir :
- **[SECURITY_ROLES_GUIDE.md](SECURITY_ROLES_GUIDE.md)** - Guide complet des rôles et permissions
- **[.env.example](.env.example)** - Variables d'environnement
- **[Swagger API**](http://localhost:8000/docs) - Documentation interactive

---

## 🆘 Dépannage

**Q: Comment activer SMTP pour Gmail?**
A: Activez l'authentification double facteur et générez un app password

**Q: Les emails ne s'envoient pas?**
A: Vérifiez que `SENDER_EMAIL` et `SENDER_PASSWORD` sont corrects dans `.env`

**Q: Comment changer le rôle d'un utilisateur?**
A: `PATCH /utilisateurs/{id}` avec `{"role": "admin"}` (admin seulement)

**Q: Comment désactiver un utilisateur?**
A: `PATCH /utilisateurs/{id}` avec `{"actif": false}` (admin seulement)

---

Vous êtes maintenant prêt à utiliser le nouveau système! 🎉

