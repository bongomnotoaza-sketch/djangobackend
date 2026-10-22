from django.core.exceptions import ValidationError
from django.db import IntegrityError

from .User_service import UserService
from .username_service import UsernameService
from .validators import RegistrationValidator
from .verification_service import VerificationService

from filesystem.create_volume_service import CreateVolumeService
from filesystem.create_container_service import CreateContainerService
from filesystem.default_directory_service import DefaultDirectoryService


class RegistrationService:

    def __init__(self):
        self.user_service = UserService()
        self.username_service = UsernameService()
        self.verification_service = VerificationService()

        # NOTE: CreateVolumeService and CreateContainerService both need a
        # `user` instance to be constructed, but `user` doesn't exist until
        # step 4 below. They can't be built here in __init__ — they're now
        # constructed later, right where they're used (steps 5 and 6).

    def register(
        self,
        password,
        first_name,
        last_name,
        email,
        phone,
        date_of_birth,
        country,
        province,
        city,
        street,
        current_activity,
    ):

        # -----------------------------------------
        # 1. Generate username
        # -----------------------------------------

        username = self.username_service.generate_username(
            first_name=first_name,
            last_name=last_name,
        )

        # -----------------------------------------
        # 2. Prepare registration data
        # -----------------------------------------

        data = {
            "username": username,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "date_of_birth": date_of_birth,
            "country": country,
            "province": province,
            "city": city,
            "street": street,
            "current_activity": current_activity,
        }

        # -----------------------------------------
        # 3. Validate registration
        # -----------------------------------------

        RegistrationValidator.validate_registration(
            data
        )

        # -----------------------------------------
        # 4. Create user
        # -----------------------------------------

        try:

            user = self.user_service.create_user(
                username=username,
                password=password,
                user_data={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "phone": phone,
                    "date_of_birth": date_of_birth,
                    "country": country,
                    "province": province,
                    "city": city,
                    "current_activity": current_activity,
                },
            )

        except IntegrityError:

            raise ValidationError(
                "A user with this email already exists."
            )

        # -----------------------------------------
        # 5. Create filesystem volume
        # -----------------------------------------
        # Constructed here (not in __init__) because it requires `user`,
        # which only exists after step 4.

        create_volume_service = CreateVolumeService(user)
        create_volume_service.create()

        # -----------------------------------------
        # 6. Create filesystem container
        # -----------------------------------------
        # Same reasoning as step 5 — needs `user`, so built here.

        create_container_service = CreateContainerService(user)
        create_container_service.create()

        # -----------------------------------------
        # 7. Create default directories
        # -----------------------------------------

        default_directory_service = DefaultDirectoryService(
            user
        )

        default_directory_service.create_default_directories()

        # -----------------------------------------
        # 8. Send verification email
        # -----------------------------------------

        self.verification_service.send_verification_email(
            user
        )

        # -----------------------------------------
        # 9. Return user
        # -----------------------------------------

        return user