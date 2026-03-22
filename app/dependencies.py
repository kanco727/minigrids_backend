from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .db import get_db
from .models import Utilisateur
from .security import decode_access_token
from .enums import RoleEnum, PermissionEnum, ROLE_PERMISSIONS

security = HTTPBearer()


async def get_current_user(
    credentials=Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Utilisateur:
    """
    Récupère l'utilisateur actuel à partir du token JWT
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token manquant"
        )

    token = credentials.credentials

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré"
        )

    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide"
        )

    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiant utilisateur invalide dans le token"
        )

    stmt = select(Utilisateur).where(Utilisateur.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé"
        )

    if not user.actif:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Utilisateur désactivé"
        )

    return user


async def get_admin_user(
    current_user: Utilisateur = Depends(get_current_user)
) -> Utilisateur:
    """
    Vérifie que l'utilisateur actuel est un ADMIN
    """
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )
    return current_user


async def has_permission(
    permission: PermissionEnum,
    current_user: Utilisateur = Depends(get_current_user)
) -> Utilisateur:
    """
    Vérifie que l'utilisateur a une permission spécifique
    """
    role = RoleEnum(current_user.role)
    permissions = ROLE_PERMISSIONS.get(role, [])

    if permission not in permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission manquante: {permission}"
        )

    return current_user


def require_permission(permission: PermissionEnum):
    """
    Décorateur pour vérifier une permission spécifique
    """
    async def permission_checker(
        current_user: Utilisateur = Depends(get_current_user)
    ) -> Utilisateur:
        role = RoleEnum(current_user.role)
        permissions = ROLE_PERMISSIONS.get(role, [])

        if permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission manquante: {permission}"
            )

        return current_user

    return permission_checker


def require_role(*roles: RoleEnum):
    """
    Décorateur pour vérifier que l'utilisateur a un rôle parmi ceux spécifiés
    """
    async def role_checker(
        current_user: Utilisateur = Depends(get_current_user)
    ) -> Utilisateur:
        if not any(RoleEnum(current_user.role) == role for role in roles):
            role_names = ", ".join([r.value for r in roles])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rôle requis parmi: {role_names}"
            )

        return current_user

    return role_checker