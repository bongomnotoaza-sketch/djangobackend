class UpdateUserInfoPermissionService:

    @staticmethod
    def can_update(user, target_user):
        
        if not user.is_authenticated:
            return False

        if user.id != target_user.id:
            return False

        return True