from django.test import TestCase
from sis.models import MyUser, Rol, Actividades, Flujo, Proyecto, AsignarRolProyecto, HU, Sprint
from sis.views import FormularioRolProyecto, proyectoFrom, FormularioFlujoProyecto, formularioActividad, HU
from django.test.client import RequestFactory
from django.contrib.auth.models import Permission
from django.utils import timezone
import datetime

class MyUserManagerTests(TestCase):

    def test_create_user_is_an_instance_of_User(self):
        """
        create_user() deberia retornar un objeto user con nombre de usuario,
        el email dado y contrasenha
        """
        usuario = MyUser.objects.create_user('testusuario', 'testusuario2@hotmail.com', 'pass123')
        self.assertEqual(isinstance(usuario, MyUser),True)
        print 'crear un usuario'
    def test_create_user_is_active_is_not_admin(self):
        """
        create_user() verificar si esta activo y no es admin
        """
        usuario = MyUser.objects.create_user('testusuario', 'testusuario2@hotmail.com', 'pass123')
        self.assertEqual(usuario.is_admin,False)
        self.assertEqual(usuario.is_active,True)
        print 'Verificar que el usuario creado esta activo pero no admin'
        
    def test_create_superuser_is_an_instance_of_User(self):
        """
        create_superuser() deberia retornar un objeto user con nombre de usuario,
        el email dado y contrasenha
        """
        usuario = MyUser.objects.create_superuser('testusuario','testusuario2@hotmail.com', 'pass123')
        self.assertEqual(isinstance(usuario, MyUser),True)
        print 'Crear usuario admin'
    def test_create_superuser_is_active_is_admin(self):
        """
        create_superuser() verificar si esta activo y no es admin
        """
        usuario = MyUser.objects.create_superuser('testusuario', 'testusuario2@hotmail.com', 'pass123')
        self.assertEqual(usuario.is_admin,True)
        self.assertEqual(usuario.is_active,True)
        print 'verificar que usuario admin esta activo y tiene permisos de admin'

class login_test(TestCase):        
        
    def test_login_valido(self):
        """ 
        Verifica que el login funcione correctamente, con un usuario creado
        """
        self.user = MyUser.objects.create_user('testusuario', 'testusuario2@hotmail.com', 'pass123') 
        self.user.set_password('1234') 
        self.user.save() 
        #self.user = authenticate(username='testuser', password='hello') 
        login = self.client.login(username='testusuario', password='1234') 
        self.assertTrue(login) 
        print 'Prueba de login con usuario Valido'
        
    def test_login_invalido(self):
        """
        Verifica que el login funcione correctamente, ingresando un usuario incorrecto
        """
        self.user = MyUser.objects.create_user('testusuario', 'testusuario2@hotmail.com', 'pass123') 
        self.user.set_password('1234') 
        self.user.save() 
        #self.user = authenticate(username='testuser', password='hello') 
        login = self.client.login(username='testusuario', password='pass1234') 
        self.assertFalse(login)
        print 'Prueba de login con usuario Invalido'
  

  
  
class RolTest(TestCase):
    
    def create_rol(self):
        return Rol.objects.create( nombre_rol="nuevoRol", descripcion="nuevo_rol")
        
    def test_rol_creation(self):
        """Test que prueba la creacion de rol"""
        w=self.create_rol()
        self.assertTrue(isinstance(w, Rol))
        self.assertEqual(w.__unicode__(), w.nombre_rol)
        print 'Crear un rol'
    def setUp(self):
        self.factory=RequestFactory
        self.rol=Rol.objects.create(nombre_rol="nuevoRol", descripcion="nuevo_rol")
        
    
    def test_modificarRol(self):
        """Test que prueba la modificacion de rol en uno de sus parametros"""
        w=self.create_rol()
        w.descripcion='rol_cambiado'
        w.save()
        self.assertEqual(w.descripcion, 'rol_cambiado')
        print 'Modificar un rol'
    def test_dato_invalido(self):
        """Test que prueba el ingreso invalido de uno de los datos del rol"""
        w=self.create_rol()
        w.descripcion='rol_cambiado'
        w.save()
        self.assertNotEqual(w.descripcion, 'nuevo_rol')
        print 'Verificar que el rol fue modificado' 
          
class ActividadesTest(TestCase):
    def create_Actividades(self, nombre="nuevaActividad", descripcion="nuevo Actividad" ):
        return Actividades.objects.create(nombre=nombre, descripcion=descripcion)
    
    def test_Actividad_creation(self):
        """Test que prueba la creacion de una acividad"""
        w=self.create_Actividades()
        self.assertTrue(isinstance(w, Actividades))
        self.assertEqual(w.__unicode__(), str(w.id)  + " - " + w.nombre)
        print 'Crear una actividad'
        
    def test_valid_formularioActividad(self):
        """Test que prueba el formulario de una acividad"""
        w = Actividades.objects.create(nombre="nuevaActividad", descripcion='nueva Actividad' )
        data = {'nombre':w.nombre, 'descripcion':w.descripcion,}
        form = formularioActividad(data=data)
        self.assertTrue(form.is_valid())
        
        
    def test_invalid_formularioActividad(self):
        """Test que prueba que el formulario de una acividad es invalido"""
        w = Actividades.objects.create(nombre="nuevaActividad", descripcion='nueva Actividad' )
        data = {'nombre':w.nombre,}
        form = formularioActividad(data=data)
        self.assertFalse(form.is_valid())
        
      
    def test_modificarActividad(self):
        """Test que prueba la modificacion de una acividad"""
        w=self.create_Actividades()
        w.nombre='actividad_prueba'
        w.save()
        self.assertEqual(w.nombre, 'actividad_prueba')
        print 'Modificar una actividad'
        
class FlujoTest(TestCase):
    def create_Flujo(self, nombre="1nuevoFlujo"):
        return Flujo.objects.create(nombre=nombre)
    
    def test_Flujo_creation(self):
        """Test que prueba la creacion de un flujo"""
        w=self.create_Flujo()
        self.assertTrue(isinstance(w, Flujo))
        print 'Crear un flujo'
       
class proyectoTest(TestCase):
    
    def create_proyecto(self):
        return Proyecto(nombre="P9", descripcion="proyecto9", fecha_inicio=timezone.now(), fecha_fin=datetime.timedelta(days=1), estado="PEN")
    
    def test_proyecto_creation(self):
        """Test que prueba la creacion de un proyecto"""
        w=self.create_proyecto()
        self.assertTrue(isinstance(w, Proyecto))
        self.assertEqual(w.__unicode__(), w.nombre)
        print 'Crear un proyecto'

class asignacionTest(TestCase):
    def create_proyecto(self):
        return Proyecto.objects.create(nombre="P9", descripcion="proyecto9", fecha_inicio="2015-03-31 00:00:00-04", fecha_fin="2015-03-31 00:00:00-04" ,estado="PEN" ,duracion=10,cantidad_dias_transcurridos=0)
        
    def create_rol(self):
        return Rol.objects.create( nombre_rol="nuevoRol", descripcion="nuevo_rol")

    def create_asignacion(self):
        usuario=MyUser.objects.create_user('anonimo','anonimo2@hotmail.com', '1234')
        rol=self.create_rol()
        proyecto=self.create_proyecto()
        return AsignarRolProyecto.objects.create(usuario=usuario, rol=rol, proyecto=proyecto)
        
    def test_asignacion_creation(self):
        """Test que prueba la asignacion de usuario"""
        w=self.create_asignacion()
        self.assertEqual(w.usuario.username, 'anonimo')
        print 'Asignar un usuario a un proyecto'
        
class huTest(TestCase):
    def create_hu(self, descripcion="hu", valor_negocio="7", valor_tecnico="0", prioridad="0", duracion="0", acumulador_horas="0", estado="ACT", estado_en_actividad="PEN", valido="FALSE", proyecto_id="1"):
            return HU.objects.create(descripcion=descripcion, valor_negocio=valor_negocio, valor_tecnico=valor_tecnico, prioridad=prioridad, duracion=duracion, acumulador_horas=acumulador_horas, estado=estado, estado_en_actividad=estado_en_actividad, valido=valido, proyecto_id=proyecto_id)
        
    def test_hu_creation(self):
        """
        Test del modelo HU, crea un hu llamando a la create_hu, verifica la condicion de las instancias
        comprueba si el resultado es el esperado del __unicode__
        """
        w=self.create_hu()
        self.assertTrue(isinstance(w, HU))
        self.assertEqual(w.__unicode__(), w.descripcion)    
        print 'Crear una HU'
        
    def test_modificar_hu(self):
        """
        Verifica que el hu se ha modificado correctamente el valor_negocio
        """
        w=HU.objects.create(valor_tecnico='1', valor_negocio='1', prioridad='1', duracion='1',acumulador_horas='1', estado='ACT', proyecto_id='1')
        w.valor_negocio=2
        w.save()
        self.assertEqual(w.valor_negocio, 2)
        print 'Modificar una HU'
        
    def test_cambioestado_hu(self):
        """
        Verifica que el hu se ha modificado correctamente su estado
        """
        w=HU.objects.create(descripcion='hu', valor_tecnico='1', valor_negocio='1', prioridad='1', duracion='1',acumulador_horas='1', estado='ACT',proyecto_id='1', valido='1')
        w.estado='CAN'
        w.save()
        self.assertEqual(w.estado, 'CAN')
        print 'Cambiar estado de una HU'

class SprintTest(TestCase):
    def create_sprint(self):
        return Sprint.objects.create( descripcion='sprintTest', fecha_inicio=timezone.now(), duracion='3', estado='ACT', proyecto_id='1')
    
    def test_sprint_creation(self):
        """
        Verifica la correcta creacion del Sprint
        """
        w=self.create_sprint()
        self.assertEqual(w.descripcion, 'sprintTest')
        print 'Crear un Sprint'

    def test_modificar_sprint(self):
        """
        Verifica que el sprint se ha modificado correctamente su duracion
        """
        sprint=self.create_sprint()
        sprint.duracion=4
        sprint.save()
        self.assertEqual(sprint.duracion, 4)
        print 'Modificar un Sprint'
    
    def test_cambiarestado_sprint(self):
        """
        Verifica que el sprint se ha cambiado correctamente su estado
        """
        sprint=self.create_sprint()
        sprint.estado='CAN'
        sprint.save()
        self.assertEqual(sprint.estado, 'CAN')
        print 'Cambiar estado de Sprint'    