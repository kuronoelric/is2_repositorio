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
    url(r'^admin/', include(admin.site.urls)),
    url('^', include('django.contrib.auth.urls')),
    url(r'^principal/', views.principal, name='principal'),
    url(r'^loggedout/', views.loggedout, name='loggedout'),
    url(r'^contactomail/$', views.contactomail, name='contactoMail'),
]
