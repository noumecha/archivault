def is_admin(user):
    return user.role in ["SUPERADMIN", "ADMIN"]

def is_supervisor(user):
    return user.role == "SUPERVISEUR"
