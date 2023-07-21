from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.utils.translation import gettext_lazy as _
import uuid
# from django.utils import timezone
# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self,email,password=None,**extra_fields):
        if not email:
            raise ValueError('email is required')
        email=self.normalize_email(email)
        user=self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self,email,password=None,**extra_fields):

        extra_fields.setdefault('is_staff' , True)
        extra_fields.setdefault('is_superuser',True)
        return self.create_user(email,password,**extra_fields)

class CustomUser(AbstractBaseUser,PermissionsMixin):
    id=models.UUIDField(default=uuid.uuid4,primary_key=True,editable=False,db_index=True)
    email=models.EmailField(_('Email'),unique=True)
    username=models.CharField(max_length=50,unique=True)
    is_active=models.BooleanField(default=True)
    is_staff=models.BooleanField(default=False)
    is_superuser=models.BooleanField(default=False)
    date_joined=models.DateTimeField(auto_now_add=True)


    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username']

    objects=CustomUserManager()

    def __str__(self) -> str:
        return str(self.username)