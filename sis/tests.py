from django.test import TestCase
from sis.models import MyUser, Rol, Actividades, Flujo, Proyecto, AsignarRolProyecto
from sis.views import FormularioRolProyecto, proyectoFrom, FormularioFlujoProyecto, formularioActividad
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

    def test_create_user_is_active_is_not_admin(self):
        """
        create_user() verificar si esta activo y no es admin
        """
        usuario = MyUser.objects.create_user('testusuario', 'testusuario2@hotmail.com', 'pass123')
        self.assertEqual(usuario.is_admin,False)
        self.assertEqual(usuario.is_active,True)
        
    def test_create_superuser_is_an_instance_of_User(self):
        """
        create_superuser() deberia retornar un objeto user con nombre de usuario,
        el email dado y contrasenha
        """
        usuario = MyUser.objects.create_superuser('testusuario','testusuario2@hotmail.com', 'pass123')
        self.assertEqual(isinstance(usuario, MyUser),True)
        
    def test_create_superuser_is_active_is_admin(self):
        """
        create_superuser() verificar si esta activo y no es admin
        """
        usuario = MyUser.objects.create_superuser('testusuario', 'testusuario2@hotmail.com', 'pass123')
        self.assertEqual(usuario.is_admin,True)
        self.assertEqual(usuario.is_active,True)
        
        
  
  

  
  
class RolTest(TestCase):
    
    def create_rol(self):
        return Rol.objects.create( nombre_rol="nuevoRol", descripcion="nuevo_rol")
    
    def test_rol_creation(self):
        """Test que prueba la creacion de rol"""
        w=self.create_rol()
        self.assertTrue(isinstance(w, Rol))
        self.assertEqual(w.__unicode__(), w.nombre_rol)
        
    def setUp(self):
        self.factory=RequestFactory
        self.rol=Rol.objects.create(nombre_rol="nuevoRol", descripcion="nuevo_rol")

    
    def test_modificarRol(self):
        """Test que prueba la modificacion de rol en uno de sus parametros"""
        w=self.create_rol()
        w.descripcion='rol_cambiado'
        w.save()
        self.assertEqual(w.descripcion, 'rol_cambiado')
    
    def test_dato_invalido(self):
        """Test que prueba el ingreso invalido de uno de los datos del rol"""
        w=self.create_rol()
        w.descripcion='rol_cambiado'
        w.save()
        self.assertNotEqual(w.descripcion, 'nuevo_rol')
         
          
class ActividadesTest(TestCase):
    def create_Actividades(self, nombre="nuevaActividad", descripcion="nuevo Actividad" ):
        return Actividades.objects.create(nombre=nombre, descripcion=descripcion)
    
    def test_Actividad_creation(self):
        """Test que prueba la creacion de una acividad"""
        w=self.create_Actividades()
        self.assertTrue(isinstance(w, Actividades))
        self.assertEqual(w.__unicode__(), str(w.id)  + " - " + w.nombre)
        
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
        
    def test_crear_actividad_views_get(self):
        """Test que prueba la vista de crearActividad de una acividad GET"""
        response=self.client.get('/crearActividad/2/1/')
        self.assertEqual(response.status_code, 200)
        
    def test_crear_actividad_views_pos(self):
        """Test que prueba la vista de crearActividad de una acividad POS"""
        w = Actividades.objects.create(nombre="nuevaActividad", descripcion='nueva Actividad' )
        w.save()
        
        actividad_in=Actividades.objects.get(pk=w.id)
        self.assertEquals(actividad_in.nombre, w.nombre)    
       
    def create_proyecto(self):
        return Proyecto(nombre="P9", descripcion="proyecto9", fecha_inicio=timezone.now(), fecha_fin=datetime.timedelta(days=1), estado="PEN")
    
     
    def test_modificar_actividad_views(self):
        """Test que prueba la vista de modificarActividad de una acividad"""
        w=self.create_proyecto()    
        u= MyUser.objects.create_user('anonimo','anonimo2@hotmail.com', '1234')
        y= self.create_Actividades()

        post_data={'usuario':u.id,'proyecto':w.id,'actividad':y.id}
        Actividad_url='/modificarActividad/1/1/'
        self.client.post(Actividad_url, data=post_data)
    
    def test_modificarActividad(self):
        """Test que prueba la modificacion de una acividad"""
        w=self.create_Actividades()
        w.nombre='actividad_prueba'
        w.save()
        self.assertEqual(w.nombre, 'actividad_prueba')
        
class FlujoTest(TestCase):
    def create_Flujo(self, nombre="1nuevoFlujo"):
        return Flujo.objects.create(nombre=nombre)
    
    def test_Flujo_creation(self):
        """Test que prueba la creacion de un flujo"""
        w=self.create_Flujo()
        self.assertTrue(isinstance(w, Flujo))
    
    def test_crear_flujo_views(self):
        """Test que prueba la vista de un flujo"""
        response=self.client.get('/crearFlujo/2/1/1/')
        self.assertEqual(response.status_code, 200)
     
        
class proyectoTest(TestCase):
    
    def create_proyecto(self):
        return Proyecto(nombre="P9", descripcion="proyecto9", fecha_inicio=timezone.now(), fecha_fin=datetime.timedelta(days=1), estado="PEN")
    
    def test_proyecto_creation(self):
        """Test que prueba la creacion de un proyecto"""
        w=self.create_proyecto()
        self.assertTrue(isinstance(w, Proyecto))
        self.assertEqual(w.__unicode__(), w.nombre)
    
    def test_invalid_proyectoFrom(self):
        """Test que prueba el formulario de un proyecto invalido"""
        w = Proyecto.objects.create(nombre="P9",  descripcion="proyecto9", fecha_inicio="2015-03-31 00:00:00-04", fecha_fin="2015-03-31 00:00:00-04",estado="PEN" ,duracion=10,cantidad_dias_transcurridos=0)
        data = {'nombre':w.nombre, 'descripcion':w.descripcion, 'fecha_inicio':w.fecha_inicio, 'fecha_fin': w.fecha_fin, }
        form = proyectoFrom(data=data)
        self.assertFalse(form.is_valid())
        
    def test_valid_FormularioRolProyecto(self):
        """Test que prueba el formulario de un rol-proyecto valido"""
        w = Rol.objects.create(nombre_rol="nuevoRol", descripcion="nuevoRol")
        w.permisos.add(Permission.objects.get(id=31))
        form = FormularioRolProyecto({'nombre_rol':w.nombre_rol, 'descripcion':w.descripcion,'permisos':[t.id for t in w.permisos.all()],})
        self.assertTrue(form.is_valid())

    def test_invalid_FormularioRolProyecto(self):
        """Test que prueba el formulario de un rol-proyecto invalido"""
        w = Proyecto(nombre="P9", descripcion="proyecto9", fecha_inicio=timezone.now(), fecha_fin=datetime.timedelta(days=1) ,estado="PEN" )
        data = {'nombre':w.nombre, 'descripcion':w.descripcion, 'fecha_inicio':w.fecha_inicio, 'fecha_fin': w.fecha_fin, 'estado':w.estado ,}
        form = FormularioRolProyecto(data=data)
        self.assertFalse(form.is_valid())
      
    def test_valid_FormularioFlujoProyecto(self):
        """Test que prueba formulario de un flujo-proyecto valido"""
        w = Flujo.objects.create(nombre='nuevoFlujo')
        w.actividades.create(nombre='Actividad1', descripcion='actividad')
        form = FormularioFlujoProyecto({'nombre':w.nombre, 'actividades': [t.id for t in w.actividades.all()],})
        self.assertTrue(form.is_valid())
        
    def test_invalid_FormularioFlujoProyecto(self):
        """Test que prueba el formulario de un flujo-proyecto invalido"""
        w = Flujo.objects.create(nombre='nuevoFlujo')
        data = {'nombre':w.nombre, }
        form = FormularioFlujoProyecto(data=data)
        self.assertFalse(form.is_valid()) 
        
        
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
        
    def create_proyecto2(self):
        return Proyecto.objects.create(nombre="P",  descripcion="proyecto", fecha_inicio="2015-03-31 00:00:00-04", fecha_fin="2015-03-31 00:00:00-04" ,estado="PEN" ,duracion=10,cantidad_dias_transcurridos=0)
        
    def test_asignacion_modificar(self):
        """Test que prueba la modificacion del proyecto de una asignacion"""
        w=self.create_asignacion()
        w.proyecto=self.create_proyecto2()
        w.save()
        self.assertEqual(w.proyecto.nombre, 'P')        
        
class asigna_sistemacionTest(TestCase):
    def create_proyecto(self):
        return Proyecto(nombre="P9", descripcion="proyecto9", fecha_inicio=timezone.now(), fecha_fin=datetime.timedelta(days=1), estado="PEN")
    
    def create_rol(self):
        return Rol.objects.create( nombre_rol="nuevoRol", descripcion="nuevo_rol")