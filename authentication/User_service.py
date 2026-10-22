from .models import User
from .services import EncryptionService


class UserService:

    def __init__(self):
        self.encryption = EncryptionService()

    def create_user(self, username, password, user_data):
        # Encrypt sensitive user data
        encrypted_data = self.encryption.encrypt_user_data(user_data)

        # Create user using Django ORM
        user = User(
            username=username,
            first_name=encrypted_data["first_name"],
            last_name=encrypted_data["last_name"],
            email=encrypted_data["email"],
            phone=encrypted_data["phone"],
            date_of_birth=encrypted_data["date_of_birth"],
            country=encrypted_data["country"],
            city=encrypted_data["city"],
            current_activity=encrypted_data["current_activity"],
        )

        # Django handles password hashing
        user.set_password(password)

        # Save encrypted data to database
        user.save()

        return user

    def get_user(self, user_id):
        # Retrieve user using Django ORM
        user = User.objects.get(id=user_id)

        # Decrypt data before returning it
        return {
            "id": user.id,
            "username": user.username,
            "first_name": self.encryption.decrypt(user.first_name),
            "last_name": self.encryption.decrypt(user.last_name),
            "email": self.encryption.decrypt(user.email),
            "phone": self.encryption.decrypt(user.phone),
            "date_of_birth": self.encryption.decrypt(user.date_of_birth),
            "country": self.encryption.decrypt(user.country),
            "city": self.encryption.decrypt(user.city),
            "current_activity": self.encryption.decrypt(
                user.current_activity
            ),
        }