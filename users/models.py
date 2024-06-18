from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# Create your models here.



class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name




class UserManager(BaseUserManager):
    def create_user(self,email,password=None,is_active=True,is_staff=False,is_admin=False):
        if not email:
            raise ValueError('Users must have a valid email')
        if not password:
            raise ValueError("You must enter a password")
        
        email=self.normalize_email(email)
        user_obj=self.model(email=email)
        user_obj.set_password(password)
        user_obj.staff=is_staff
        user_obj.admin=is_admin
        user_obj.active=is_active
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self,email,password=None):
        user=self.create_user(email,password=password,is_staff=True)
        return user

    def create_superuser(self,email,password=None):
        user=self.create_user(email,password=password,is_staff=True,is_admin=True)
        return user
        

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255,unique=True)
    roles = models.ManyToManyField(Role,blank=True)
    active=models.BooleanField(default=True)
    staff=models.BooleanField(default=False)
    admin=models.BooleanField(default=False)

    objects= UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS=[]

    def __str__(self):
        return self.email

    def has_perm(self,perm,obj=None):
        return True

    def has_module_perms(self,app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active


class Condition(models.Model):
    name = models.CharField(max_length=250, unique=True)
    description = models.TextField(null=True, blank=True)
    causes = models.TextField(null=True, blank=True)
    symptoms_features = models.TextField(null=True, blank=True)
    investigations = models.TextField(null=True, blank=True)
    treatments = models.TextField(null=True, blank=True)
    surgical_options = models.TextField(null=True, blank=True)
    preventive_measures = models.TextField(null=True, blank=True)
    emergency_management = models.TextField(null=True, blank=True)
    referral_criteria = models.TextField(null=True, blank=True)
    prognosis = models.TextField(null=True, blank=True)
    def __str__(self):
        return str(self.id) + '-' +self.name


class Symptoms(models.Model):
    name = models.CharField(max_length=250, unique=True)
    conditions = models.ManyToManyField(Condition,blank=True)
    further_management = models.TextField(null=True, blank=True)
    referral_criteria = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return str(self.id) + '-' +self.name
