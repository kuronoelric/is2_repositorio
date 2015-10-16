from django.shortcuts import render, render_to_response
from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from sis.models import Proyecto, Rol, AsignarRolProyecto, MyUser, Flujo, Actividades, HU
from django.template.context import RequestContext
from django.utils import timezone
from django.core.mail.message import EmailMessage
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



class proyectoFrom(forms.ModelForm):
    """
    Clase que obtiene el formulario para la visualizacion y modificacion de proyectos desde la vista del Scrum.
    """
    class Meta:
        model = Proyecto
        fields = ['nombre', 'descripcion','estado','fecha_inicio','fecha_fin']



def modificarProyecto(request, usuario_id, proyecto_id_rec):
    """
    Vista que utiliza el formulario proyectoFrom para desplegar los datos editables
    del Proyecto que se quiere modificar.
    """
    p=Proyecto.objects.get(id=proyecto_id_rec)
    if request.method == 'POST':
        form = proyectoFrom(request.POST)
        if form.is_valid():
            nombre=form.cleaned_data['nombre']
            descripcion=form.cleaned_data['descripcion']
            estado=form.cleaned_data['estado']
            fecha_inicio=form.cleaned_data['fecha_inicio']
            fecha_fin=form.cleaned_data['fecha_fin']
            p.nombre=nombre
            p.descripcion=descripcion
            p.estado=estado
            p.fecha_inicio=fecha_inicio
            p.fecha_fin=fecha_fin
            p.save() #Guardamos el modelo de manera Editada
            return HttpResponse('Tu proyecto a sido guardado exitosamente')
    else:
        
        form = proyectoFrom(initial={
                                         'nombre': p.nombre,
                                         'descripcion': p.descripcion,
                                         'estado':p.estado,
                                         'fecha_inicio': p.fecha_inicio,
                                         'fecha_fin': p.fecha_fin,
                                     
                                         })
        ctx = {'form':form, 'proyecto':p,'usuarioid':usuario_id}
        return render_to_response('modificarProyecto.html', ctx ,context_instance=RequestContext(request))


  
def visualizarProyectoView(request,usuario_id, proyecto_id_rec):
    """
    Vista que utiliza el formulario proyectoFrom para desplegar los datos almacenados
    en el Flujo que se quiere visualizar.
    """
    proyecto_enc= Proyecto.objects.get(id=proyecto_id_rec)
    return render_to_response('visualizarProyecto.html',{'proyecto':proyecto_enc,'usuarioid':usuario_id},
                                  context_instance=RequestContext(request))



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
    
    
    
    
    
    
    
    
    """
    Vista que se obtiene del regex al presionar el boton Crear Actividad dentro del formulario
    de creacion o modificacion de Flujos, devolviendo un formulario html para crear una nueva actividad
     
    if request.method == 'GET':
        form = formularioActividad()
        return render_to_response("crearActividad.html",{"form":form,'usuarioid':usuario_id,'proyectoid':proyectoid}, context_instance = RequestContext(request))
    
    else:#request.method == 'POST'
        form = formularioActividad(request.POST)
        if form.is_valid():
            nombre=form.cleaned_data['nombre']
            descripcion=form.cleaned_data['descripcion']
            form.nombre=nombre
            form.descripcion=descripcion
            form.save()
            return HttpResponse('Ha sido guardado exitosamente')       

"""

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
 


def asignarRol(request,rolid,proyectoid,usuario_id):
    """
    Vista que permite asignar un rol a un usuario dentro de la vista del Scrum, valiendose de la URL para obtener
    los id's del rol , proyecto ye l usuario creador.
    """
    proyectox=Proyecto.objects.get(id=proyectoid)
    rolx = Rol.objects.get(id=rolid)
    if request.method=='POST':
        try:
            for p in request.POST.getlist('usuarios'):
                asignacion_a_crear = AsignarRolProyecto.objects.create(usuario=MyUser.objects.get(id=p),rol=rolx, proyecto=proyectox)
                asignacion_a_crear.save()
                usuario=MyUser.objects.get(id=usuario_id)
                return render(request,'rol-flujo-para-scrum.html',{'roles':Rol.objects.all(), 'flujos':Flujo.objects.all(),'proyecto':proyectox,'usuario':usuario})
        except ObjectDoesNotExist:
            print "Either the entry or blog doesn't exist." 
            return HttpResponseRedirect('/crearFlujo/')
    else:
        return render(request,'asignaRolProyecto.html',{'proyecto':proyectox,'usuarios':MyUser.objects.all().exclude(id=usuario_id),'proyectoid':proyectoid,'usuarioid':usuario_id})
    
    
    
def listarEquipo(request,proyecto_id_rec,usuario_id):
    """Esta vista debe obtener los datos de los usuarios que han sido asignados a un rol en el proyecto,el parametro
    usuario_id se necesita simplemente para el render para poder retornar a rol-flujo-para-scrum"""
    lista={}
    proyectox=Proyecto.objects.get(id=proyecto_id_rec)
    for a in AsignarRolProyecto.objects.all():
        if a.proyecto.id == proyectox.id:#si el proyecto relacionado a una asignacion es el que se esta viendo ahora
            rol_a=Rol.objects.get(id=a.rol.id)
            usuario_a=MyUser.objects.get(id=a.usuario.id)
            lista[usuario_a]=rol_a#agregar el usuario de esa asignacion a la vista, y mandarlo al template
    return render(request,'formarEquipo.html',{'roles':Rol.objects.all(),'lista_asigna':lista, 'flujos':Flujo.objects.all(),'proyecto':proyectox,'usuario_id':usuario_id})

## ----------------------------------------------------------------------------------------------------------------

class FormularioHU(forms.ModelForm):
    """
    Clase que obtiene el formulario para la creacion, visualizacion y modificacion
    de HU's del proyecto desde la vista del Scrum y del Product Owner.
    """
    class Meta:
        model= HU
        fields=['valor_tecnico','prioridad','duracion']
        
def visualizarHUView(request,usuario_id, proyectoid, rolid, HU_id_rec,is_Scrum, kanban):
    """
    Vista que utiliza el formulario HU para desplegar los datos almacenados
    en la HU que se quiere visualizar.
        :param func: request
        :param args: usuario_id, proyectoid, rolid, HU_id_rec,is_Scrum, kanban
        :returns: 'visualizarHU.html'
    """
    HU_disponible= HU.objects.get(id=HU_id_rec)
    usuario_asignado = HU_disponible.saber_usuario() 
    flujo_al_que_pertenece=HU_disponible.flujo()
    sprint_al_que_pertenece=HU_disponible.sprint()
    #adjuntos=archivoadjunto.objects.filter(hU=HU_disponible)
    formulario =  FormularioHU(initial={
                                                     'descripcion': HU_disponible.descripcion,
                                                     'valor_negocio': HU_disponible.valor_negocio,
                                                     })      
    return render_to_response('visualizarHU.html',{'formulario':formulario,'version':HU_disponible.version,'usuario_asignado':usuario_asignado,'HU':HU_disponible, 'proyectoid':proyectoid,'usuarioid':usuario_id, 'rolid':rolid,'''adjuntos':adjuntos,''' 'is_Scrum':is_Scrum, 'sprint':sprint_al_que_pertenece, 'flujo':flujo_al_que_pertenece, 'kanban':kanban},
                                  context_instance=RequestContext(request))

def modificarHU(request, usuario_id, proyectoid, rolid, HU_id_rec,is_Scrum):
    """
    Vista que utiliza el formulario HU para desplegar los datos editables
    de la HU en tres niveles de modificacion.
    Esta vista corresponde a la modificacion del nivel 1, es decir, a nivell Scrum Master
        :param func: request
        :param args: usuario_id, proyectoid, rolid, HU_id_rec,is_Scrum
        :returns: modificarHU.html
        :rtype: valor_tecnico, prioridad, duracion
    """
    estados=['ACT','CAN']
    VALORES10_CHOICES = range(1,10)
    h=HU.objects.get(id=HU_id_rec)
    if (is_Scrum == '1'):
        if request.method == 'POST':
            form = FormularioHU(request.POST)
            if form.is_valid():
                valor_tecnico=form.cleaned_data['valor_tecnico']
                prioridad=form.cleaned_data['prioridad']
                duracion=form.cleaned_data['duracion']
                #estado=form.cleaned_data['estado']
                h.valor_tecnico=valor_tecnico
                h.prioridad=prioridad
                h.duracion=duracion
                #h.estado=estado
                h.save() #Guardamos el modelo de manera Editada   
                evento_e=usuario_id+"+"+proyectoid+"+"+rolid+"+"+"HU+"+"M+"+"La HU '"+str(h.descripcion)+"' valor de negocio  '"+str(form.cleaned_data['valor_tecnico'])+"'  prioridad '"+str(form.cleaned_data['prioridad'])+"' y duracion  '"+str(form.cleaned_data['duracion'])+"' ha sido modificado exitosamente en la fecha y hora: "+str(timezone.now())
                usuario_e=MyUser.objects.get(id=usuario_id)
                '''historial_notificacion.objects.create(usuario=usuario_e, fecha_hora=timezone.now(), objeto=h.descripcion,evento=evento_e)
                if usuario_e.frecuencia_notificaciones == 'instante':
                    send_email(str(usuario_e.email), 'Notificacion', evento_e)
'''
                return HttpResponse('La HU ha sido modificado exitosamente')
            else:
                return HttpResponse('error'+str(form.errors))
        else:
        
            form = FormularioHU(initial={
                                        'valor_tecnico': h.valor_tecnico,
                                        'prioridad': h.prioridad,
                                        'duracion':h.duracion,
                                        #'estado':h.estado
                                         })
            ctx = {'version':h.version,'valores':VALORES10_CHOICES,'form':form, 'HU':h, 'proyectoid':proyectoid,'usuarioid':usuario_id, 'rolid':rolid,'is_Scrum':is_Scrum}
            return render_to_response('modificarHU.html', ctx ,context_instance=RequestContext(request))
    else:
        return render(request,'modificarHU.html', {'version':h.version,'estados':estados, 'valores':VALORES10_CHOICES,'HU':h, 'proyectoid':proyectoid,'usuarioid':usuario_id, 'rolid':rolid,'is_Scrum':is_Scrum})


def crearHU(request,usuario_id,proyectoid,rolid):
    """
    Vista que realiza la creacion de flujos de proyecto desde la vista del Scrum.
        :param func: request
        :param args: usuario_id,proyectoid,rolid
        :returns: crearHU.html
    
    """
    VALORES10_CHOICES = range(1,10)
    if request.method == 'GET':
        return render(request, 'crearHU.html',{'usuarioid':usuario_id,'proyectoid':proyectoid,'rolid':rolid,'valores':VALORES10_CHOICES})