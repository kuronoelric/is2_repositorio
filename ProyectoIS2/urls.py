"""ProyectoIS2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from sis import views


"""Archivo donde se especifican las expresiones regulares que seran filtradas y 
y redirigidas a una vista para el procesamiento de las peticiiones. El funcionamiento 
depende de la variable urlpatterns que puede incluir otros URLConfs o el nombre de la vista 
y la ruta para poder acceder a la misma"""

urlpatterns = [
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url('^', include('django.contrib.auth.urls')),
    #url(r'^principal/', views.principal, name='principal'),
    url(r'^loggedout/', views.loggedout, name='loggedout'),
    url(r'^contactomail/$', views.contactomail, name='contactoMail'),
    
#------------------------------------------------------------------------------------------------------    
    url(r'^hola/', views.holaView, name='hola'),
    url(r'^modificarProyecto/(?P<usuario_id>\d+)/(?P<proyecto_id_rec>\d+)/$', views.modificarProyecto, name='modificar_proyecto'),
    url(r'^visualizarProyecto/(?P<usuario_id>\d+)/(?P<proyecto_id_rec>\d+)/$', views.visualizarProyectoView, name='visualizar_proyecto'),
    url(r'^visualizarRol/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<rol_id_rec>\d+)/$', views.visualizarRolProyectoView, name='visualizar_rol'),
    url(r'^visualizarFlujo/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<flujo_id_rec>\d+)/$', views.visualizarFlujoProyectoView, name='visualizar_flujo'),
    url(r'^modificarFlujo/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<flujo_id_rec>\d+)/$', views.modificarFlujo, name='modificar_flujo'),
    url(r'^crearFlujo/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/', views.crearFlujo, name='crear_Flujo'),
    url(r'^guardarFlujo/', views.guardarFlujoView, name='guardar_nuevo_flujo'),
    url(r'^scrum/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/$', views.holaScrumView, name='roles-flujos'),
    url(r'^crearActividad/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/$', views.crearActividadView, name='crearActividad'),
    url(r'^modificarActividad/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/$', views.seleccionarFlujoModificar, name='seleccionarFlujoModificar'),
    url(r'^modificarActividad/(?P<usuario_id>\d+)/(?P<proyectoid>\d+)/(?P<actividad_id_rec>\d+)/$', views.modificarActividad, name='modificarActividad'),
    url(r'^asignarRol/(?P<usuario_id>\d+)/(?P<rolid>\d+)/(?P<proyectoid>\d+)$',views.asignarRol, name= 'asignaRol'),
    url(r'^equipoProyecto/(?P<proyecto_id_rec>\d+)/(?P<usuario_id>\d+)$',views.listarEquipo,name='listaEquipo'),
    url(r'^crearActividad/$', views.crearActividadAdminView, name='crearActividadAdmin'),
    url(r'^modificarActividad/$', views.seleccionarFlujoModificarAdmin, name='seleccionarFlujoModificarAdmin'),
    url(r'^modificarActividad/(?P<actividad_id_rec>\d+)/$', views.modificarActividadAdmin, name='modificarActividadAdmin'),

    
]