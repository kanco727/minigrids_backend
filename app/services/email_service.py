import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# Configuration email
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your-email@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "your-app-password")
SENDER_NAME = os.getenv("SENDER_NAME", "Mini-Grid Management System")

class EmailService:
    """Service pour envoyer des emails"""
    
    @staticmethod
    def send_email(
        recipient: str,
        subject: str,
        body: str,
        is_html: bool = True
    ) -> bool:
        """
        Envoie un email
        
        Args:
            recipient: Email du destinataire
            subject: Sujet de l'email
            body: Corps du message
            is_html: Si True, le corps est du HTML, sinon du texte brut
            
        Returns:
            True si succès, False sinon
        """
        try:
            # Créer le message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
            message["To"] = recipient
            
            # Ajouter le corps
            if is_html:
                part = MIMEText(body, "html")
            else:
                part = MIMEText(body, "plain")
            message.attach(part)
            
            # Envoyer l'email
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.sendmail(SENDER_EMAIL, recipient, message.as_string())
            
            logger.info(f"Email envoyé à {recipient}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi d'email à {recipient}: {str(e)}")
            return False
    
    @staticmethod
    def send_notification_email(
        recipient: str,
        notification_type: str,
        message: str,
        metadata: dict = None
    ) -> bool:
        """
        Envoie une notification par email avec template
        
        Args:
            recipient: Email du destinataire
            notification_type: Type de notification (alerte, maintenance, rapport)
            message: Message principal
            metadata: Données additionnelles
            
        Returns:
            True si succès, False sinon
        """
        # Templates HTML pour chaque type
        templates = {
            "alerte": """
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2 style="color: #d9534f;">🚨 Alerte Mini-Grid</h2>
                    <p>{message}</p>
                    {details}
                    <hr style="border: 1px solid #ddd; margin: 20px 0;">
                    <footer style="color: #888; font-size: 12px;">
                        <p>Système de Gestion Mini-Grid</p>
                    </footer>
                </body>
            </html>
            """,
            "maintenance": """
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2 style="color: #5bc0de;">🔧 Maintenance Requise</h2>
                    <p>{message}</p>
                    {details}
                    <hr style="border: 1px solid #ddd; margin: 20px 0;">
                    <footer style="color: #888; font-size: 12px;">
                        <p>Système de Gestion Mini-Grid</p>
                    </footer>
                </body>
            </html>
            """,
            "rapport": """
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2 style="color: #5cb85c;">📊 Rapport Mini-Grid</h2>
                    <p>{message}</p>
                    {details}
                    <hr style="border: 1px solid #ddd; margin: 20px 0;">
                    <footer style="color: #888; font-size: 12px;">
                        <p>Système de Gestion Mini-Grid</p>
                    </footer>
                </body>
            </html>
            """,
            "info": """
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2 style="color: #0275d8;">ℹ️ Information</h2>
                    <p>{message}</p>
                    {details}
                    <hr style="border: 1px solid #ddd; margin: 20px 0;">
                    <footer style="color: #888; font-size: 12px;">
                        <p>Système de Gestion Mini-Grid</p>
                    </footer>
                </body>
            </html>
            """,
        }
        
        # Construire les détails
        details = ""
        if metadata:
            details = "<dl>"
            for key, value in metadata.items():
                details += f"<dt><strong>{key}:</strong></dt><dd>{value}</dd>"
            details += "</dl>"
        
        template = templates.get(notification_type, templates["info"])
        html_body = template.format(message=message, details=details)
        
        subject_map = {
            "alerte": "[ALERTE] Mini-Grid",
            "maintenance": "[MAINTENANCE] Mini-Grid",
            "rapport": "[RAPPORT] Mini-Grid",
            "info": "Notification Mini-Grid",
        }
        
        subject = subject_map.get(notification_type, "Notification Mini-Grid")
        
        return EmailService.send_email(recipient, subject, html_body, is_html=True)
    
    @staticmethod
    def send_welcome_email(email: str, nom: str) -> bool:
        """Envoie un email de bienvenue"""
        subject = "Bienvenue dans le Système de Gestion Mini-Grid"
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Bienvenue, {nom}!</h2>
                <p>Vous avez été ajouté au Système de Gestion Mini-Grid.</p>
                <p>Connexion à : <strong>https://votre-app.com/login</strong></p>
                <p>Si vous avez des questions, contactez l'administrateur.</p>
                <hr style="border: 1px solid #ddd; margin: 20px 0;">
                <footer style="color: #888; font-size: 12px;">
                    <p>© 2026 Mini-Grid Management System</p>
                </footer>
            </body>
        </html>
        """
        return EmailService.send_email(email, subject, body, is_html=True)
