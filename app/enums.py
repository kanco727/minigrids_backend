from enum import Enum

class RoleEnum(str, Enum):
    """Énumération des rôles utilisateur"""
    ADMIN = "admin"
    TECHNICIEN = "technicien"
    OPERATEUR = "operateur"
    SUPERVISEUR = "superviseur"

class PermissionEnum(str, Enum):
    """Permissions disponibles"""
    # Utilisateurs
    MANAGE_USERS = "manage_users"
    VIEW_USERS = "view_users"
    
    # Minigrids
    MANAGE_MINIGRIDS = "manage_minigrids"
    VIEW_MINIGRIDS = "view_minigrids"
    
    # Sites
    MANAGE_SITES = "manage_sites"
    VIEW_SITES = "view_sites"
    
    # Maintenance
    MANAGE_MAINTENANCE = "manage_maintenance"
    VIEW_MAINTENANCE = "view_maintenance"
    
    # Statistiques
    VIEW_STATISTICS = "view_statistics"
    
    # Alertes
    MANAGE_ALERTS = "manage_alerts"
    VIEW_ALERTS = "view_alerts"
    
    # Notifications
    SEND_NOTIFICATIONS = "send_notifications"

# Mapping des rôles aux permissions
ROLE_PERMISSIONS = {
    RoleEnum.ADMIN: [
        # Admin a accès à tout
        PermissionEnum.MANAGE_USERS,
        PermissionEnum.VIEW_USERS,
        PermissionEnum.MANAGE_MINIGRIDS,
        PermissionEnum.VIEW_MINIGRIDS,
        PermissionEnum.MANAGE_SITES,
        PermissionEnum.VIEW_SITES,
        PermissionEnum.MANAGE_MAINTENANCE,
        PermissionEnum.VIEW_MAINTENANCE,
        PermissionEnum.VIEW_STATISTICS,
        PermissionEnum.MANAGE_ALERTS,
        PermissionEnum.VIEW_ALERTS,
        PermissionEnum.SEND_NOTIFICATIONS,
    ],
    RoleEnum.SUPERVISEUR: [
        # Superviseur : gestion complète sauf utilisateurs
        PermissionEnum.VIEW_USERS,
        PermissionEnum.MANAGE_MINIGRIDS,
        PermissionEnum.VIEW_MINIGRIDS,
        PermissionEnum.MANAGE_SITES,
        PermissionEnum.VIEW_SITES,
        PermissionEnum.MANAGE_MAINTENANCE,
        PermissionEnum.VIEW_MAINTENANCE,
        PermissionEnum.VIEW_STATISTICS,
        PermissionEnum.MANAGE_ALERTS,
        PermissionEnum.VIEW_ALERTS,
        PermissionEnum.SEND_NOTIFICATIONS,
    ],
    RoleEnum.TECHNICIEN: [
        # Technicien : lecture et maintenance
        PermissionEnum.VIEW_USERS,
        PermissionEnum.VIEW_MINIGRIDS,
        PermissionEnum.VIEW_SITES,
        PermissionEnum.MANAGE_MAINTENANCE,
        PermissionEnum.VIEW_MAINTENANCE,
        PermissionEnum.VIEW_STATISTICS,
        PermissionEnum.VIEW_ALERTS,
    ],
    RoleEnum.OPERATEUR: [
        # Opérateur : lecture seulement
        PermissionEnum.VIEW_MINIGRIDS,
        PermissionEnum.VIEW_SITES,
        PermissionEnum.VIEW_MAINTENANCE,
        PermissionEnum.VIEW_STATISTICS,
        PermissionEnum.VIEW_ALERTS,
    ],
}
