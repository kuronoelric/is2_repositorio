from django.conf.urls import include, url
from django.contrib import admin
from sis import views


"""Archivo donde se especifican las expresiones regulares que seran filtradas y 
y redirigidas a una vista para el procesamiento de las peticiiones. El funcionamiento 
depende de la variable urlpatterns que puede incluir otros URLConfs o el nombre de la vista 
y la ruta para poder acceder a la misma"""

urlpatterns = [
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^loggedout/', views.loggedout, name='loggedout'),
    url(r'^contactomail/$', views.contactomail, name='contactoMail'),
    

    url(r'^admin/', include(admin.site.urls)),
    url('^', include('django.contrib.auth.urls')),
    url(r'^hola/', views.holaView, name='hola'),
    url(r'^contactomail/$', views.contactomail, name='contactoMail'),
    url(r'^modificarProyecto/(?P<usuario_id>\d+)/(?P<proyecto_id_rec>\d+)/$', views.modificarProyecto, name='modificar_proyecto'),
    url(r'^anularProyecto/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/$', views.anularProyecto, name='anular_proyecto'),
    url(r'^finalizarProyecto/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rol_id>\d+)/$', views.finalizarProyecto, name='finalizarProyecto'),
    url(r'^visualizarProyecto/(?P<usuario_id>\d+)/(?P<proyecto_id_rec>\d+)/$', views.visualizarProyectoView, name='visualizar_proyecto'),
    url(r'^visualizarFlujo/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/(?P<flujo_id_rec>\d+)/$', views.visualizarFlujoProyectoView, name='visualizar_flujo'),
    url(r'^modificarFlujo/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/(?P<flujo_id_rec>\d+)/$', views.modificarFlujo, name='modificar_flujo'),
    url(r'^crearFlujo/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/$', views.crearFlujo, name='crear_Flujo'),
    url(r'^guardarFlujo/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/$', views.guardarFlujoView, name='guardar_nuevo_flujo'),
    url(r'^scrum/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rol_id>\d+)/$', views.holaScrumView, name='roles-flujos'),
    url(r'^crearActividad/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/$', views.crearActividadView, name='crearActividad'),
    url(r'^modificarActividad/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/$', views.seleccionarFlujoModificar, name='seleccionarFlujoModificar'),
    url(r'^modificarActividad/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<actividad_id_rec>\d+)/$', views.modificarActividad, name='modificarActividad'),
    url(r'^asignarRol/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/(?P<rol_id_rec>\d+)/$',views.asignarRol, name= 'asignaRol'),
    url(r'^equipoProyecto/(?P<proyecto_id_rec>\d+)/(?P<usuario_id>\d+)$',views.listarEquipo,name='listaEquipo'),
    url(r'^crearActividad/$', views.crearActividadAdminView, name='crearActividadAdmin'),
    url(r'^modificarActividad/$', views.seleccionarFlujoModificarAdmin, name='seleccionarFlujoModificarAdmin'),
    url(r'^modificarActividad/(?P<actividad_id_rec>\d+)/$', views.modificarActividadAdmin, name='modificarActividadAdmin'),
    url(r'^visualizarHU/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/(?P<HU_id_rec>\d+)/(?P<is_Scrum>\d+)/(?P<kanban>\d+)/$', views.visualizarHUView, name='visualizar_HU'),
    url(r'^crearHU/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/$', views.crearHU, name='crear_HU'),
    url(r'^guardarHU/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/$', views.guardarHUView, name='guardar_nuevo_HU'),
    url(r'^modificarHU/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/(?P<HU_id_rec>\d+)/(?P<is_Scrum>\d+)/$', views.modificarHU, name='modificar_HU'),
    url(r'^guardarHU/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/(?P<HU_id_rec>\d+)/(?P<is_Scrum>\d+)/$', views.guardarHUProdOwnerView, name='guardar_HU_modificada'),
    url(r'^visualizarSprint/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/(?P<Sprint_id_rec>\d+)/$', views.visualizarSprintProyectoView,name='visualizar_Sprint'),
    url(r'^crearSprint/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/$', views.crearSprint, name='crear_Sprint'),
    url(r'^guardarSprint/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/$', views.guardarSprintView, name='guardar_nuevo_Sprint'),
    url(r'^modificarSprint/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/(?P<Sprint_id_rec>\d+)/$', views.modificarSprint, name='modificar_Sprint'),
    url(r'^delegarHU/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/(?P<hu_id>\d+)/(?P<reasignar>\d+)/$',views.delegarHU,name='delegarhu'),
    url(r'^validarHU/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/(?P<HU_id_rec>\d+)/(?P<is_Scrum>\d+)/$',views.validarHU,name='validarhu'),
    url(r'^visualizarBacklog/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/$',views.visualizarBacklog,name='verBacklog'),
    url(r'^reactivar/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/(?P<tipo>\d+)/(?P<id_tipo>\d+)/$', views.reactivar, name='reactivar'),
    url(r'^adminAdjunto/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/(?P<HU_id_rec>\d+)/$',views.adminAdjunto,name='adminAdjunto'),
    url(r'^descargar/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/(?P<HU_id_rec>\d+)/(?P<archivo_id>\d+)/$',views.descargar,name='descargarAdjunto'),
    url(r'^eliminar/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/(?P<HU_id_rec>\d+)/(?P<archivo_id>\d+)/$',views.eliminar_adjunto,name='eliminarrAdjunto'),
    url(r'^visualizarSprintBacklog/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/$',views.visualizarSprintBacklog,name='verSprintBacklog'),
    url(r'^asignarHUFlujo/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/(?P<sprintid>\d+)/$',views.asignarHU_Usuario_FLujo,name='asignarHU_Usuario_FLujo'),
    url(r'^delegarHUFlujo/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/(?P<sprintid>\d+)/(?P<flujo_id>\d+)/$',views.asignarHU_a_FLujo,name='asignarHU_a_FLujo'),
    url(r'^verKanban/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/(?P<sprintid>\d+)/$',views.verKanban,name='ver_Kanban'),
    url(r'^aprobarHU/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/(?P<sprintid>\d+)/(?P<HU_id_rec>\d+)/$', views.aprobarHU, name='aprobar'),
    url(r'^reasignarhuFlujo/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/(?P<sprintid>\d+)/(?P<huid>\d+)/(?P<kanban>\d+)/$',views.reasignarhuFlujo, name='reasignar hu flujo'),
    url(r'^guardarFlujoSprint/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/$', views.guardarSprintFlujos, name='guardar_nuevo_flujo_sprint'),
    url(r'^iniciar/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rol_id>\d+)/(?P<sprintid>\d+)/$', views.iniciarProyecto, name='iniciarSprint'),
    url(r'^asignarRol/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/(?P<rol_id_rec>\d+)/$',views.asignarRol, name= 'asignaRol'),
    url(r'^visualizarRol/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rolid>\d+)/(?P<rol_id_rec>\d+)/$', views.visualizarRolProyectoView, name='visualizar_rol'),

]

