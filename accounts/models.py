import random
import string

from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _

from PIL import Image


# CUSTOM USER
class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        user = self.model(username=email, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    def create_user_without_password(self, email, **extra_fields):
        """
        Create and save a user without a password.
        """
        password = self.make_random_password()  # Generate a random password
        return self._create_user(email, password, **extra_fields), password, True

    def make_random_password(self, length=10):
        """
        Generate a random password.
        """
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    def get_or_create_user(self, email, **extra_fields):
        """
        Get or create a user with the given email.
        If the user already exists, generate a new random password and update it.
        """
        try:
            user = self.get(email=email)
            # new_password = self.make_random_password()
            # user.set_password(new_password)
            # user.save()
            return user, '', False
        except self.model.DoesNotExist:
            return self.create_user_without_password(email, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True,
                              help_text=_(
                                  "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
                              ),
                              validators=[],  # TODO: Add custom Email validator here
                              error_messages={
                                  "unique": _("A user with that email already exists."),
                              },
                              )
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<User(id={self.id} email={self.email} first_name={self.first_name} last_name={self.last_name}...)>"


# PROFILE
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=60, unique=True, blank=True, null=True)
    name = models.CharField(_("name"), max_length=120, blank=True, null=True, help_text="Card name")
    email = models.EmailField(unique=True, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    # address
    address_city = models.CharField(max_length=160, blank=True, null=True)
    address_country = models.CharField(max_length=2, blank=True, null=True, help_text="max 2 characters, for example: UK, DE")
    address_line1 = models.CharField(max_length=160, blank=True, null=True)
    address_line2 = models.CharField(max_length=160, blank=True, null=True)
    address_postal_code = models.CharField(max_length=10, blank=True, null=True)
    address_state = models.CharField(max_length=160, blank=True, null=True)

    # local
    created_at = models.DateTimeField(auto_now_add=True)
    # media
    avatar = models.ImageField(_("Avatar"), upload_to="avatars/", null=True, blank=True)

    def save(self, *args, **kwargs):
        # Resize avatar before saving
        if self.avatar:
            self.resize_avatar()
        super().save(*args, **kwargs)

    def resize_avatar(self):
        from PIL import Image, ImageOps
        from io import BytesIO
        from django.core.files.uploadedfile import InMemoryUploadedFile
        import sys

        # Open the avatar image
        img = Image.open(self.avatar)

        # Define maximum avatar size
        max_size = (300, 300)

        # Resize the avatar if it exceeds the maximum size
        if img.height > max_size[1] or img.width > max_size[0]:
            img.thumbnail(max_size, Image.LANCZOS)  # Use Image.LANCZOS for resizing

            # Create a BytesIO buffer to store the resized image
            buffer = BytesIO()
            img.save(buffer, format=img.format)

            # Create a new InMemoryUploadedFile instance with the resized image
            self.avatar = InMemoryUploadedFile(
                buffer, None, f"{self.avatar.name.split('.')[0]}_resized.{img.format.lower()}", 'image/jpeg',
                sys.getsizeof(buffer), None
            )

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Profile: {self.id} | {self.name}>"
