from django.contrib.auth.base_user import BaseUserManager


class AuthUserManager(BaseUserManager):
    def create_user(self, email, phone_number, first_name, username=None, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not phone_number:
            raise ValueError('Users must have an phone_number')
        if not first_name:
            raise ValueError('Users must have an first_name')

        self._check_unique_email(email)

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            phone_number=phone_number,
            first_name=first_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number, first_name, password, username):
        user = self.create_user(
            email=email,
            password=password,
            username=username,
            phone_number=phone_number,
            first_name=first_name
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

    def get_by_email(self, email):
        return self.get_queryset().get(email=email)

    def _check_unique_email(self, email):
        try:
            self.get_queryset().get(email=email)
            raise ValueError("This email is already registered")
        except self.model.DoesNotExist:
            return True
