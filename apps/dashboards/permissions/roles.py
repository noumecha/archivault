def is_superadmin(user):
    return user.role == "SUPERADMIN"

def is_admin(user):
    return user.role in ["SUPERADMIN", "ADMIN"]

def is_supervisor(user):
    return user.role == "SUPERVISEUR"
