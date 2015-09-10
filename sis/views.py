from django.shortcuts import render, render_to_response
from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from sis.models import Proyecto, Rol, AsignarRolProyecto, MyUser, Flujo, Actividades
from django.template.context import RequestContext
#asignacion, proyecto, rol, Flujo, Actividades, HU, Sprint, delegacion, HU_descripcion, archivoadjunto, asignaHU_actividad_flujo, historial_notificacion, HU_version,\adjuntoVersion



'''def principal(request):
    if request.user.is_staff:
        return HttpResponseRedirect(reverse('admin:index'))
        
    else:
        return render(request,'principal.html',{'usuario':request.user}) 
'''

def loggedout(request):
    return render(request,'registration/logged_out.html')


def contactomail(request):
    return render(request,'registration/contactoMail.html')

#---------------------------------------------------------------------------------------------



@login_required
def holaView(request):
    """Vista que redirige a la pagina principal de administracion tanto a usuarios como a
    superusuarios, los superusuarios son redirigidos a la aplicacion admin mientras que los 
    usuarios obtienen una respuesta con el template hola.html"""
    if request.user.is_staff:
        return HttpResponseRedirect(reverse('admin:index'))
    else:
        nombres_de_proyecto = {}
        for a in AsignarRolProyecto.objects.all():
            if a.usuario.id == request.user.id:
                rol_lista = Rol.objects.get(id = a.rol.id)
                for p in Proyecto.objects.all():
                    if p.id == a.proyecto.id:
                        nombres_de_proyecto[p] = rol_lista
        return render(request,'hola.html',{'usuario':request.user, 'proyectos':nombres_de_proyecto})
    
    

def holaScrumView(request,usuario_id,proyectoid):
    """
    Vista especial para el usuario scrum en la que le listan los proyectos y los enlaces para la creacion de roles y flujos
    Vista para los usuario comunes, en la que solo se listan los proyectos sin enlaces, ya que no tiene permiso para ello.
    """
    proyectox=Proyecto.objects.get(id=proyectoid)
    usuario=MyUser.objects.get(id=usuario_id)
    return render(request,'rol-flujo-para-scrum.html',{'roles':Rol.objects.all(), 'flujos':Flujo.objects.all(),'proyecto':proyectox,'usuario':usuario})



class FormularioRolProyecto(forms.ModelForm):
    """
    Clase que obtiene el formulario para la creacion, visualizacion y modificacion
    de roles de proyecto desde la vista del Scrum.
    """
    class Meta:
        model= Rol
        fields=['permisos','nombre_rol','descripcion']

def visualizarRolProyectoView(request,usuario_id,proyectoid, rol_id_rec):
    """
    Vista que utiliza el formulario RolProyecto para desplegar los datos almacenados
    en el Rol que se quiere visualizar.
    """
    rolproyecto= Rol.objects.get(id=rol_id_rec)
    if request.method == 'POST':
        formulario = FormularioRolProyecto(request.POST)
        if formulario.is_valid():
            nombre_rol=formulario.cleanned_data['c']
            descripcion=formulario.cleanned_data['descripcion']
            permisos=formulario.cleanned_data['permisos']
            rolproyecto.nombre_rol=nombre_rol
            rolproyecto.descripcion=descripcion
            rolproyecto.permisos=permisos
            rolproyecto.save() 
            return HttpResponse('El rol ha sido guardado exitosamente')
    else:       
        formulario =  FormularioRolProyecto(initial={
                                                     'nombre_rol': rolproyecto.nombre_rol,
                                                     'permisos': rolproyecto.permisos,
                                                     'descripcion': rolproyecto.descripcion,
                                                     }) 
        return render_to_response('visualizarRol.html',{'formulario':formulario, 'rol':rolproyecto, 'proyectoid':proyectoid,'usuarioid':usuario_id},
                                  context_instance=RequestContext(request))































































   

def guardarFlujoView(request):
    """Vista de guardado de nuevo usuario relacionado con un correo autorizado en la tabla Permitidos
    que se utiliza en la interfaz devuelta por /registrar """
    try:
    
        flujo_a_crear = Flujo.objects.create(nombre=request.POST['nombre'])
        for p in request.POST.getlist('actividades'):
            flujo_a_crear.actividades.add(Actividades.objects.get(id=p))
        flujo_a_crear.save()
        return HttpResponse('El flujo se ha creado')  
    except ObjectDoesNotExist:
        print "Either the entry or blog doesn't exist." 
        return HttpResponseRedirect('/crearFlujo/')
    


class FormularioFlujoProyecto(forms.ModelForm):
    """
    Clase que obtiene el formulario para la creacion, visualizacion y modificacion
    de flujos de proyecto desde la vista del Scrum.
    """
    class Meta:
        model= Flujo
        fields=['nombre','actividades']
        widgets = {
            'actividades': CheckboxSelectMultiple(),
        }
        
        

def visualizarFlujoProyectoView(request,usuario_id, proyectoid, flujo_id_rec):
    """
    Vista que utiliza el formulario FlujoProyecto para desplegar los datos almacenados
    en el Flujo que se quiere visualizar.
    """
    flujo_disponible= Flujo.objects.get(id=flujo_id_rec)
    if request.method == 'POST':
        formulario = FormularioFlujoProyecto(request.POST)
        if formulario.is_valid():
            nombre=formulario.cleanned_data['nombre']
            #estado=formulario.cleanned_data['estado']
            actividades=formulario.cleanned_data['actividades']
            flujo_disponible.nombre=nombre
            #flujo_disponible.estado=estado
            flujo_disponible.actividades=actividades
            flujo_disponible.save() #Guardamos el modelo de manera Editada
            return HttpResponse('El rol ha sido guardado exitosamente')
    else:   
        formulario =  FormularioRolProyecto(initial={
                                                     'nombre': flujo_disponible.nombre,
                                                     'actividades': flujo_disponible.actividades,
                                                     })      
        return render_to_response('visualizarFlujo.html',{'formulario':formulario, 'flujo':flujo_disponible, 'proyectoid':proyectoid,'usuarioid':usuario_id},
                                  context_instance=RequestContext(request))



def modificarFlujo(request, usuario_id, proyectoid, flujo_id_rec):
    """
    Vista que utiliza el formulario FlujoProyecto para desplegar los datos editables
    del Flujo que se quiere modificar.
    """
    f=Flujo.objects.get(id=flujo_id_rec)
    if request.method == 'POST':
        form = FormularioFlujoProyecto(request.POST)
        if form.is_valid():
            nombre=form.cleaned_data['nombre']
            #estado=form.cleaned_data['estado']
            actividades=form.cleaned_data['actividades']
            f.nombre=nombre
            #f.estado=estado
            f.actividades=actividades
            f.save() #Guardamos el modelo de manera Editada
            return HttpResponse('El flujo a sido modificado exitosamente')
    else:
        
        form = FormularioFlujoProyecto(initial={
                                         'nombre': f.nombre,
                                         #'estado': f.estado,
                                         'actividades': [t.id for t in f.actividades.all()],
   
                                         })
        ctx = {'form':form, 'flujo':f, 'proyectoid':proyectoid,'usuarioid':usuario_id}
        return render_to_response('modificarFlujo.html', ctx ,context_instance=RequestContext(request))
    
    

def crearFlujo(request,usuario_id,proyectoid):
    """
    Vista que realiza la creacion de flujos de proyecto desde la vista del Scrum.
    """
    if request.method == 'GET':
        return render(request, 'crearFlujo.html',{'actividades':Actividades.objects.all(),'usuarioid':usuario_id,'proyectoid':proyectoid})




























































def crearActividadView(request,usuario_id,proyectoid):
    
    """
    Vista que se obtiene del regex al presionar el boton Crear Actividad dentro del formulario
    de creacion o modificacion de Flujos del admin, devolviendo un formulario html para crear una nueva actividad
    """  
    if request.method == 'GET':
        form = formularioActividad()
        return render_to_response("crearActividadAdmin.html",{"form":form,}, context_instance = RequestContext(request))
    
    else:#request.method == 'POST'
        form = formularioActividad(request.POST)
        if form.is_valid():
            nombre=form.cleaned_data['nombre']
            descripcion=form.cleaned_data['descripcion']
            form.nombre=nombre
            form.descripcion=descripcion
            form.save()
            return HttpResponse('Ha sido guardado exitosamente') 
    


def crearActividadAdminView(request):
    """
    Vista que se obtiene del regex al presionar el boton Crear Actividad dentro del formulario
    de creacion o modificacion de Flujos del admin, devolviendo un formulario html para crear una nueva actividad
    """  
    if request.method == 'GET':
        form = formularioActividad()
        return render_to_response("crearActividadAdmin.html",{"form":form,}, context_instance = RequestContext(request))
    
    else:#request.method == 'POST'
        form = formularioActividad(request.POST)
        if form.is_valid():
            nombre=form.cleaned_data['nombre']
            descripcion=form.cleaned_data['descripcion']
            form.nombre=nombre
            form.descripcion=descripcion
            form.save()
            return HttpResponse('Ha sido guardado exitosamente')  
        
        

def seleccionarFlujoModificarAdmin(request):
    """
    Al presionar el boton Modificar Actividad en el admin, esta vista despliega una lista de todas las actividades 
    seleccionables por el usuario para su modificacion.
    """
    return render(request,'seleccionarActividadAdmin.html',{'actividades':Actividades.objects.all(),})



def modificarActividadAdmin(request,actividad_id_rec):
    """
    Vista que utiliza el formulario formularioActividad para desplegar los datos editables en el admin
    de la Actividad que se quiere modificar.
    """
    p=Actividades.objects.get(id=actividad_id_rec)
    if request.method == 'POST':
        form = formularioActividad(request.POST)
        if form.is_valid():
            nombre=form.cleaned_data['nombre']
            descripcion=form.cleaned_data['descripcion']
            p.nombre=nombre
            p.descripcion=descripcion
            p.save() #Guardamos el modelo de manera Editada
            return HttpResponse('Se ha guardado exitosamente')
    else:
        
        form = formularioActividad(initial={
                                         'nombre': p.nombre,
                                         'descripcion': p.descripcion,                                     
                                         })
        ctx = {'form':form, 'Actividad':p,}
        return render_to_response('modificarActividadAdmin.html', ctx ,context_instance=RequestContext(request)) 



class formularioActividad(forms.ModelForm):
    """
    Clase que obtiene el formulario para la creacion y modificacion de actividades desde la vista del Scrum y el admin.
    """
    class Meta:
        model=Actividades
        fields = ('nombre', 'descripcion')



def seleccionarFlujoModificar(request,usuario_id,proyectoid):
    """
    Al presionar el boton Modificar Actividad, esta vista despliega una lista de todas las actividades seleccionables por el usuario
    para su modificacion.
    """
    return render(request,'seleccionarActividad.html',{'actividades':Actividades.objects.all(),'usuarioid':usuario_id,'proyectoid':proyectoid})



def modificarActividad(request,usuario_id,proyectoid,actividad_id_rec):
    """
    Vista que utiliza el formulario formularioActividad para desplegar los datos editables
    de la Actividad que se quiere modificar.
    """
    p=Actividades.objects.get(id=actividad_id_rec)
    if request.method == 'POST':
        form = formularioActividad(request.POST)
        if form.is_valid():
            nombre=form.cleaned_data['nombre']
            descripcion=form.cleaned_data['descripcion']
            p.nombre=nombre
            p.descripcion=descripcion
            p.save() #Guardamos el modelo de manera Editada
            return HttpResponse('Se ha guardado exitosamente')
    else:
        
        form = formularioActividad(initial={
                                         'nombre': p.nombre,
                                         'descripcion': p.descripcion,                                     
                                         })
        ctx = {'form':form, 'Actividad':p,'usuarioid':usuario_id,'proyectoid':proyectoid}
        return render_to_response('modificarActividad.html', ctx ,context_instance=RequestContext(request)) 
 
