from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.


class MyUserManager(BaseUserManager):
    
    def create_user(self, username, email, password=None):
        """
        Para crear un usuario no admin
        """
        if not username:
            raise ValueError('Los usuarios deben tener un nombre de usuario')

        user = self.model(
            username=username,
            email= email,            
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        """
        Crea y guarda un superuser con el nombre de usuario, email y password
        dados
        """
        user = self.create_user(username,
            password=password,
            email= email,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user




class MyUser(AbstractBaseUser):
    username = models.CharField(unique = True, max_length = 50)
    user_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    email = models.EmailField(max_length = 50)
    cedula = models.IntegerField(null = True)
    
    is_active = models.BooleanField(default = True)
    is_admin = models.BooleanField(default = False)
    
    USERNAME_FIELD = 'username'  #indica que username es la clave primaria
    REQUIRED_FIELDS = ['email']
    
    objects = MyUserManager()
    
    
    def create(self,username,email,password,user_name, last_name, cedula):
        """Metodo para la creacion de usuarios desde interfaz web completando todos los 
        atributos"""
        usuario=MyUser.objects.create_user(username, email, password=None)
        usuario.last_name=last_name
        usuario.user_name=user_name
        usuario.cedula = cedula
        return usuario
        

    def get_full_name(self):
        """Retorna el nombre y apellido del usuario"""
        # The user is identified by their email address
        return self.user_name+self.last_name

    def get_short_name(self):
        """Retorna el username identificador del usuario"""
        # The user is identified by their email address
        return self.username

    def __unicode__(self):
        """Representacion unicode del objeto usuario"""
        return self.username

    def has_perm(self, perm, obj=None):
        "Por implementar: Retornara true si un usuario tiene el permiso indicado como argumento"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Por implementar: Retornarea true si el usuario tiene permiso de acceder a una 
        applicacion particular"""
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Retorna true si el usuario es administrador"
        # Simplest possible answer: All admins are staff
        return self.is_admin


        
    
     





