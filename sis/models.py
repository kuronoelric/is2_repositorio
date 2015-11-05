#coding: utf-8
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Permission
from django.conf import settings
import math
from datetime import timedelta
from django.forms.fields import CharField
# Create your models here.


class MyUserManager(BaseUserManager):
    
    """Clase utilizada para la creacion de managers personalizados 
    de clase de usuarios tambien personalizados, herada metodos y atributos
    de la clase abstracta BaseUserManager que exige redefinir los metodos
    create_user y create_superuser"""
    def create_user(self, username, email, password=None):
        """
        Crea y guarda un usuario con el nombre de usuario , email y contraseña
        dados
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
    """Clase que representa usuario del modulo de autenticacion personalizada con mas atributos, hereda
    metodos y atributos de la clase abstracta AbstractBaseUser, especifica la confguracion 
    de sus instancias en USERNAME_FIELDS y los atributos requeridos en create_user y create_superuser
    en REQUIRED_FIELDS, ademas redefine metodos: get_full_name(),get_short_name(),has_perm(),
    has_module_perms(),is_staff()"""
    username = models.CharField(unique = True, max_length = 50)
    user_name = models.CharField(max_length = 50, verbose_name='Nombre')
    last_name = models.CharField(max_length = 50, verbose_name='Apellido')
    email = models.EmailField(max_length = 50)
    cedula = models.IntegerField(null = True)
       
    is_active = models.BooleanField(default = True, verbose_name='Activo')
    is_admin = models.BooleanField(default = False, verbose_name='Administrador')
    
    USERNAME_FIELD = 'username'  #indica que username es la clave primaria
    REQUIRED_FIELDS = ['email']
    
    objects = MyUserManager()
    
    class Meta: 
        verbose_name_plural = "Usuarios"
        verbose_name='usuario'
        
    
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




class Actividades(models.Model):
    """Modelo de las actividades de un flujo relacionada a su proyecto"""
    nombre = models.CharField(max_length = 200)
    descripcion = models.CharField(max_length = 200)
    
    class Meta: 
        verbose_name_plural = "Actividades" 
        verbose_name = 'actividad'
    
    
    def __unicode__(self):
        """Representacion unicode del objeto actividad"""
        return str(self.id)  + " - " + self.nombre



    
class Flujo(models.Model):
    """Modelo de flujos de proyecto relacionados a su respectivo proyecto"""
    
    #ESTADO_CHOICES = (
    #    ('CAN', 'Cancelado'),
    #    ('ACT', 'Activo'),
    #)
     
    nombre = models.CharField(max_length = 200)
    #estado = models.CharField(max_length = 3, choices = ESTADO_CHOICES)
    actividades = models.ManyToManyField(Actividades)
    orden_actividades = models.TextField(null=True)
    def __unicode__(self):
        """Representacion unicode del objeto flujo"""
        return self.nombre




class Proyecto(models.Model):
    """Modelo que representa los proyectos creados"""
    
    ESTADOS = (
        ('PEN', 'Pendiente'),
        ('ACT', 'Activo'),
        ('CAN', 'Cancelado'),
        ('FIN', 'Finalizado'),
    )
    
    nombre = models.CharField(max_length = 200)
    descripcion = models.CharField(max_length = 200)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    duracion = models.IntegerField()
    cantidad_dias_transcurridos=models.IntegerField()
    estado = models.CharField(max_length = 3, choices = ESTADOS)
    flujos = models.ManyToManyField(Flujo)
    
    def __unicode__(self):
        """Representacion unicode del objeto proyecto"""
        return self.nombre
    
    def get_fecha_inicio(self):
        return str(self.fecha_inicio)[:10]
    
    def get_fecha_fin(self):
        return str(self.fecha_fin)[:10]




class Rol(models.Model):
    """Modelo que representa los roles, esta relacionado a la tabla de permisos"""

    permisos= models.ManyToManyField(Permission)
    nombre_rol = models.CharField(max_length = 200)
    descripcion = models.CharField(max_length = 200)
    
    class Meta: 
        verbose_name_plural = "Roles" 
    
    
    def tiene_permiso(self,perm):
        """Verifica si un rol esta compuesto por un determinado permiso"""
        permiso= Permission.objects.get(name=perm)
        if permiso in self.permisos.all():
            return True
        else:
            return False

    def __unicode__(self):
        """Representacion unicode del objeto rol"""
        return self.nombre_rol





class Horas_Trabajadas(models.Model):
    """
    Modelo representa la descripcion de cada hora de trabajo agregada mostrando de la fecha de la misma
    """
    horas_trabajadas=models.FloatField()  
    descripcion_horas_trabajadas=models.CharField(max_length = 500)
    fecha=models.DateTimeField()
    actividad=models.CharField(max_length = 200)
    estado=models.CharField(max_length = 200)

    
    def __unicode__(self):
        """Representacion unicode del objeto HU_descripcion"""
        return str(self.id)  


  
  
    
class HU(models.Model):
    """Modelo que reprenseta las historias de usuario"""
    VALORES100_CHOICES = zip(range(1,101), range(1,101))
    VALORES10_CHOICES = zip(range(1,11), range(1,11))

    ESTADO_CHOICES = (
        ('CAN', 'Cancelado'),
        ('ACT', 'Activo'),
    )
    
    ESTADO_ACTIVIDAD_CHOICES = (
        ('PEN', 'Pendiente'),
        ('PRO', 'En Progreso'),
        ('FIN', 'Finalizado'),
        ('APR', 'Aprobado'),
    ) 
    
    descripcion = models.CharField(max_length = 200)
    valor_negocio = models.IntegerField(choices = VALORES10_CHOICES)
    valor_tecnico = models.IntegerField(choices = VALORES10_CHOICES)
    prioridad = models.IntegerField(choices = VALORES100_CHOICES)
    duracion = models.FloatField()
    acumulador_horas = models.FloatField()
    estado = models.CharField(max_length = 3, choices = ESTADO_CHOICES)
    actividad=models.ForeignKey(Actividades, null=True, blank=True)
    estado_en_actividad = models.CharField(max_length = 3, choices = ESTADO_ACTIVIDAD_CHOICES)
    proyecto=models.ForeignKey(Proyecto) #este campo va indicar a que proyecto pertenece asi en la vista ya no tenemos que hacer hu.objects.all()
    valido=models.BooleanField(default=False) # rl productOwner debe validar
    hu_descripcion=models.ManyToManyField(Horas_Trabajadas)

    
    
    def __unicode__(self):
        """Representacion unicode del objeto HU"""
        return self.descripcion
    

    
    def sprint(self):
        """ Funcion que retorna el sprint de una hu """
        id=0
        sprint=None
        for a in Sprint.objects.filter(proyecto=self.proyecto):
            for h in a.hu.all():
                if self.id == h.id:
                    if a.id > id:
                        sprint=a
                        id=a.id
        return sprint
    
    def flujo(self):
        """ Funcion que retorna el flujo de una hu """
        for a in AsignaHU_flujo.objects.all():
            for h in a.lista_de_HU.all():
                if self.id == h.id:
                    return a.flujo_al_que_pertenece
        return None
    
    def saber_usuario(self): 
        """ Funcion que retorna el usuario de una hu """
        for d in AsignaHU_Usuario.objects.all():
            if self.id == d.hu.id:
                return d.usuario
        return None
    
    
    def dias_hu(self, duracion):
        
        round_up = lambda num: int(num + 1) if int(num) != num else int(num)
        dias=round_up(duracion/8)
        return dias
    
    def saber_duracion_dias(self):
        return math.ceil(self.duracion/8)




class archivoadjunto(models.Model):
    """ Representacion de una archivo adjunto """
    ESTADO_CHOICES = (
        ('CAN', 'Cancelado'),
        ('ACT', 'Activo'),
    )
    
    nombre=models.CharField(max_length = 200)
    content=models.CharField(max_length = 200)
    archivo=models.BinaryField()
    tamanho=models.IntegerField()
    hU=models.ForeignKey(HU)
    estado = models.CharField(max_length = 3, choices = ESTADO_CHOICES)

    
    def __unicode__(self):
        """Representacion unicode del objeto archivoadjunto"""
        return self.archivo.nombre





class AsignarRolProyecto(models.Model):
    """Modelo que especifica una asignacion de un rol a un usuario en un proyecto"""
    usuario=models.ForeignKey(MyUser)
    rol=models.ForeignKey(Rol)    
    proyecto=models.ForeignKey(Proyecto)
    
    class Meta: 
        verbose_name_plural = "Asignar rol x proyecto" 
        verbose_name = 'rol x proyecto'
        
    def __unicode__(self):
        """Representacion unicode del objeto asignacion"""
        return str(self.id)+" - "+str(self.usuario)+" - "+str(self.rol)+" - "+str(self.proyecto) 
    




class Sprint(models.Model):
    """Modelo que reprenseta los Spring de un proyecto relacionados a
    sus respectivos proyectos mediante un foreign key"""
    
    ESTADO_CHOICES = (
        ('CAN', 'Cancelado'),
        ('ACT', 'Activo'),
        ('CON', 'Consulta'),
        ('FIN', 'Finalizado')
    )
     
    descripcion = models.CharField(max_length = 200)
    hu=models.ManyToManyField(HU)
    fecha_inicio = models.DateTimeField()
    duracion = models.FloatField()
    estado = models.CharField(max_length = 3, choices = ESTADO_CHOICES)
    proyecto=models.ForeignKey(Proyecto)
    flujo=models.ManyToManyField(Flujo)
    equipo=models.ManyToManyField(MyUser)
    
    def __unicode__(self):
        """Representacion unicode del objeto Sprint"""
        return self.descripcion
    
    def get_fecha_inicio(self):
        return str(self.fecha_inicio)[:10]
    
    def termino_Sprint(self):
        """Funcion que representa el termino de un sprint retornando True o False"""
        suma=0
        terminaron=True
        for h in self.hu.all():
            suma=suma+h.acumulador_horas
            if h.estado_en_actividad != 'FIN':
                terminaron=False
        if float(suma/8) >= self.duracion or terminaron:
            return True
        else:
            return False



class AsignaHU_Usuario(models.Model):
    """Modelo que especifica una delegacion de una HU a un usuario en un proyecto"""
    usuario=models.ForeignKey(settings.AUTH_USER_MODEL)
    hu=models.ForeignKey(HU)
    def __unicode__(self):
        """Representacion unicode del objeto delegacion"""
        return str(self.id)+" - "+str(self.usuario)+" - "+str(self.hu.descripcion)+" - "+str(self.hu.proyecto)



class AsignaHU_flujo(models.Model):
    """Modelo intermedio para la relacion varios a varios del modelo flujo con actividades"""
    lista_de_HU = models.ManyToManyField(HU)
    flujo_al_que_pertenece = models.ForeignKey(Flujo)
    def __unicode__(self):
        """Representacion unicode del objeto asignaHU_actividad_flujo"""
        return str(self.id)+" - "+str(self.flujo_al_que_pertenece)



