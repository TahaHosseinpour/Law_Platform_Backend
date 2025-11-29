from enum import Enum


class UserRole(str, Enum):
    """User roles matching Prisma schema"""
    USER = "USER"
    LAWYER = "LAWYER"
    ADMIN = "ADMIN"


class Permission(str, Enum):
    """System permissions"""
    # User permissions
    VIEW_OWN_PROFILE = "view_own_profile"
    UPDATE_OWN_PROFILE = "update_own_profile"
    CREATE_CASE = "create_case"
    VIEW_OWN_CASES = "view_own_cases"

    # Lawyer permissions
    VIEW_ALL_CASES = "view_all_cases"
    UPDATE_LAWYER_PROFILE = "update_lawyer_profile"
    VIEW_LAWYER_PROFILES = "view_lawyer_profiles"

    # Admin permissions
    MANAGE_USERS = "manage_users"
    MANAGE_LAWYERS = "manage_lawyers"
    VIEW_ALL_DATA = "view_all_data"
    DELETE_USERS = "delete_users"


# Role-based permissions mapping
ROLE_PERMISSIONS: dict[UserRole, list[Permission]] = {
    UserRole.USER: [
        Permission.VIEW_OWN_PROFILE,
        Permission.UPDATE_OWN_PROFILE,
        Permission.CREATE_CASE,
        Permission.VIEW_OWN_CASES,
        Permission.VIEW_LAWYER_PROFILES,
    ],
    UserRole.LAWYER: [
        Permission.VIEW_OWN_PROFILE,
        Permission.UPDATE_OWN_PROFILE,
        Permission.CREATE_CASE,
        Permission.VIEW_OWN_CASES,
        Permission.VIEW_ALL_CASES,
        Permission.UPDATE_LAWYER_PROFILE,
        Permission.VIEW_LAWYER_PROFILES,
    ],
    UserRole.ADMIN: [
        # Admin has all permissions
        Permission.VIEW_OWN_PROFILE,
        Permission.UPDATE_OWN_PROFILE,
        Permission.CREATE_CASE,
        Permission.VIEW_OWN_CASES,
        Permission.VIEW_ALL_CASES,
        Permission.UPDATE_LAWYER_PROFILE,
        Permission.VIEW_LAWYER_PROFILES,
        Permission.MANAGE_USERS,
        Permission.MANAGE_LAWYERS,
        Permission.VIEW_ALL_DATA,
        Permission.DELETE_USERS,
    ],
}


def has_permission(user_role: UserRole, permission: Permission) -> bool:
    """Check if a role has a specific permission"""
    return permission in ROLE_PERMISSIONS.get(user_role, [])
