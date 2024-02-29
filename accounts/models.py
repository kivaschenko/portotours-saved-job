from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _


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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    stripe_customer_id = models.CharField(max_length=220, blank=True, null=True)
    name = models.CharField(_("name"), max_length=120, blank=True, null=True, help_text="Card name")
    email = models.EmailField(unique=True, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    # address
    address_city = models.CharField(max_length=160, blank=True, null=True)
    address_country = models.CharField(max_length=2, blank=True, null=True)
    address_line1 = models.CharField(max_length=160, blank=True, null=True)
    address_line2 = models.CharField(max_length=160, blank=True, null=True)
    address_postal_code = models.CharField(max_length=10, blank=True, null=True)
    address_state = models.CharField(max_length=60, blank=True, null=True)
    # shipping address
    shipping_address_city = models.CharField(max_length=160, blank=True, null=True)
    shipping_address_country = models.CharField(max_length=2, blank=True, null=True)
    shipping_address_line1 = models.CharField(max_length=160, blank=True, null=True)
    shipping_address_line2 = models.CharField(max_length=160, blank=True, null=True)
    shipping_address_postal_code = models.CharField(max_length=10, blank=True, null=True)
    shipping_address_state = models.CharField(max_length=60, blank=True, null=True)
    shipping_phone = models.CharField(max_length=20, blank=True, null=True)
    shipping_name = models.CharField(max_length=160, blank=True, null=True)

    # local
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Profile: {self.id} | {self.name}>"
