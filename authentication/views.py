import json
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.core.exceptions import ValidationError
from django.core.cache import cache
from .services import EncryptionService
from .login_service import LoginService
from .registration_service import RegistrationService
from .verification_service import VerificationService
from .password_recovery_service import PasswordRecoveryService
from .password_reset_service import PasswordResetService
from .update_info_service import UpdateInfoService
from .logout_service import LogoutService

logger = logging.getLogger("authentication")

# Rate limiting configuration
LOGIN_RATE_LIMIT = 5
LOGIN_RATE_WINDOW = 60


def _get_client_ip(request):
    """Extract client IP address from request."""
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _is_rate_limited(request, username):
    """Throttle on IP + username combined."""
    ip = _get_client_ip(request)
    key = f"login_attempts:{ip}:{username}"
    attempts = cache.get(key, 0)
    if attempts >= LOGIN_RATE_LIMIT:
        return True
    cache.set(key, attempts + 1, timeout=LOGIN_RATE_WINDOW)
    return False


def register_page(request):
    return render(request, "authentication/register.html")


def password_reset_page(request):
    return render(request, "authentication/password_reset_page.html")


# Ensure CSRF cookie is set when loading the login page
@ensure_csrf_cookie
def login_page(request):
    """Render login page with CSRF cookie set."""
    return render(request, "authentication/login.html")


# Endpoint to get CSRF token for AJAX requests - FIXED
@ensure_csrf_cookie
@require_GET
def get_csrf_token(request):
    """Return CSRF token for AJAX requests."""
    token = get_token(request)
    return JsonResponse({
        "csrfToken": token
    })


@require_POST
def login_view(request):
    """
    Handle user login with rate limiting.
    
    Expects JSON body with 'username' and 'password' fields.
    Returns user data on success, error message on failure.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400
        )

    required_fields = ["username", "password"]
    missing_fields = [
        field for field in required_fields
        if field not in data
    ]

    if missing_fields:
        return JsonResponse(
            {
                "error": "Missing required fields",
                "fields": missing_fields,
            },
            status=400
        )

    username = data["username"]
    client_ip = _get_client_ip(request)

    if _is_rate_limited(request, username):
        logger.warning(
            "Login rate limit exceeded for username=%s ip=%s",
            username, client_ip,
        )
        return JsonResponse(
            {"error": "Too many login attempts. Please try again later."},
            status=429
        )

    try:
        login_service = LoginService()

        user = login_service.login_user(
        request=request,
        username=username,
        password=data["password"],
        )
    except ValidationError as e:
        logger.info(
            "Failed login attempt for username=%s ip=%s",
            username, client_ip,
        )
        return JsonResponse(
            {"error": e.messages[0] if hasattr(e, "messages") else str(e)},
            status=401
        )

    # Successful login clears the throttle counter for this ip+username pair
    cache.delete(f"login_attempts:{client_ip}:{username}")

    logger.info("Successful login for username=%s ip=%s", username, client_ip)

    return JsonResponse(
        {
            "message": "Login successful",
            "user_id": user.id,
            "username": user.username,
        },
        status=200
    )
    

def current_user(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {
                "authenticated": False,
                "error": "Authentication required",
            },
            status=401,
        )

    user = request.user
    encryption = EncryptionService()

    return JsonResponse(
        {
            "authenticated": True,
            "user": {
                "username": user.username,
                "first_name": encryption.decrypt(user.first_name),
                "last_name": encryption.decrypt(user.last_name),
                "email": encryption.decrypt(user.email),
                "phone": encryption.decrypt(user.phone),
                "date_of_birth": encryption.decrypt(user.date_of_birth),
                "country": encryption.decrypt(user.country),
                "province": encryption.decrypt(user.province) if user.province else "",
                "city": encryption.decrypt(user.city),
                "street": encryption.decrypt(user.street) if user.street else "",
                "current_activity": encryption.decrypt(user.current_activity),
                "role": user.role,
                "email_verified": user.email_verified,
            },
        }
    )

@require_POST
def register(request):
    """Handle user registration."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400
        )

    required_fields = [
        "password",
        "first_name",
        "last_name",
        "email",
        "phone",
        "date_of_birth",
        "country",
        "province",
        "city",
        "street",
        "current_activity",
    ]

    missing_fields = [
        field for field in required_fields
        if field not in data
    ]

    if missing_fields:
        return JsonResponse(
            {
                "error": "Missing required fields",
                "fields": missing_fields,
            },
            status=400
        )

    registration_service = RegistrationService()

    try:
        user = registration_service.register(
            password=data["password"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            phone=data["phone"],
            date_of_birth=data["date_of_birth"],
            country=data["country"],
            province=data["province"],
            city=data["city"],
            street=data["street"],
            current_activity=data["current_activity"],
        )
    except ValidationError as e:
        return JsonResponse(
            {
                "error": (
                    e.messages[0]
                    if hasattr(e, "messages")
                    else str(e)
                )
            },
            status=400
        )

    return JsonResponse(
        {
            "message": (
                "Registration successful. "
                "Please check your email to verify your account."
            ),
            "user_id": user.id,
            "email_verified": user.email_verified,
        },
        status=201
    )


@require_GET
def verify_email(request):
    """Verify the user's email address."""
    token = request.GET.get("token")

    if not token:
        return JsonResponse(
            {"error": "Verification token is required."},
            status=400
        )

    verification_service = VerificationService()

    try:
        verified = verification_service.verify_email(token)
    except Exception:
        return JsonResponse(
            {"error": "Unable to process verification."},
            status=500
        )

    if not verified:
        return JsonResponse(
            {"error": "Invalid or expired verification token."},
            status=400
        )

    return JsonResponse(
        {
            "message": (
                "Email verified successfully. "
                "Your username has been sent to your email."
            )
        },
        status=200
    )


@require_POST
def password_recovery(request):
    """Handle password recovery requests."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400
        )

    if "username" not in data:
        return JsonResponse(
            {"error": "Username is required."},
            status=400
        )

    username = data["username"]
    recovery_service = PasswordRecoveryService()

    try:
        user = recovery_service.get_user(username)
        recovery_service.send_password_recovery_email(user)
    except ValidationError:
        # Do not reveal whether the username exists or email is verified
        pass

    return JsonResponse(
        {
            "message": (
                "If the account exists and has a verified "
                "email address, password recovery "
                "instructions have been sent."
            )
        },
        status=200
    )


@require_POST
def password_reset(request):
    """Reset a user's password using their temporary password."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400
        )

    required_fields = [
        "username",
        "temporary_password",
        "new_password",
        "confirm_password",
    ]

    missing_fields = [
        field for field in required_fields
        if field not in data
    ]

    if missing_fields:
        return JsonResponse(
            {
                "error": "Missing required fields",
                "fields": missing_fields,
            },
            status=400
        )

    password_reset_service = PasswordResetService()

    try:
        password_reset_service.reset_password(
            username=data["username"],
            temporary_password=data["temporary_password"],
            new_password=data["new_password"],
            confirm_password=data["confirm_password"],
        )
    except ValidationError:
        return JsonResponse(
            {"error": "Unable to reset password."},
            status=400
        )

    return JsonResponse(
        {"message": "Password reset successfully."},
        status=200
    )


@require_POST
def update_info(request):
    """Update the authenticated user's information."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON."},
            status=400
        )

    if not data:
        return JsonResponse(
            {"error": "No information was provided for update."},
            status=400
        )

    try:
        user = UpdateInfoService().update_info(
            request.user,
            **data
        )
    except ValidationError as error:
        return JsonResponse(
            {"error": str(error)},
            status=400
        )

    return JsonResponse(
        {
            "message": "User information updated successfully.",
            "user_id": user.id,
        },
        status=200
    )


@require_POST
def logout(request):
    """Logout the authenticated user."""
    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "Authentication required."},
            status=401
        )

    LogoutService().logout_user(request)

    return JsonResponse(
        {"message": "Logged out successfully."},
        status=200
    )