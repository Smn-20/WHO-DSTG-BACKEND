from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# Create your models here.



class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name




class UserManager(BaseUserManager):
    def create_user(self,email, names,password=None,is_active=True,is_staff=False,is_admin=False):
        if not email:
            raise ValueError('Users must have a valid email')
        if not password:
            raise ValueError("You must enter a password")
        
        email=self.normalize_email(email)
        user_obj=self.model(email=email)
        user_obj.names = names
        user_obj.set_password(password)
        user_obj.staff=is_staff
        user_obj.admin=is_admin
        user_obj.active=is_active
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self,email, names="",password=None):
        user=self.create_user(email, names, password=password,is_staff=True)
        return user

    def create_superuser(self,email, names="",password=None):
        user=self.create_user(email, names, password=password, is_staff=True, is_admin=True)
        return user
        

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255,unique=True)
    names = models.CharField(max_length=255, null=True, blank=True)
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


class Department(models.Model):
    name = models.CharField(max_length=250, unique=True)
    
    def __str__(self):
        return str(self.id) + '-' +self.name
        

class Condition(models.Model):
    name = models.CharField(max_length=255,unique=True)
    department = models.ForeignKey(Department, null= True,blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class Attribute(models.Model):
    condition = models.ForeignKey(Condition, related_name='attributes', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return f"{self.title} for {self.condition.name}"


class AttributeImage(models.Model):
    class ImageType(models.TextChoices):
        TABLE = "TABLE", "Table"
        FIGURE = "FIGURE", "Figure"

    attribute = models.ForeignKey(Attribute, related_name='images', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True, choices=ImageType.choices)
    image = models.ImageField(upload_to='attribute_images/')


class Symptoms(models.Model):
    name = models.CharField(max_length=250, unique=True)
    conditions = models.ManyToManyField(Condition,blank=True)
    further_management = models.TextField(null=True, blank=True)
    referral_criteria = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return str(self.id) + '-' +self.name


class ForumPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts', null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)  # For anonymous users
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='department_post')
    condition = models.ForeignKey(Condition, on_delete=models.CASCADE, related_name='condition_post')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username or self.user.email}'s post"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)  # For anonymous users
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes', null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)  # For anonymous likes
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_user_like'),
            models.UniqueConstraint(fields=['username', 'post'], name='unique_anon_like')
        ]

