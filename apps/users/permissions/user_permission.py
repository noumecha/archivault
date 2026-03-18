from config.roles import *
class UserPermission:
    @staticmethod
    def can_manage_user(current_user, target_user):

        if is_admin(current_user) or is_superadmin(current_user):
            return True

        if is_superviseur(current_user):
            return target_user.cellule == current_user.cellule

        return False
