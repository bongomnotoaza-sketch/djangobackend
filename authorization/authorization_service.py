class AuthorizationService:

    @staticmethod
    def authorize(request):
        user = request.user

        if not user.is_authenticated:
            return {
                "authenticated": False,
                "user": None,
            }

        return {
            "authenticated": True,
            "user": user,
        }