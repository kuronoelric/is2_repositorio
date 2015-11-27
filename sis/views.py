from django.shortcuts import render, render_to_response
from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from sis.models import Proyecto, Rol, AsignarRolProyecto, MyUser, Flujo, Actividades, Sprint, HU, AsignaHU_Usuario, Horas_Trabajadas, AsignaHU_flujo, archivoadjunto
from django.template.context import RequestContext
from django.utils import timezone
from io import BytesIO
import math, json
from django.core.mail.message import EmailMessage
from django.core.mail import send_mail


def loggedout(request):
    return render(request,'registration/logged_out.html')


def contactomail(request):
    return render(request,'registration/contactoMail.html')


def send_email(to, subj, body):
    # this will be executed in a separate thread
    mail = EmailMessage(subj, body, to=[to])
    mail.send()

@login_required
def holaView(request):
    """
    Vista que redirige a la pagina principal de administracion tanto a usuarios como a
    superusuarios, los superusuarios son redirigidos a la aplicacion admin mientras que los 
    usuarios obtienen una respuesta con el template hola.html
        :param func: request
        :returns: 'hola.html'
    """
    if request.user.is_staff:
        return HttpResponseRedirect(reverse('admin:index'))
    else:
        proyecto_cliente=[]
        proyectos_enlace={}
        proyectos_sin_enlace={}
        roles_enlace = []
        roles_sin_enlace = []
        for a in AsignarRolProyecto.objects.all():
            if a.usuario.id == request.user.id:
                rol_lista = Rol.objects.get(id = a.rol.id)
                for p in Proyecto.objects.all():
                    if p.estado != 'FIN' and p.estado != 'ANU':
                        p.cantidad_dias_transcurridos=int(str((datetime.today().date()-p.fecha_inicio.date()).days))
                        p.save()
                    Sprint_consulta=Sprint.objects.filter(proyecto=p).filter(estado='CON')
                    if Sprint_consulta:
                        for s in Sprint_consulta:
                            if int(s.duracion) <= int(str((datetime.today().date()-s.fecha_inicio.date()).days)):
                                s.estado = 'FIN'
                                s.save()
                    Sprint_activo=Sprint.objects.filter(proyecto=p).filter(estado='ACT')    
                    if Sprint_activo and not Sprint_consulta:
                        for s in Sprint_activo:
                            if s.fecha_inicio.date() <= datetime.today().date():
                                s.estado = 'CON'
                                s.save()
                    if p.id == a.proyecto.id:
                        if rol_lista.tiene_permiso('Can change proyecto'):
                            roles_enlace.append(rol_lista)
                        else:
                            roles_sin_enlace.append(rol_lista)
                            if rol_lista.tiene_permiso('Visualizar proyecto') and rol_lista.tiene_permiso('Visualizar equipo'):
                                proyecto_cliente.append(a.proyecto.id)
            if roles_enlace:
                if proyectos_enlace.has_key(a.proyecto):
                    r=list(set(roles_enlace+proyectos_enlace[a.proyecto]))
                    proyectos_enlace[a.proyecto]=r
                else:
                    proyectos_enlace[a.proyecto]=roles_enlace
                roles_enlace=[]
                    
            if roles_sin_enlace:
                if proyectos_sin_enlace.has_key(a.proyecto):
                    r=list(set(roles_sin_enlace+proyectos_sin_enlace[a.proyecto]))
                    proyectos_sin_enlace[a.proyecto]=r
                else:
                    proyectos_sin_enlace[a.proyecto]=roles_sin_enlace
                roles_sin_enlace = []
        proyectos_completo=[]
        for p in Proyecto.objects.all():
            if (proyectos_sin_enlace.has_key(p) or proyectos_enlace.has_key(p)):
                proyectos_completo.append(p)
                    
        proyecto_cliente=set(proyecto_cliente)
        return render(request,'hola.html',{'proyectos_completo':proyectos_completo,'proyecto_cliente':proyecto_cliente, 'usuario':request.user, 'proyectos_enlace':proyectos_enlace, 'proyectos_sin_enlace':proyectos_sin_enlace})


        

def holaScrumView(request,usuario_id,proyectoid,rol_id):
    """
    Vista especial para el usuario scrum en la que le listan los proyectos y los enlaces para la creacion de roles y flujos
    Vista para los usuario comunes, en la que solo se listan los proyectos sin enlaces, ya que no tiene permiso para ello.
        :param func: request
        :param args: usuario_id,proyectoid,rol_id
        :returns: 'rol-flujo-para-scrum.html'
    """
    proyectox=Proyecto.objects.get(id=proyectoid)
    usuario=MyUser.objects.get(id=usuario_id)
    rolx=Rol.objects.get(id=rol_id)
    enlaces=[]
    HUs=[]
    HUsm=[]
    HUs_add_horas=[]
    HUsm_horas_agotadas=[]
    HUsm_no_desarrolladas=[]
    enlacef=[]
    enlacefm=[]
    enlacefv=[]
    enlaceHU=[]
    enlaceHUv=[]
    enlaceHUm=[]
    enlaceHUa=[]
    enlaceHU_agregar=[]
    enlaceSprint=[]
    enlaceSprintv=[]
    enlaceSprintm=[]
    is_Scrum=0
    HUsa=0
    kanban=0
    class enlacex:
        """
        La clase  permite enviar al html solo las url que se corresponden con los permisos contenidos
        en el rol del usuario.
        """
        def __init__(self,urlx,nombrex):
            self.url=urlx
            self.nombre=nombrex
    class usu_hs:
        """Guarda el usuario y las horas acumualadas"""
        def __init__(self,usuario, hs, cont_hu, list_hu):
            self.usuario=usuario
            self.hs=hs
            self.cont_hu=cont_hu
            self.list_hu=list_hu
    
    if rolx.tiene_permiso('Can add rol'):
            roles=Rol.objects.all()
    else:
            roles =[]#lista vacia si no tiene permiso de ver roles
    
    roles_modificables=[]
    roles_inmodificables=[]
    for r in roles:
        roles_inmodificables.append(r)
            
    if rolx.tiene_permiso('Can add flujo'):
        """Tiene permiso de crear un nuevo flujo, obtengo todos los flujos y enlancef envia el url de crear con el nombre del
        permiso correspondiente al rol-flujo-para-scrum.html"""
        flujos=Flujo.objects.all()
        enlacef.append(enlacex('/crearFlujo/'+usuario_id+'/'+proyectoid+'/'+rol_id,'Agregar Flujo'))
    else:
        flujos = []#lista vacia si no tiene permiso de ver flujos
        
    if rolx.tiene_permiso('Can change flujo'):
        """Tiene permiso de modificar flujo, obtengo todos los flujos para enviar al rol-flujo-para-scrum.html"""
        flujosm=Flujo.objects.all()
        for flujo in flujosm:
            for s in Sprint.objects.all():
                if s.estado == 'CON':
                    for f in s.flujo.all():
                        if f == flujo:
                            flujosm=flujosm.exclude(id=f.id)
        flujos=Flujo.objects.all()
        enlacefm.append(enlacex(usuario_id+'/'+proyectoid+'/'+rol_id,'Modificar Flujo'))
    else:
        flujosm = []#lista vacia si no tiene permiso de ver flujos
        
    if rolx.tiene_permiso('Can add flujo') or rolx.tiene_permiso('Can change flujo'):
        enlacefv.append(enlacex(usuario_id+'/'+proyectoid+'/'+rol_id,'Visualizar'))
    
    if rolx.tiene_permiso('Can add hu'):
        HUs = HU.objects.filter(proyecto=proyectox).filter(estado='ACT')
        enlaceHU.append(enlacex('/crearHU/'+usuario_id+'/'+proyectoid+'/'+rol_id,'Agregar HU'))

    HU_no_asignada_owner=[]
    HU_asignada_owner=[]
    if rolx.tiene_permiso('Can change hu'):
        HUs = HU.objects.filter(proyecto=proyectox)
        HUsm = HU.objects.filter(proyecto=proyectox)
        for HUa in HU.objects.filter(proyecto=proyectox):
            x=0
            for d in AsignaHU_Usuario.objects.all():
                if d.hu == HUa:
                    x=1
            if x == 0:
                HU_no_asignada_owner.append(HUa)
            else:
                HU_asignada_owner.append(HUa)
 
        enlaceHUm.append(enlacex(usuario_id+'/'+proyectoid+'/'+rol_id,'Modificar'))
        is_Scrum=0
    elif rolx.tiene_permiso('Can change hu nivel Scrum'):
        HUs = HU.objects.filter(proyecto=proyectox).filter(valido=True)
        HUsm = HU.objects.filter(proyecto=proyectox).filter(valido=True)
        for h in HUsm:
            if h.sprint():
                if h.sprint().estado != 'ACT' and h.sprint().estado != 'CAN':
                    HUs=HUs.exclude(id=h.id)
            if h.estado_en_actividad != "FIN" and h.estado_en_actividad !='APR' and h.duracion == h.acumulador_horas and h.acumulador_horas !=0:
                HUsm_horas_agotadas.append(h)
        hus_desarrollandose=[]
        for s in Sprint.objects.filter(proyecto=proyectox):
            if s.estado == 'CON':
                hus_desarrollandose=s.hu.all()
        for h in HUsm:
            x=0
            for hu in hus_desarrollandose:
                if h == hu:
                    x=1
            if x == 0:
                HUsm_no_desarrolladas.append(h)
        
        enlaceHUm.append(enlacex(usuario_id+'/'+proyectoid+'/'+rol_id,'Modificar'))
        is_Scrum=1
    
    if rolx.tiene_permiso('Can add hu') or rolx.tiene_permiso('Can change hu') or rolx.tiene_permiso('Can change hu nivel Scrum'):
        enlaceHUv.append(enlacex(usuario_id+'/'+proyectoid+'/'+rol_id,'Visualizar'))
        
    agregar_horas=[]
    if rolx.tiene_permiso('Agregar horas trabajadas'):
        for d in AsignaHU_Usuario.objects.all():
            if d.hu.proyecto == proyectox and str(d.usuario.id) == usuario_id:
                if d.hu.estado == 'ACT':
                    HUs_add_horas.append(d.hu)
        #HU ordenada por prioridad
        HUs_add_horas=sorted(HUs_add_horas,key=lambda x: x.prioridad, reverse=True)
        enlaceHU_agregar.append(enlacex(usuario_id+'/'+proyectoid+'/'+rol_id,'Agregar horas'))
        i=0
        for p in HUs_add_horas:
            if p.acumulador_horas != p.duracion and p.estado_en_actividad != 'FIN' and p.sprint().fecha_inicio.date() <= datetime.today().date():
                agregar_horas=HUs_add_horas[i]             
                break
            i=i+1
        is_Scrum=2
        
    if rolx.tiene_permiso('Can add sprint'):
        if len(Sprint.objects.filter(proyecto=proyectox).filter(estado='ACT')) < 1:
            enlaceSprint.append(enlacex('/crearSprint/'+usuario_id+'/'+proyectoid+'/'+rol_id,'Agregar Sprint'))
    else:
        sprints = []#lista vacia si no tiene permiso de ver flujos
    if rolx.tiene_permiso('Can change sprint'):
        """Tiene permiso de modificar flujo, obtengo todos los flujos para enviar al rol-flujo-para-scrum.html"""
        sprintsm=Sprint.objects.filter(proyecto=proyectox)
        for s in sprintsm:
            if s.estado == 'FIN' or s.estado == 'CON':
                sprintsm=sprintsm.exclude(id=s.id)
        sprints=Sprint.objects.filter(proyecto=proyectox)
        enlaceSprintm.append(enlacex(usuario_id+'/'+proyectoid+'/'+rol_id,'Modificar Sprint'))
    else:
        sprintsm = []#lista vacia si no tiene permiso de ver flujos
        
    if rolx.tiene_permiso('Can add sprint') or rolx.tiene_permiso('Can change sprint'):
        enlaceSprintv.append(enlacex(usuario_id+'/'+proyectoid+'/'+rol_id,'Visualizar'))
    existe=0
    if Sprint.objects.filter(proyecto=proyectox).filter(estado='CON'):
        existe=1

    finalizar=0
    if proyectox.estado == 'ACT':
        finalizar=1
        for h in HU.objects.filter(proyecto=proyectox).filter(valido=True):
            if h.estado_en_actividad != 'APR':
                finalizar=0
 
    return render(request,'rol-flujo-para-scrum.html',{'finalizar':finalizar,'fecha_inicio':str(proyectox.fecha_inicio)[:10],'existe':existe,'proyecto':proyectox,'HUsm_no_desarrolladas':HUsm_no_desarrolladas,'HUsm_horas_agotadas':HUsm_horas_agotadas,'roles_inmodificables':roles_inmodificables,'roles_modificables':roles_modificables,'sprints':sprints,'enlaceSprint':enlaceSprint,'sprintsm':sprintsm,'enlaceSprintm':enlaceSprintm,'enlaceSprintv':enlaceSprintv,'enlaceHUa':enlaceHUa,'HUsa':HUsa,'is_Scrum':is_Scrum,'HUs_add_horas':HUs_add_horas, 'enlaceHU_agregar':enlaceHU_agregar,'enlaceHUm':enlaceHUm,'HUsm':HUsm,'enlaceHUv':enlaceHUv,'HUs':HUs,'enlaceHU':enlaceHU,'enlacefv':enlacefv,'enlacefm':enlacefm,'enlacef':enlacef,'enlaces':enlaces,'roles':roles,'flujosm':flujosm, 'flujos':flujos,'proyecto':proyectox,'usuario':usuario,'rolid':rol_id, 'HU_asignada_owner':HU_asignada_owner, 'HU_no_asignada_owner':HU_no_asignada_owner, 'HU_cargar':agregar_horas, 'kanban':kanban})
 
        
        

class FormularioRolProyecto(forms.ModelForm):
    """
    Clase que obtiene el formulario para la creacion, visualizacion y modificacion
    de roles de proyecto desde la vista del Scrum.
    """
    class Meta:
        model= Rol
        fields=['permisos','nombre_rol','descripcion']



def visualizarRolProyectoView(request,usuario_id,proyectoid, rolid, rol_id_rec):
    """
    Vista que utiliza el formulario RolProyecto para desplegar los datos almacenados
    en el Rol que se quiere visualizar
        :param func: request
        :param args: usuario_id,proyectoid, rolid, rol_id_rec
        :returns: 'visualizarRol.html'
    """
    rolproyecto= Rol.objects.get(id=rol_id_rec)
    formulario =  FormularioRolProyecto(initial={
                                                     'nombre_rol': rolproyecto.nombre_rol,
                                                     'permisos': rolproyecto.permisos,
                                                     'descripcion': rolproyecto.descripcion,
            
                                                     }) 
    return render_to_response('visualizarRol.html',{'formulario':formulario, 'rol':rolproyecto, 'proyectoid':proyectoid,'usuarioid':usuario_id,'rolid':rolid},
                                  context_instance=RequestContext(request))





def guardarFlujoView(request, usuario_id, proyectoid, rolid):
    """
    Vista de guardado de un nuevo flujo en la base de datos
    que se utiliza en la interfaz devuelta por /crearFlujo/ 
        :param func: request
        :param args: usuario_id, proyectoid, rolid 
        :returns: 'crearFlujo.html'
        :rtype: nombre, estado
    """
    
    actividades_disponibles=Actividades.objects.all()
    actividades_asignadas=[]
    guardar=0
    for g in request.POST.getlist('_save'):
        if g == 'Guardar':
            guardar=1
    if guardar == 1:
        flujo_a_crear = Flujo.objects.create(nombre=request.POST['nombre'])
        orden=[]
        for p in request.POST.getlist('actividades'):
            orden.append(Actividades.objects.get(id=p).id)
            flujo_a_crear.actividades.add(Actividades.objects.get(id=p))
        flujo_a_crear.orden_actividades=json.dumps(orden)
        flujo_a_crear.save()
        
        usuarioe = MyUser.objects.get(id=usuario_id).username
        proyectoe = Proyecto.objects.get(id=proyectoid).nombre
        evento_e="Estimado usuario "+ usuarioe+ ", se ha creado un nuevo flujo de nombre: '"+request.POST['nombre']+"' con fecha y hora: "+str(timezone.now().strftime("%Y/%m/%d %H:%M:%S"))+" en el proyecto "+proyectoe
        email_e=str(MyUser.objects.get(id=usuario_id).email)
        send_email(str(email_e), 'Notificacion', evento_e)
            
            
        return HttpResponse('El flujo se ha creado')
    else:
        if request.POST['boton'] == 'Agregar':
            act_asi=request.POST.getlist('actividades_asignadas')
            for a in act_asi:
                actividades_disponibles=actividades_disponibles.exclude(id=a)
                actividades_asignadas.append(Actividades.objects.get(id=a))
            act_dis=request.POST.getlist('actividades_disponibles')
            for a in act_dis:
                actividades_asignadas.append(Actividades.objects.get(id=a))
                actividades_disponibles=actividades_disponibles.exclude(id=a)
            return render(request, 'crearFlujo.html',{'nombre_flujo':request.POST['nombre'],'proyectoid':proyectoid,'usuarioid':usuario_id,'rolid':rolid ,'actividades_asignadas':actividades_asignadas,'actividades':actividades_disponibles})
        elif request.POST['boton'] == 'Eliminar':
            act_asi=request.POST.getlist('actividades_asignadas')
            for a in act_asi:
                actividades_disponibles=actividades_disponibles.exclude(id=a)
                actividades_asignadas.append(Actividades.objects.get(id=a))
            return render(request, 'crearFlujo.html',{'nombre_flujo':request.POST['nombre'],'proyectoid':proyectoid,'usuarioid':usuario_id,'rolid':rolid ,'actividades_asignadas':actividades_asignadas,'actividades':actividades_disponibles})     


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
        
        

def visualizarFlujoProyectoView(request,usuario_id, proyectoid, rolid, flujo_id_rec):
    """
    Vista que utiliza el formulario FlujoProyecto para desplegar los datos almacenados
    en el Flujo que se quiere visualizar.
        :param func: request
        :param args: usuario_id, proyectoid, rolid, flujo_id_rec 
        :returns: visualizarFlujo.html
    """
    flujo_disponible= Flujo.objects.get(id=flujo_id_rec)
    jsonDec = json.decoder.JSONDecoder()
    orden=jsonDec.decode(flujo_disponible.orden_actividades)
    formulario =  FormularioRolProyecto(initial={
                                                     'nombre': flujo_disponible.nombre,
                                                     'actividades': flujo_disponible.actividades,
                                                     })      
    return render_to_response('visualizarFlujo.html',{'formulario':formulario, 'orden':orden,'flujo':flujo_disponible, 'proyectoid':proyectoid,'usuarioid':usuario_id, 'rolid':rolid},
                                  context_instance=RequestContext(request))

    
    
def modificarFlujo(request, usuario_id, proyectoid, rolid, flujo_id_rec):
    """
    Vista que utiliza el formulario FlujoProyecto para desplegar los datos editables
    del Flujo que se quiere modificar.
        :param func: request
        :param args: usuario_id, proyectoid, rolid, flujo_id_rec
        :returns: modificarFlujo.html
        :rtype: nombre
    """
    actividades_disponibles=Actividades.objects.all()
    actividades_asignadas=[]
    #estados=['ACT','CAN']
    f=Flujo.objects.get(id=flujo_id_rec)
    guardar=0
    for g in request.POST.getlist('_save'):
        if g == 'Guardar':
            guardar=2
        elif g=='Guardar nuevo':
            guardar=1
    if request.method == 'POST':
        if guardar ==0:
            if request.POST['boton'] == 'Agregar':
                act_asi=request.POST.getlist('actividades_asignadas')
                if act_asi:
                    for a in act_asi:
                        actividades_disponibles=actividades_disponibles.exclude(id=a)
                        actividades_asignadas.append(Actividades.objects.get(id=a))
                act_dis=request.POST.getlist('actividades_disponibles')
                for a in act_dis:
                    actividades_asignadas.append(Actividades.objects.get(id=a))
                    actividades_disponibles=actividades_disponibles.exclude(id=a)
                ctx = {'actividades_asignadas':actividades_asignadas,'actividades':actividades_disponibles,'flujo':f, 'proyectoid':proyectoid,'usuarioid':usuario_id, 'rolid':rolid}
                return render(request,'modificarFlujo.html', ctx)
            elif request.POST['boton'] == 'Eliminar':
                act_asi=request.POST.getlist('actividades_asignadas')
                for a in act_asi:
                    actividades_disponibles=actividades_disponibles.exclude(id=a)
                    actividades_asignadas.append(Actividades.objects.get(id=a))
                ctx = {'actividades_asignadas':actividades_asignadas,'actividades':actividades_disponibles,'flujo':f, 'proyectoid':proyectoid,'usuarioid':usuario_id, 'rolid':rolid}
                return render(request,'modificarFlujo.html', ctx)
        elif guardar == 1:
            nombre=request.POST['nombre']
            try:
                flujo_a_crear = Flujo.objects.create(nombre=nombre)
                orden=[]
                for p in request.POST.getlist('actividades_asignadas'):
                    orden.append(Actividades.objects.get(id=p).id)
                    flujo_a_crear.actividades.add(Actividades.objects.get(id=p))
                flujo_a_crear.orden_actividades=json.dumps(orden)
                flujo_a_crear.save()

                usuarioe = MyUser.objects.get(id=usuario_id).username
                proyectoe = Proyecto.objects.get(id=proyectoid).nombre
                evento_e="Estimado usuario "+ usuarioe+ ", El flujo '"+request.POST['nombre']+" ha sido creado exitosamente en la fecha y hora: "+str(timezone.now().strftime("%Y/%m/%d %H:%M:%S"))+" en el proyecto "+proyectoe
                email_e=str(MyUser.objects.get(id=usuario_id).email)
                send_email(str(email_e), 'Notificacion', evento_e)


                return HttpResponse('El flujo nuevo se ha creado')  
            except ObjectDoesNotExist:
                print "No se ha podido crear el nuevo flujo"

            usuarioe = MyUser.objects.get(id=usuario_id).username
            proyectoe = Proyecto.objects.get(id=proyectoid).nombre
            evento_e="Estimado usuario "+ usuarioe+ ", El flujo '"+request.POST['nombre']+"' ha sido creado exitosamente en la fecha y hora: "+str(timezone.now().strftime("%Y/%m/%d %H:%M:%S"))+" en el proyecto "+proyectoe
            email_e=str(MyUser.objects.get(id=usuario_id).email)
            send_email(str(email_e), 'Notificacion', evento_e)

            return HttpResponse('El flujo ha sido creado exitosamente')
        elif guardar == 2:
            nombre=request.POST['nombre']

            f.nombre=nombre
     
            orden=[]
            f.actividades=[]
            f.orden_actividades=orden
            for p in request.POST.getlist('actividades_asignadas'):
                orden.append(Actividades.objects.get(id=p).id)
                f.actividades.add(Actividades.objects.get(id=p))
            f.orden_actividades=json.dumps(orden)
            f.save() #Guardamos el modelo de manera Editada
            
            usuarioe = MyUser.objects.get(id=usuario_id).username
            proyectoe = Proyecto.objects.get(id=proyectoid).nombre
            evento_e="Estimado usuario "+ usuarioe+ ", El flujo '"+request.POST['nombre']+" ha sido modificado exitosamente en la fecha y hora: "+str(timezone.now().strftime("%Y/%m/%d %H:%M:%S"))+" en el proyecto "+proyectoe
            email_e=str(MyUser.objects.get(id=usuario_id).email)
            send_email(str(email_e), 'Notificacion', evento_e)
            
            return HttpResponse('El flujo ha sido modificado exitosamente')
    else:
        actividades_asignadas=[]
        actividades_disponibles=[]
        jsonDec = json.decoder.JSONDecoder()
        orden=jsonDec.decode(f.orden_actividades)
        for o in orden:
            for a in f.actividades.all():
                if a.id == o:
                    actividades_asignadas.append(a)
        for a in Actividades.objects.all():
            x=0
            for asig in actividades_asignadas:
                if a == asig:
                    x=1
            if x == 0:
                actividades_disponibles.append(a)
        
        ctx = {'actividades_asignadas':actividades_asignadas,'actividades':actividades_disponibles,'flujo':f, 'proyectoid':proyectoid,'usuarioid':usuario_id, 'rolid':rolid}
        return render_to_response('modificarFlujo.html', ctx ,context_instance=RequestContext(request))    
    
    
    

def crearFlujo(request,usuario_id,proyectoid,rolid):
    """
    Vista que realiza la creacion de flujos de proyecto desde la vista del Scrum.
        :param func: request
        :param args: usuario_id,proyectoid,rolid
        :returns: crearFlujo.html
    """
    actividades_asignadas=[]
    actividades_disponibles=Actividades.objects.all()
    if request.method == 'GET':
        return render(request, 'crearFlujo.html',{'actividades_asignadas':actividades_asignadas,'actividades':actividades_disponibles,'usuarioid':usuario_id,'proyectoid':proyectoid,'rolid':rolid})



class proyectoFrom(forms.ModelForm):
    """
    Clase que obtiene el formulario para la visualizacion y modificacion de proyectos desde la vista del Scrum.
    """
    class Meta:
        model = Proyecto
        fields = ['nombre', 'descripcion','duracion']


def modificarProyecto(request, usuario_id, proyecto_id_rec):
    """
    Vista que utiliza el formulario proyectoFrom para desplegar los datos editables
    del Proyecto que se quiere modificar.
        :param func: request
        :param args: usuario_id, proyecto_id_rec
        :returns: modificarProyecto.html
        :rtype: nombre, descripcion, estado, fecha_inicio, fecha_fin
    """
    p=Proyecto.objects.get(id=proyecto_id_rec)
    if request.method == 'POST':
        form = proyectoFrom(request.POST)
        if form.is_valid():

            nombre=form.cleaned_data['nombre']
            descripcion=form.cleaned_data['descripcion']
            duracion=form.cleaned_data['duracion']
            if p.estado == "PEN":
                fecha_inicio=request.POST['fecha_inicio']
                fecha_fin=datetime.strptime(request.POST['fecha_inicio'],"%Y-%m-%d").date() + timedelta(days=int(duracion))
                p.fecha_inicio=fecha_inicio
                p.fecha_fin=fecha_fin
            p.nombre_largo=nombre
            p.descripcion=descripcion
            p.duracion=duracion
            p.save() #Guardamos el modelo de manera Editada


            return HttpResponse('Tu proyecto a sido guardado exitosamente')
    else:
        
        form = proyectoFrom(initial={
                                         'nombre': p.nombre,
                                         'descripcion': p.descripcion,
                                         'duracion':p.duracion,
                                     
                                         })
        ctx = {'form':form, 'fecha_inicio':str(p.fecha_inicio)[:10],'proyecto':p,'usuarioid':usuario_id,'proyecto':p}
        return render_to_response('modificarProyecto.html', ctx ,context_instance=RequestContext(request))
    

def visualizarProyectoView(request,usuario_id, proyecto_id_rec):
    """
    Vista que utiliza el formulario proyectoFrom para desplegar los datos almacenados
    en el Flujo que se quiere visualizar.
        :param func: request
        :param args: usuario_id, proyecto_id_rec
        :returns: visualizarProyecto.html
    """
    proyecto_enc= Proyecto.objects.get(id=proyecto_id_rec)
    return render_to_response('visualizarProyecto.html',{'proyecto':proyecto_enc,'usuarioid':usuario_id},
                                  context_instance=RequestContext(request))


############################################    
def crearActividadView(request,usuario_id,proyectoid):
    """
    Vista que se obtiene del regex al presionar el boton Crear Actividad dentro del formulario
    de creacion o modificacion de Flujos, devolviendo un formulario html para crear una nueva actividad
        :param func: request
        :param args: usuario_id,proyectoid
        :returns: crearActividad.html 
        :rtype: nombre, descripcion
    """   
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
            
            usuarioe = MyUser.objects.get(id=usuario_id).username
            proyectoe = Proyecto.objects.get(id=proyectoid).nombre
            evento_e="Estimado usuario "+ usuarioe+ ", La Actividad '"+form.cleaned_data['nombre']+"' con descripcion '"+form.cleaned_data['descripcion']+"' se ha creado exitosamente en la fecha y hora: "+str(timezone.now().strftime("%Y/%m/%d %H:%M:%S"))+" en el proyecto "+proyectoe
            email_e=str(MyUser.objects.get(id=usuario_id).email)
            send_email(str(email_e), 'Notificacion', evento_e)
            
            return HttpResponse('Ha sido guardado exitosamente') 
    
    

def crearActividadAdminView(request):
    """
    Vista que se obtiene del regex al presionar el boton Crear Actividad dentro del formulario
    de creacion o modificacion de Flujos del admin, devolviendo un formulario html para crear una nueva actividad
        :param func: request
        :returns: crearActividadAdmin.html
        :rtype: nombre, descripcion
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
        :param func: request
        :param args: actividad_id_rec
        :returns: modificarActividadAdmin.html
        :rtype: nombre, descripcion, 
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
        :param func: request
        :param args: usuario_id,proyectoid
        :returns: seleccionarActividad.html
    """
    return render(request,'seleccionarActividad.html',{'actividades':Actividades.objects.all(),'usuarioid':usuario_id,'proyectoid':proyectoid})


def modificarActividad(request,usuario_id,proyectoid,actividad_id_rec):
    """
    Vista que utiliza el formulario formularioActividad para desplegar los datos editables
    de la Actividad que se quiere modificar.
        :param func: request
        :param args: usuario_id,proyectoid,actividad_id_rec
        :returns: modificarActividad.html
        :rtype: nombre, descripcion
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
            
            usuarioe = MyUser.objects.get(id=usuario_id).username
            proyectoe = Proyecto.objects.get(id=proyectoid).nombre
            evento_e="Estimado usuario "+ usuarioe+ ", La actividad '"+form.cleaned_data['nombre']+"' con descripcion '"+form.cleaned_data['descripcion']+"' ha sido modificado exitosamente en la fecha y hora: "+str(timezone.now().strftime("%Y/%m/%d %H:%M:%S"))+" en el proyecto "+proyectoe
            email_e=str(MyUser.objects.get(id=usuario_id).email)
            send_email(str(email_e), 'Notificacion', evento_e)
            
            return HttpResponse('Se ha guardado exitosamente')
    else:
        
        form = formularioActividad(initial={
                                         'nombre': p.nombre,
                                         'descripcion': p.descripcion,                                     
                                         })
        ctx = {'form':form, 'Actividad':p,'usuarioid':usuario_id,'proyectoid':proyectoid}
        return render_to_response('modificarActividad.html', ctx ,context_instance=RequestContext(request)) 


    
def asignarRol(request,usuario_id, proyectoid,rolid, rol_id_rec):
    """
    Vista que permite asignar un rol a un usuario dentro de la vista del Scrum, valiendose de la URL para obtener
    los id's del rol , proyecto y el usuario creador.
        :param func: request
        :param args: usuario_id, proyectoid,rolid, rol_id_rec
        :returns: asignaRolProyecto.html
        :rtype: usuarios
    """
    proyectox=Proyecto.objects.get(id=proyectoid)
    rolx = Rol.objects.get(id=rol_id_rec)
    x=0
    if request.method=='POST':
        try:
            for p in request.POST.getlist('usuarios'):
                u=MyUser.objects.get(id=p)
                for a in AsignarRolProyecto.objects.all():
                    if a.usuario == u and a.rol == rolx and a.proyecto == proyectox:
                        x=1
            if x == 0:
                asignacion_a_crear = AsignarRolProyecto.objects.create(usuario=u,rol=rolx, proyecto=proyectox)
                asignacion_a_crear.save()
            return HttpResponseRedirect('/scrum/'+usuario_id+'/'+proyectoid+'/'+rolid+'/')
        except ObjectDoesNotExist:
            print "Either the entry or blog doesn't exist." 
            return HttpResponseRedirect('/crearFlujo/')
    else:
        usuarios_ya_asignados=[]
        for a in AsignarRolProyecto.objects.all():
            if a.rol == Rol.objects.get(id=rol_id_rec) and a.proyecto == proyectox:
                usuarios_ya_asignados.append(a.usuario)
        usuarios_ya_asignados=set(usuarios_ya_asignados)
        
        usuarios_sin_asignar=[]
        for u in MyUser.objects.all().exclude(id=usuario_id).exclude(username='admin'):
            x=0
            for u_asig in usuarios_ya_asignados:
                if u == u_asig:
                    x=1
            if x==0:
                usuarios_sin_asignar.append(u)
        return render(request,'asignaRolProyecto.html',{'usuarios_sin_asignar':usuarios_sin_asignar,'usuarios_ya_asignados':usuarios_ya_asignados,'proyecto':proyectox,'usuarios':MyUser.objects.all().exclude(id=usuario_id),'proyectoid':proyectoid,'usuarioid':usuario_id, 'rolid':rolid})
    
    
    
    
def listarEquipo(request,proyecto_id_rec,usuario_id):
    """
    Esta vista debe obtener los datos de los usuarios que han sido asignados a un rol en el proyecto,el parametro
    usuario_id se necesita simplemente para el render para poder retornar a rol-flujo-para-scrum
        :param func: request
        :param args: proyecto_id_rec,usuario_id
        :returns: formarEquipo.html 
    """
    lista={}
    proyectox=Proyecto.objects.get(id=proyecto_id_rec)
    for a in AsignarRolProyecto.objects.all():
        if a.proyecto.id == proyectox.id:#si el proyecto relacionado a una asignacion es el que se esta viendo ahora
            rol_a=Rol.objects.get(id=a.rol.id)
            usuario_a=MyUser.objects.get(id=a.usuario.id)
            lista[usuario_a]=rol_a#agregar el usuario de esa asignacion a la vista, y mandarlo al template
    return render(request,'formarEquipo.html',{'roles':Rol.objects.all(),'lista_asigna':lista, 'flujos':Flujo.objects.all(),'proyecto':proyectox,'usuario_id':usuario_id})



def guardarSprintFlujos(request,usuario_id,proyectoid,rolid):
    """Tengo que sacar el guardado de flujos del metodo guardarSprintView y ponerlo aqui y desde 
    aqui redirijir hacia asignaHUActividad_Flujo"""
    """en guardarSprintView tengo que redirigir hacia un html donde se muestren los flujos y des ese dirijirme a este metodo"""
    
    
    sprint_id =  request.POST['sprint']
    
    Sprint_a_crear= Sprint.objects.get(id=sprint_id)
    
    for f in request.POST.getlist('Flujos'):
            Sprint_a_crear.flujo.add(Flujo.objects.get(id=f))
    Sprint_a_crear.save()
    
    return HttpResponseRedirect('/asignarHUFlujo/'+usuario_id+'/'+proyectoid+'/'+rolid+'/'+sprint_id)



 
def guardarSprintView(request, usuario_id, proyectoid, rolid):
    """
    Vista de guardado de un nuevo Sprint en la Base de datos
    que se utiliza en la interfaz devuelta por /crearSprint/
        :param func: request
        :param args: usuario_id, proyectoid, rolid 
        :returns: 'El Sprint se ha creado'
        :rtype: descripcion, fecha_inicio, duracion
    
    """
    guardar=0
    for g in request.POST.getlist('_save'):
        if g == 'Guardar':
            guardar=1
    if guardar == 1:
        try:
            HUs=[]
            HUs_pendientes=[]
            Sprint_a_crear = Sprint.objects.create(descripcion=request.POST['descripcion'],estado="ACT",fecha_inicio=request.POST['fecha_inicio'], duracion=request.POST['duracion'], proyecto=Proyecto.objects.get(id=proyectoid))
            for p in request.POST.getlist('HUs'):
                h=HU.objects.get(id=p)
                Sprint_a_crear.hu.add(h)
                HUs.append(h)#ahora HUs tienen todas las seleccionadas incluso las pendientes
                Sprint_a_crear.save()
            for f in request.POST.getlist('Flujos'):
                Sprint_a_crear.flujo.add(Flujo.objects.get(id=f))
            for u in request.POST.getlist('usuarios'):
                Sprint_a_crear.equipo.add(MyUser.objects.get(id=u))
            Sprint_a_crear.save()
            
            usuarioe = MyUser.objects.get(id=usuario_id).username
            proyectoe = Proyecto.objects.get(id=proyectoid).nombre
            evento_e="Estimado usuario "+ usuarioe+ ", se ha creado un nuevo Sprint de nombre: '"+request.POST['descripcion']+"' con una fecha de inicio '"+str(request.POST['fecha_inicio'])+"' ,duracion '"+str(request.POST['duracion'])+ "' dias, en la fecha y hora:"+str(timezone.now().strftime("%Y/%m/%d %H:%M:%S"))+" en el proyecto "+proyectoe
            email_e=str(MyUser.objects.get(id=usuario_id).email)
            send_email(str(email_e), 'Notificacion', evento_e)
            

            flujos=Flujo.objects.all()
            flujos_pen=[]

            for h in HUs:#por cada hu seleccionada
                if h.estado_en_actividad!='APR':
                    if h not in HUs_pendientes:
                        HUs_pendientes.append(h)
                    if h.flujo() not in flujos_pen:
                        flujos_pen.append(h.flujo())
                    if h.flujo() in flujos:   
                        flujos=flujos.exclude(id=h.flujo().id)
                    HUs.remove(h)#HUs es una lista porque se definio asi pero flujos se obtuvo con un query
            #asi HU tiene todas las HU no pendientes 
            #y HU_pendientes tiene las HU pendientes
            HUs_pendientes=set(HUs_pendientes)

            return render(request,"eleccionFlujo.html",{'sprint':Sprint_a_crear,'HUs_pendientes':HUs_pendientes,'HUs':HUs,'flujo_pen':flujos_pen,'flujos':flujos,'usuarioid':usuario_id,'proyectoid':proyectoid,'rolid':rolid})
        except ObjectDoesNotExist:
            print "Either the entry or blog doesn't exist." 
            return HttpResponseRedirect('/crearSprint/')
    else:
        if request.POST['boton'] == 'Calcular':
            proyectox = Proyecto.objects.get(id=proyectoid)
            HUs = HU.objects.filter(proyecto=proyectox).filter(valido=True)
            flujos=Flujo.objects.all()#le mando todos los flujos para que elija los que quiere
            HUs_pendientes=[]
            for x in Sprint.objects.filter(proyecto=proyectox):
                if x.estado != 'FIN':
                    for h in x.hu.all():
                        HUs=HUs.exclude(id=h.id)
                elif x.estado != 'CON':
                    for h in x.hu.all():
                        if h.estado_en_actividad == 'FIN' or h.estado_en_actividad == 'APR':
                            HUs=HUs.exclude(id=h.id)
                        else:
                            HUs_pendientes.append(h)
                            HUs=HUs.exclude(id=h.id)
            sum=0
            hus_seleccionadas=[]
            HUs_no_seleccionadas=HUs
            HUs_pendientes_no_seleccionadas=HUs_pendientes
            HUs_pendientes=[]
            flujos_pen=[]
            for h in request.POST.getlist('HUs'):
                x=0
                for hp in HUs_pendientes_no_seleccionadas:
                    if hp == HU.objects.get(id=h):
                        x=1
                if x == 1:
                    HUs_pendientes_no_seleccionadas.remove(HU.objects.get(id=h))
                    HUs_pendientes.append(HU.objects.get(id=h))
                    flujos_pen.append((HU.objects.get(id=h)).flujo())
                else:
                    hus_seleccionadas.append(HU.objects.get(id=h))
                    HUs_no_seleccionadas=HUs_no_seleccionadas.exclude(id=h)
                sum=sum+HU.objects.get(id=h).duracion
            flujos_pen=set(flujos_pen)
            for f in flujos_pen:
                for flu in flujos:
                    if flu == f:
                        flujos=flujos.exclude(id=f.id)
                
            equipo_seleccionado=[]
            equipo_no_seleccionado=[]
            asignaciones= AsignarRolProyecto.objects.filter(proyecto=proyectox)#obtuve todas las asignaciones para este proyecto
            for a in asignaciones:
                
                rola = a.rol
                if rola.tiene_permiso('Agregar horas trabajadas'):
                    equipo_no_seleccionado.append(a.usuario)
                #equipo_no_seleccionado.append(a.usuario)
                
            horas=0
            for u in request.POST.getlist('usuarios'):
                horas=horas+8
                equipo_seleccionado.append(MyUser.objects.get(id=u))
                equipo_no_seleccionado.remove(MyUser.objects.get(id=u))
            
            fecha_fin=datetime.strptime(request.POST['fecha_inicio'],"%Y-%m-%d").date() + timedelta(days=math.ceil(sum/horas))
            
        return render(request, 'crearSprint.html',{'fecha_fin':fecha_fin,'equipo_pen':equipo_seleccionado,'equipo':equipo_no_seleccionado,'flujos_pen':flujos_pen,'HUs_pendientes_no_seleccionadas':HUs_pendientes_no_seleccionadas,'HUs_pendientes':HUs_pendientes,'nombre':request.POST['descripcion'],'duracion':math.ceil(sum/horas),'flujos':flujos,'HUs':HUs,'HUs_seleccionadas':hus_seleccionadas,'HUs_no_seleccionadas':HUs_no_seleccionadas,'fecha_ahora':request.POST['fecha_inicio'],'usuarioid':usuario_id,'proyectoid':proyectoid,'rolid':rolid})
    
    
    
    
    
def guardarHUView(request,usuario_id, proyectoid, rolid):
    """
    Vista de guardado de una nueva HU en la base de datos creada por el Product Owner
    que se utiliza en la interfaz devuelta por /crearHU/
        :param func: request
        :param args: proyectoid 
        :returns: 'La HU se ha creado y relacionado con el proyecto'
        :rtype: descripcion, valor_negocio
    """
    try:
        proyectox = Proyecto.objects.get(id=proyectoid)
        HU_a_crear = HU.objects.create(descripcion=request.POST['descripcion'],estado="ACT",valor_negocio=request.POST['valor_negocio'], valor_tecnico=0, prioridad=0, duracion=0, acumulador_horas=0, estado_en_actividad='PEN',proyecto=proyectox,valido=False)
        HU_a_crear.save()
        
        usuarioe = MyUser.objects.get(id=usuario_id).username
        proyectoe = Proyecto.objects.get(id=proyectoid).nombre
        evento_e="Estimado usuario "+ usuarioe+ ", se ha creado un nuevo HU de nombre: '"+request.POST['descripcion']+"' con valor de negocio '"+request.POST['valor_negocio']+"' con fecha y hora: "+str(timezone.now().strftime("%Y/%m/%d %H:%M:%S"))+" en el proyecto "+proyectoe
        email_e=str(MyUser.objects.get(id=usuario_id).email)
        send_email(str(email_e), 'Notificacion', evento_e)
        

        return HttpResponse('La HU se ha creado y relacionado con el proyecto')  
    except ObjectDoesNotExist:
        print "Either the entry or blog doesn't exist." 
        return HttpResponseRedirect('/crearHU/')

    
    
    
def guardarHUProdOwnerView(request,usuario_id, proyectoid, rolid, HU_id_rec,is_Scrum):
    """
    Vista de guardado de la modificacion de una HU existente modificada por el Product Owner
    que se utiliza en la interfaz devuelta por /modificarHU/ 
    0 corresponde a la modificaci[on realizada por el Product Owner
        :param func: request
        :param args: usuario_id, proyectoid, rolid, HU_id_rec,is_Scrum 
        :returns: 'La descripcion y valor de negocio de la HU a sido modificado exitosamente'
        :rtype: descripcion, valor_negocio, estado 
    1 coresponde a la modificaci[on realizada por el Scrum
        :param func: request
        :param args: usuario_id, proyectoid, rolid, HU_id_rec,is_Scrum 
    2 corresponde a la modificaci[on realizada por el Equipo
        :param func: request
        :param args: usuario_id, proyectoid, rolid, HU_id_rec,is_Scrum 
        :returns: 'modificarHU.html'
        :rtype: agregar_horas, descripcion_horas    
    """
          
    h=HU.objects.get(id=HU_id_rec)
    if request.method == 'POST':
        if is_Scrum == '0':
            
            
            valor_negocio=request.POST['valor_negocio']
            descripcion=request.POST['descripcion']
            estado=request.POST['estado']
            h.valor_negocio=valor_negocio
            h.descripcion=descripcion
            h.estado=estado
            h.save() #Guardamos el modelo de manera Editada
            
            usuarioe = MyUser.objects.get(id=usuario_id).username
            proyectoe = Proyecto.objects.get(id=proyectoid).nombre
            evento_e="Estimado usuario "+ usuarioe+ ", se ha modificado '"+request.POST['descripcion']+"' con valor de negocio '"+request.POST['valor_negocio']+"' y estado '"+request.POST['estado']+" con fecha y hora: "+str(timezone.now().strftime("%Y/%m/%d %H:%M:%S"))+" en el proyecto "+proyectoe
            email_e=str(MyUser.objects.get(id=usuario_id).email)
            send_email(str(email_e), 'Notificacion', evento_e)       
            
            return HttpResponse('La descripcion y valor de negocio de la HU a sido modificado exitosamente')
        else:
            acumulador=0
            prueba=request.POST['horas_agregar']
            acumulador=acumulador + float(prueba)
            y=str(timezone.now())
            for horas in h.hu_descripcion.all():
                x=str(horas.fecha)
                if x[:10] == y[:10]:
                    acumulador=horas.horas_trabajadas + acumulador
            if acumulador<9:
                s=h.sprint()
                if s is not None and s.termino_Sprint():
                    s.estado='FIN'
                guardar=0
                for g in request.POST.getlist('_save'):
                    if g == 'Guardar':
                        guardar=1
                if guardar == 1:
                    try:
                        proyectox=Proyecto.objects.get(id=h.proyecto.id)
                        horas_a_agregar = request.POST['horas_agregar']
                        descripcion_horas=request.POST['descripcion_horas']
                        acumulador_horas = float(horas_a_agregar)+h.acumulador_horas
                        if h.duracion >= acumulador_horas:
                            h.acumulador_horas=acumulador_horas
                            h.estado_en_actividad='PRO'
                            h.save()
                            if proyectox.estado == 'PEN' and acumulador_horas > 0:
                                proyectox.estado='ACT'
                                proyectox.save()
                            if s is not None:
                                if s.estado == 'ACT' and acumulador_horas >0:
                                    s.estado='CON'
                                    s.save()
                                    
                            usuarioe = MyUser.objects.get(id=usuario_id).username
                            proyectoe = Proyecto.objects.get(id=proyectoid).nombre
                            evento_e="Estimado usuario "+ usuarioe+ ", se ha agregado '"+str(request.POST['horas_agregar'])+"' horas a la '"+str(h.descripcion)+"' con una descripcion '"+request.POST['descripcion_horas']+"' estando en la actividad '"+ str(h.actividad)+ "' con el estado '"+str(h.estado_en_actividad)+"' con fecha y hora "+str(timezone.now().strftime("%Y/%m/%d %H:%M:%S"))+" en el proyecto "+proyectoe
                            email_e=str(MyUser.objects.get(id=usuario_id).email)
                            send_email(str(email_e), 'Notificacion', evento_e)  
                  
                            hd=Horas_Trabajadas.objects.create(horas_trabajadas=horas_a_agregar,descripcion_horas_trabajadas=descripcion_horas,fecha=datetime.now(), actividad=str(h.actividad), estado=str(h.estado_en_actividad))
                            h.hu_descripcion.add(Horas_Trabajadas.objects.get(id=hd.id))
                            hd.save()
                            return render(request,'modificarHU.html', {'HU':h, 'proyectoid':proyectoid,'usuarioid':usuario_id, 'rolid':rolid,'is_Scrum':2})
                        else:
                            return HttpResponse('Contactar con el Scrum para aumentar la duracion de la HU, ya que ha sobrepasado el tiempo de realizacion de HU')
                    except ObjectDoesNotExist:
                        print "Either the entry or blog doesn't exist." 
                        return HttpResponseRedirect('/crearHU/')
                else:
                    if request.POST['boton'] == 'Finalizar':
                        for a in AsignaHU_flujo.objects.all():
                            for hu in a.lista_de_HU.all():
                                if hu==h:
                                    flujo=a.flujo_al_que_pertenece
                                    break
                        jsonDec = json.decoder.JSONDecoder()
                        orden=jsonDec.decode(flujo.orden_actividades)
                         
                        proyectox=Proyecto.objects.get(id=h.proyecto.id)
                        horas_a_agregar = request.POST['horas_agregar']
                        descripcion_horas=request.POST['descripcion_horas']
                        fecha=timezone.now()

                        acumulador_horas = float(horas_a_agregar)+h.acumulador_horas
                        if h.duracion >= acumulador_horas:
                            h.acumulador_horas=acumulador_horas
                            h.save()
                        x=1
                        for o in orden:
                            if Actividades.objects.get(id=o) == h.actividad:
                                break
                            else:
                                x=x+1
                        if x >= len(orden) and h.acumulador_horas <= h.duracion:
                            h.estado_en_actividad='FIN'
                            h.save()
                            hd=Horas_Trabajadas.objects.create(horas_trabajadas=horas_a_agregar,descripcion_horas_trabajadas=descripcion_horas, fecha=fecha, actividad=str(h.actividad), estado=str(h.estado_en_actividad))
                            h.hu_descripcion.add(Horas_Trabajadas.objects.get(id=hd.id))
                            hd.save()
                                   
                            usuarioe = MyUser.objects.get(id=usuario_id).username
                            proyectoe = Proyecto.objects.get(id=proyectoid).nombre
                            evento_e="Estimado usuario "+ usuarioe+ ", Se ha agregado '"+request.POST['horas_agregar']+"' horas a la '"+h.descripcion+"' con una descripcion '"+request.POST['descripcion_horas']+"' quedando asi finalizadas las actividades con fecha y hora"+str(timezone.now().strftime("%Y/%m/%d %H:%M:%S"))+" en el proyecto "+proyectoe
                            email_e=str(MyUser.objects.get(id=usuario_id).email)
                            send_email(str(email_e), 'Notificacion', evento_e)       
                                                 
                            return HttpResponse("Todas las actividades de HU finalizadas")
                        elif x < len(orden) and h.acumulador_horas == h.duracion:
                            h.estado_en_actividad='PEN'
                            h.save()
                            estadoP='PRO'
                            hd=Horas_Trabajadas.objects.create(horas_trabajadas=horas_a_agregar,descripcion_horas_trabajadas=descripcion_horas, fecha=fecha, actividad=str(h.actividad), estado=estadoP)
                            h.hu_descripcion.add(Horas_Trabajadas.objects.get(id=hd.id))
                            hd.save()
                            
                            usuarioe = MyUser.objects.get(id=usuario_id).username
                            proyectoe = Proyecto.objects.get(id=proyectoid).nombre
                            evento_e="Estimado usuario "+ usuarioe+ ", Se ha agregado '"+request.POST['horas_agregar']+"' horas a la '"+h.descripcion+"' con una descripcion '"+request.POST['descripcion_horas']+"' ,completando la duracion sin terminar todas las actividades con fecha y hora: "+str(timezone.now().strftime("%Y/%m/%d %H:%M:%S"))+" en el proyecto "+proyectoe
                            email_e=str(MyUser.objects.get(id=usuario_id).email)
                            send_email(str(email_e), 'Notificacion', evento_e) 
                            
                            return HttpResponse("Duracion de HU finalizada sin terminar todas las actividades. Contactar con el Scrum")
                        else:
                            h.actividad=Actividades.objects.get(id=orden[x])
                            h.estado_en_actividad='PEN'
                            h.save()
                            estadoP='PRO'
                            hd=Horas_Trabajadas.objects.create(horas_trabajadas=horas_a_agregar,descripcion_horas_trabajadas=descripcion_horas, fecha=fecha, actividad=str(h.actividad), estado=estadoP)
                            h.hu_descripcion.add(Horas_Trabajadas.objects.get(id=hd.id))
                            hd.save()
                            
                            usuarioe = MyUser.objects.get(id=usuario_id).username
                            proyectoe = Proyecto.objects.get(id=proyectoid).nombre
                            evento_e="Estimado usuario "+ usuarioe+ ", Se ha agregado '"+str(request.POST['horas_agregar'])+"' horas a la '"+str(h.descripcion)+"' con una descripcion '"+str(request.POST['descripcion_horas'])+"' estando en la actividad '"+ str(h.actividad)+ "' con el estado '"+str(h.estado_en_actividad)+"' con fecha y hora: "+str(timezone.now().strftime("%Y/%m/%d %H:%M:%S"))+" en el proyecto "+proyectoe
                            email_e=str(MyUser.objects.get(id=usuario_id).email)
                            send_email(str(email_e), 'Notificacion', evento_e)
                            
                            return render(request,'modificarHU.html', {'HU':h, 'proyectoid':proyectoid,'usuarioid':usuario_id, 'rolid':rolid,'is_Scrum':2})
                    return('Las horas se han cargado exitosamente')
            else:
                return HttpResponse('Las Horas cargadas ya superan las 8 Horas diarias que deben cargarse por dia. Ya ha cargado '+str(acumulador-int(prueba))+' horas en este dia') 
                

class FormularioSprintProyecto(forms.ModelForm):
    """
    Clase que obtiene el formulario para la creacion, visualizacion y modificacion
    de sprints del proyecto desde la vista del Scrum.
    """
    class Meta:
        model= Sprint
        fields=['descripcion','fecha_inicio','duracion','estado','hu','flujo','equipo']



    
def visualizarSprintProyectoView(request,usuario_id, proyectoid, rolid, Sprint_id_rec):
    """
    Vista que utiliza el formulario SprintProyecto para desplegar los datos almacenados
    en el Sprint que se quiere visualizar.
        :param func: request
        :param args: usuario_id, proyectoid, rolid, Sprint_id_rec
        :returns: visualizarSprint.html
    
    """
    Sprint_disponible= Sprint.objects.get(id=Sprint_id_rec)
    formulario =  FormularioSprintProyecto(initial={
                                                     'descripcion': Sprint_disponible.descripcion,
                                                     'fecha_inicio': Sprint_disponible.fecha_inicio,
                                                     'duracion': Sprint_disponible.duracion,
                                                     'estado': Sprint_disponible.estado,
                                                     })      
    return render_to_response('visualizarSprint.html',{'formulario':formulario, 'Sprint':Sprint_disponible, 'proyectoid':proyectoid,'usuarioid':usuario_id, 'rolid':rolid},
                                  context_instance=RequestContext(request))
    
    
    
    
    
def modificarSprint(request, usuario_id, proyectoid, rolid, Sprint_id_rec):
    """
    Vista que utiliza el formulario SprintProyecto para desplegar los datos editables
    del Sprint que se quiere modificar.
    La lista de HU asignables se dividen en dos sublistas: las ya asignadas a algun sprint y las que aun
    no han sido asignadas.
        :param func: request
        :param args: usuario_id, proyectoid, rolid, Sprint_id_rec
        :returns: 'modificarSprint.html'
        :rtype: descripcion, estado, fecha_inicio, duracion, hu, flujo

    """
    estados=['ACT','CAN']
    proyectox=Proyecto.objects.get(id=proyectoid)
    s=Sprint.objects.get(id=Sprint_id_rec)
    if request.method == 'POST':
        guardar=0
        for g in request.POST.getlist('Submit'):
            if g == 'Guardar':
                guardar=1
        if guardar == 1:
            descripcion=request.POST['descripcion']
            estado=request.POST['estado']
            fecha_inicio=request.POST['fecha_inicio']
            duracion=request.POST['duracion']
            hu=request.POST.getlist('hu')
            flujo=request.POST.getlist('flujo')
            usuarios=request.POST.getlist('equipo')
            s.descripcion=descripcion
            s.estado=estado
            s.fecha_inicio=fecha_inicio
            s.duracion=duracion
            for h in hu:
                s.hu.add(HU.objects.get(id=h))
            for h in flujo:
                s.flujo.add(Flujo.objects.get(id=h))
            for h in usuarios:
                s.equipo.add(MyUser.objects.get(id=h))
            s.save() #Guardamos el modelo de manera Editada

            usuarioe = MyUser.objects.get(id=usuario_id).username
            proyectoe = Proyecto.objects.get(id=proyectoid).nombre
            evento_e="Estimado usuario "+ usuarioe+ ", El Sprint '"+descripcion+"' con estado '"+estado+"' con una fecha de inicio '"+str(fecha_inicio)+"' ,duracion '"+duracion+"' ,hu '"+str([t.descripcion for t in s.hu.all()])+"' y flujo '"+str([t.nombre for t in s.flujo.all()])+"' ha sido modificado exitosamente en la fecha y hora: "+str(timezone.now().strftime("%Y/%m/%d %H:%M:%S"))+" en el proyecto "+proyectoe
            email_e=str(MyUser.objects.get(id=usuario_id).email)
            send_email(str(email_e), 'Notificacion', evento_e)


            return HttpResponse('El Sprint ha sido modificado exitosamente')

        else:
            if request.POST['boton'] == 'Calcular':
                sum=0
                for h in s.hu.all():
                    sum=sum+h.duracion
                hus_seleccionadas=[]
                HUs_no_seleccionadas=[]
                for h in HU.objects.filter(estado="ACT").filter(proyecto=proyectox).filter(valido=True):
                    if h not in s.hu.all():
                        if not h.sprint():
                            HUs_no_seleccionadas.append(h)
                        else:
                            if h.sprint().estado == 'FIN' and h.estado_en_actividad != 'APR':
                                HUs_no_seleccionadas.append(h)
                    
                flujos_seleccionados=[]
                flujos_no_seleccionados=[]
                for f in Flujo.objects.all():
                    if f not in s.flujo.all():
                        flujos_no_seleccionados.append(f)
                        
                for h in request.POST.getlist('hu'):
                    hus_seleccionadas.append(HU.objects.get(id=h))
                    sum=sum+HU.objects.get(id=h).duracion
                    if HU.objects.get(id=h) in HUs_no_seleccionadas:
                        HUs_no_seleccionadas.remove(HU.objects.get(id=h))
                
                for f in request.POST.getlist('flujo'):
                    flujos_seleccionados.append(Flujo.objects.get(id=f))
                    if Flujo.objects.get(id=f) in flujos_no_seleccionados:
                        flujos_no_seleccionados.remove(Flujo.objects.get(id=f))
                
                equipo_seleccionado=[]
                equipo_no_seleccionado=[]
                horas=len(s.equipo.all())*8
                asignaciones= AsignarRolProyecto.objects.filter(proyecto=proyectox)#obtuve todas las asignaciones para este proyecto
                for a in asignaciones:
                    rola = a.rol
                    if rola.tiene_permiso('Agregar horas trabajadas'):
                        equipo_no_seleccionado.append(a.usuario)
                for e in s.equipo.all():
                    if e in equipo_no_seleccionado:
                        equipo_no_seleccionado.remove(e)
                        
                for u in request.POST.getlist('equipo'):
                    horas=horas+8
                    equipo_seleccionado.append(MyUser.objects.get(id=u))
                    equipo_no_seleccionado.remove(MyUser.objects.get(id=u))
                fecha = str(s.fecha_inicio)
                ctx = {'estimacion':math.ceil(sum/horas),'equipo':equipo_no_seleccionado,'equipo_sel':equipo_seleccionado,'flujos':flujos_no_seleccionados,'flujos_sel':flujos_seleccionados,'estados':estados, 'fecha':fecha[0:10],'lista_HU_sin_asignar':HUs_no_seleccionadas,'HUs_sel':hus_seleccionadas,'Sprint':s, 'proyectoid':proyectoid,'usuarioid':usuario_id, 'rolid':rolid}
                return render_to_response('modificarSprint.html', ctx ,context_instance=RequestContext(request))

    else:    
        
        proyectox=Proyecto.objects.get(id=proyectoid)
        HUs = HU.objects.filter(proyecto=proyectox).filter(valido=True)
        flujos=Flujo.objects.all()
        users=[]
        asignaciones= AsignarRolProyecto.objects.filter(proyecto=proyectox)#obtuve todas las asignaciones para este proyecto
        for a in asignaciones:
            rola = a.rol
            if rola.tiene_permiso('Agregar horas trabajadas'):
                users.append(a.usuario)
        HUs_pendientes=[]
        for x in Sprint.objects.filter(proyecto=proyectox):
            if x.estado != 'FIN':
                for h in x.hu.all():
                    HUs=HUs.exclude(id=h.id)
            else:
                for h in x.hu.all():
                    if h.estado_en_actividad != 'APR' and h.sprint() == x:
                        HUs_pendientes.append(h)
                        HUs=HUs.exclude(id=h.id)
                    else:
                        HUs=HUs.exclude(id=h.id)
                
        lista_restante=[]
        for permitido in HUs:
            x=0
            for perm_hu in s.hu.all():
                if permitido.id==perm_hu.id:
                    x=1
            if x==0:
                lista_restante.append(permitido)
        for h in s.hu.all():
            for hp in HUs_pendientes:
                if h == hp:
                    HUs_pendientes.remove(h)
                    
        fecha = str(s.fecha_inicio)
        
        ctx = {'estimacion':s.duracion,'equipo':users,'HUs_pendientes':HUs_pendientes,'flujos':flujos,'estados':estados, 'fecha':fecha[0:10],'HUs':HUs,'lista_HU_sin_asignar':lista_restante,'Sprint':s, 'proyectoid':proyectoid,'usuarioid':usuario_id, 'rolid':rolid}
        return render_to_response('modificarSprint.html', ctx ,context_instance=RequestContext(request))
    




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
    adjuntos=archivoadjunto.objects.filter(hU=HU_disponible)
    formulario =  FormularioHU(initial={
                                                     'descripcion': HU_disponible.descripcion,
                                                     'valor_negocio': HU_disponible.valor_negocio,
                                                     })      
    return render_to_response('visualizarHU.html',{'formulario':formulario,'usuario_asignado':usuario_asignado,'HU':HU_disponible, 'proyectoid':proyectoid,'usuarioid':usuario_id, 'rolid':rolid,'adjuntos':adjuntos,'is_Scrum':is_Scrum, 'sprint':sprint_al_que_pertenece, 'flujo':flujo_al_que_pertenece, 'kanban':kanban},
                                  context_instance=RequestContext(request))

    
    
    

#-------------------------------------------------------------------------------------------------------    
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
            ctx = {'valores':VALORES10_CHOICES,'form':form, 'HU':h, 'proyectoid':proyectoid,'usuarioid':usuario_id, 'rolid':rolid,'is_Scrum':is_Scrum}
            return render_to_response('modificarHU.html', ctx ,context_instance=RequestContext(request))
    else:
        return render(request,'modificarHU.html', {'estados':estados, 'valores':VALORES10_CHOICES,'HU':h, 'proyectoid':proyectoid,'usuarioid':usuario_id, 'rolid':rolid,'is_Scrum':is_Scrum})

    
    
    
def crearSprint(request,usuario_id,proyectoid,rolid):
    """
    Vista que realiza la creacion de flujos de proyecto desde la vista del Scrum.
        :param func: request
        :param args: usuario_id,proyectoid,rolid
        :returns: crearSprint.html
    """
    proyectox = Proyecto.objects.get(id=proyectoid)
    HUs = HU.objects.filter(proyecto=proyectox).filter(valido=True)
    flujos=Flujo.objects.all()#le mando todos los flujos para que elija los que quiere
    flujos_pen=[]
    HUs_pendientes=[]
    for x in Sprint.objects.filter(proyecto=proyectox):#se podria chequear solo los sprint del proyecto para hacer menos trabajo!
        if x.estado == 'FIN':
            for h in x.hu.all():
                if h.estado_en_actividad != 'APR':
                    HUs_pendientes.append(h)
                    HUs=HUs.exclude(id=h.id)
                    flujos_pen.append(h.flujo())
                else:
                    HUs=HUs.exclude(id=h.id)
    for x in Sprint.objects.filter(proyecto=proyectox):#este super for es para analizae el contenido de los sprint que no hayan terminado 
        if x.estado != 'FIN' and x.estado != 'CAN':#se busca sacar los hu que se pueden continuar todavia que esteen entre los pendientes
            for h in x.hu.all():
                HUs=HUs.exclude(id=h.id)
                for hp in HUs_pendientes:
                    if h == hp:
                        HUs_pendientes.remove(h)  
                for f in flujos_pen:#tambien se busca sacar los flujos que pueden continuar todavia que esteen en entre pendientes de hus pen.
                    if f == h.flujo():
                        flujos_pen.remove(h.flujo())
    flujos_pen=set(flujos_pen)
    for f in flujos_pen:
        for flu in flujos:
            if flu == f:
                flujos=flujos.exclude(id=f.id)
    HUs=sorted(HUs,key=lambda x: x.prioridad, reverse=True)
    users=[]
    asignaciones= AsignarRolProyecto.objects.filter(proyecto=proyectox)#obtuve todas las asignaciones para este proyecto
    for a in asignaciones:
        
        rola = a.rol
        if rola.tiene_permiso('Agregar horas trabajadas'):
            users.append(a.usuario)
        #users.append(a.usuario) #pise como comentario lo de arriba temporalmente
    
    
    users_pen=[]
    for h in HUs_pendientes:
        users_pen.append(h.saber_usuario())
    users_pen=set(users_pen)
    for u in users_pen:
        for up in users:
            if u == up:
                users.remove(u)
    fecha_inicio_sugerida=str(datetime.now())[0:10]
    for s in Sprint.objects.filter(proyecto=proyectox).filter(estado='CON'):
        fecha_inicio_sugerida=str(s.fecha_inicio.date() + timedelta(days=math.ceil(s.duracion)))[0:10]
    if request.method == 'GET':
        return render(request, 'crearSprint.html',{'equipo_pen':users_pen,'equipo':users,'flujos_pen':flujos_pen,'HUs_pendientes':HUs_pendientes,'HUs_no_seleccionadas':HUs,'flujos':flujos,'HUs':HUs,'fecha_ahora':fecha_inicio_sugerida,'usuarioid':usuario_id,'proyectoid':proyectoid,'rolid':rolid})



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
    
    
    
    
    
def delegarHU(request,usuario_id,proyectoid,rolid,hu_id,reasignar):
    """
    Delega o asigna una HU a un usuario miembro del proyecto, y en caso de ser necesario, reasignar la HU
    a otro usuario evitando duplicaciones en la Base de Datos
        :param func: request
        :param args: 
        :returns: asignaHU.html
        :rtype: usuarios
    """
    proyectox=Proyecto.objects.get(id=proyectoid)
    hu=HU.objects.get(id=hu_id)
    if request.method=='POST' :
        if reasignar == '0':
            try:
                delegacionx= AsignaHU_Usuario.objects.create(usuario=MyUser.objects.get(id=request.POST['usuario']),hu=hu)
                delegacionx.save()

                proyectoe = Proyecto.objects.get(id=proyectoid).nombre
                evento_e="Estimado usuario,Se ha asignado una HU '"+hu.descripcion+"' al usuario '"+str(delegacionx.usuario)+"' en la fecha y hora: "+str(timezone.now().strftime("%Y/%m/%d %H:%M:%S"))+" en el proyecto "+proyectoe
                email_e=str(MyUser.objects.get(id=usuario_id).email)
                send_email(str(email_e), 'Notificacion', evento_e)

                return HttpResponse('La asignacion se realizo correctamente')
            except ObjectDoesNotExist:
                return HttpResponseRedirect('/crearFlujo/') #redirijir a rol flujo para scrum despues
        else:
            for d in AsignaHU_Usuario.objects.all():
                if d.hu == hu:
                    d.usuario=MyUser.objects.get(id=request.POST['usuario'])
                    d.save()

                    proyectoe = Proyecto.objects.get(id=proyectoid).nombre
                    evento_e="Estimado usuario,Se ha asignado una HU '"+hu.descripcion+"' al usuario '"+str(d.usuario)+"' en la fecha y hora:"+str(timezone.now().strftime("%Y/%m/%d %H:%M:%S"))+" en el proyecto "+proyectoe
                    email_e=str(MyUser.objects.get(id=usuario_id).email)
                    send_email(str(email_e), 'Notificacion', evento_e)

                    return HttpResponse('Se ha reasignado la HU exitosamente')
    else:
        users=hu.sprint().equipo.all()
        usuario_asignado=[]
        if reasignar == '1':
            for d in AsignaHU_Usuario.objects.all():
                if d.hu == hu:
                    usuario_asignado = d.usuario
        
        return render(request,'asignaHU.html',{'sprint':hu.sprint(),'usuario_asignado':usuario_asignado, 'proyecto':proyectox,'usuarios':users,'proyectoid':proyectoid,'usuarioid':usuario_id, 'rolid':rolid})
    
def validarHU(request, usuario_id, proyectoid, rolid, HU_id_rec,is_Scrum):
    """
    Controla la validacion de una HU creada por el product owner
        :param func: request
        :param args: usuario_id, proyectoid, rolid, HU_id_rec,is_Scrum
        :returns: validarHU.html
    """
    hu_x=HU.objects.get(id=HU_id_rec)
    if request.method == 'GET':       
        return render(request,'validarHU.html',{'hu':HU_id_rec, 'HU':hu_x.valido, 'proyectoid':proyectoid,'usuarioid':usuario_id, 'rolid':rolid,'is_Scrum':is_Scrum})
    else:
        if hu_x.valido == False:
            hu_x.valido=True
            hu_x.save()
            return HttpResponse('Se ha validado exitosamente') 
        else:
            hu_x.valido=False
            hu_x.save()
            return HttpResponse('Se ha invalidado exitosamente')
  
def visualizarBacklog(request, usuario_id, proyectoid, rolid):
    """
    Vista disponible para el Scrum y el Product Owner.
    Esta vista contiene la lista de HU pendientes pero ACTIVAS y VALIDADAS ordenadas segun su prioridad
    en orden descendente para la correspondiente asignacion que realizara el Scrum Master.
    A medida que las HU se realizan, estas desapareceran del Product Backlog.
        :param func: request
        :param args: usuario_id, proyectoid, rolid
        :returns: visualizarBacklog.html
    """
    proyectox=Proyecto.objects.get(id=proyectoid)
    huss=HU.objects.all().filter(proyecto=proyectox).filter(estado='ACT').filter(valido=True).filter(sprint__hu__isnull=True)
    hu=sorted(huss,key=lambda x: x.prioridad, reverse=True)
    HUs_pendientes=[]
    for x in Sprint.objects.filter(proyecto=proyectox):
        if x.estado == 'FIN':
            for h in x.hu.all():
                if h.estado_en_actividad != 'APR':
                    HUs_pendientes.append(h)
    for x in Sprint.objects.filter(proyecto=proyectox):
        if x.estado != 'FIN':
            for h in x.hu.all():
                for hp in HUs_pendientes:
                    if h == hp:
                        HUs_pendientes.remove(h)  
    return render(request,'visualizarBacklog.html',{'HUs_pendientes':HUs_pendientes,'huss':hu, 'proyectoid':proyectoid,'usuarioid':usuario_id, 'rolid':rolid})

def reactivar(request, usuario_id, proyectoid, rolid, tipo, id_tipo):
    """
    Vista que permite reactivar un flujo, HU o Sprint cancelado por el usuario,
    para su correspondiente uso o modificacion, ya que los objetos cancelados
    solo estan disponibles para su visualizacion, no para su asignacion o modificacion.
    Recibe un tipo en la url que le permite distinguir de que tipo de objeto se trata.
        :param func: request
        :param args: usuario_id, proyectoid, rolid, tipo, id_tipo
        :returns: '/scrum/'+usuario_id+'/'+proyectoid+'/'+rolid+'/'
    """

    if tipo == '1': #se trata de un flujo
        f=Flujo.objects.get(id=id_tipo)
        f.estado='ACT'
        f.save()

            
    if tipo == '2': #se trata de una HU
        h=HU.objects.get(id=id_tipo)
        h.estado='ACT'
        h.save()


    if tipo == '3': #se trata de un sprint
        s=Sprint.objects.get(id=id_tipo)
        s.estado='ACT'
        s.save()


    if tipo == '4': #se trata de un rol
        s=Rol.objects.get(id=id_tipo)
        s.estado='ACT'
        s.save()

    
    if tipo == '5': #se trata de un proyecto
        s=Proyecto.objects.get(id=id_tipo)
        s.estado='ACT'
        s.save()

        return HttpResponseRedirect('/hola/')
    return HttpResponseRedirect('/scrum/'+usuario_id+'/'+proyectoid+'/'+rolid+'/')


def adminAdjunto(request, usuario_id, proyectoid, rolid, HU_id_rec):
    """
    Vista que gestiona el guardado de archivos adjuntos a HUs    
        :param func: request
        :param args: usuario_id, proyectoid, rolid, HU_id_rec
        :returns: adjuntos.html
    """
    if request.method=='GET':
        hux=HU.objects.get(id=HU_id_rec)
        adjuntos=[]
        try: 
            adjuntos=archivoadjunto.objects.filter(hU=hux).filter(estado='ACT')
        except ObjectDoesNotExist:
            adjuntos = []
        return render(request,'adjuntos.html',{'HU':hux,'adjuntos':adjuntos,'proyectoid':proyectoid,'usuarioid':usuario_id, 'rolid':rolid})
    else:
        archivox = request.FILES['archivo']
        file=bytearray()
        for d in archivox.chunks():
            file.extend(d)
        n=0
        split=archivox.name.split('.')
        cambiar=split[0]
        while archivoadjunto.objects.filter(nombre=cambiar).filter(estado='ACT'):
            n=n+1
            split=archivox.name.split('.')
            cambiar=split[0]+"("+str(n)+")"
            
        filex=archivoadjunto.objects.create(nombre=cambiar,content=archivox.content_type,tamanho=archivox.size,archivo=file,hU_id=HU_id_rec,estado='ACT')
        filex.save()

        #archivox.save()
        return HttpResponseRedirect('/adminAdjunto/'+usuario_id+'/'+proyectoid+'/'+rolid+'/'+HU_id_rec+'/')
    
def descargar(request, usuario_id, proyectoid, rolid, HU_id_rec,archivo_id):
    """
     Descarga el archivo adjunto seleccionado 
        :param func: request
        :param args: usuario_id, proyectoid, rolid, HU_id_rec,archivo_id
        :returns: response = HttpResponse(content_type=archivox.content)
    """
    archivox=archivoadjunto.objects.get(id=archivo_id)
    response = HttpResponse(content_type=archivox.content)
    response['Content-Disposition'] = 'attachment; filename="%s"' % archivox.nombre
    buffer = BytesIO(archivox.archivo)
    file = buffer.getvalue()
    buffer.close()
    response.write(file)
    return response

def eliminar_adjunto(request, usuario_id, proyectoid, rolid, HU_id_rec,archivo_id):
    """
    Elminar archivo adjunto desde el admin
        :param func: request
        :param args: usuario_id, proyectoid, rolid, HU_id_rec,archivo_id
        :returns: '/adminAdjunto/'+usuario_id+'/'+proyectoid+'/'+rolid+'/'+HU_id_rec+'/'
    """
    archivox=archivoadjunto.objects.get(id=archivo_id)
    archivox.estado='CAN'
    archivox.save()
    return HttpResponseRedirect('/adminAdjunto/'+usuario_id+'/'+proyectoid+'/'+rolid+'/'+HU_id_rec+'/')



def visualizarSprintBacklog(request, usuario_id, proyectoid, rolid):
    """
    El sprint backlog es una lista de las tareas identificadas por el equipo de Scrum
    Los equipos estiman el numero de horas para cada tarea que se corresponde a alguien del equipo para completar.
        :param func: request
        :param args: usuario_id, proyectoid, rolid
        :returns: visualizarSprintBacklog.html
    """
    class descripcionHU:
        """Obtiene toda la informacion de una hu"""
        def __init__(self,dias, duracionhu, pendiente, p):
            self.dias=dias
            self.duracionhu=duracionhu
            self.pendiente=pendiente
            self.p=p
    
    class usu_estado:
        """Guarda el usuario y el estado en actividad de una HU dentro de un Sprint"""
        def __init__(self,usuario, estado):
            self.usuario=usuario
            self.estado=estado
    class sprint_acu_fecha:
        """Guarda el fecha fin e Inicio y el acumulado de todas las HU dentro de un Sprint"""
        def __init__(self,fecha_f, fecha_i):
            self.fecha_f=fecha_f
            self.fecha_i=fecha_i
    class acu_color:
        """Guarda el acumulado y el color"""
        def __init__(self, acum, color):
            self.acum=acum
            self.color=color        
            
   

    dias=0
    hux=HU.objects.filter(proyecto=Proyecto.objects.get(id=proyectoid))
    sprint=Sprint.objects.filter(proyecto=Proyecto.objects.get(id=proyectoid))
    s=sorted(sprint,key=lambda x: x.estado, reverse=False)
    
    #obtengo las fechas
    lista_fecha=[]
    for sp in sprint:
        if sp.estado == 'CON':
            dias=sp.duracion-1
            contador=-1
            while dias > contador:
                lista_fecha.append(((sp.fecha_inicio)+timedelta(days=contador)).strftime('%Y-%m-%d'))
                contador += 1
    #obtengo las dias
    lista_dias=[]
    for sp in sprint:
        if sp.estado == 'CON':
            dias=sp.duracion
            contador=1
            while dias >= contador:
                lista_dias.append(contador)
                contador += 1
                
    hu_x=sorted(hux,key=lambda x: x.prioridad, reverse=True)   

    longitud_para_tabla={}
    for i in sprint:
        longitud_para_tabla[i]=len(i.hu.all())+1
        
    usuario_hu={}
    for h in hu_x:
        for d in AsignaHU_Usuario.objects.all():
            if h.id == d.hu.id:
                usuario=d.usuario
                estado=h.estado_en_actividad
                usuario_hu[h]=usu_estado(usuario, estado)#hu-usuario-estado
    
    longitud_equipo=[]
    usu=""
    for i, u in usuario_hu.items():
            if usu=="":
                usu=u.usuario
                #longitud_equipo[i]=usu
                longitud_equipo.append(usu)
            elif usu != u.usuario:
                usu=u.usuario
                #longitud_equipo[i]=usu
                longitud_equipo.append(usu)#los usuarios
        
    fecha_fin_sprint=0
    fecha_inicio=0
    lista_sprint={}
    for hu in hu_x:
        for sp in sprint:
                    for h in sp.hu.all():
                        if h == hu:
                            if sp.estado == 'CON':    
                                fecha_fin_sprint=(sp.fecha_inicio+timedelta(days=(sp.duracion-1))).strftime('%Y-%m-%d')
                                fecha_inicio=(sp.fecha_inicio+timedelta(days=0)).strftime('%Y-%m-%d')
        lista_sprint[sp]=sprint_acu_fecha(fecha_fin_sprint,fecha_inicio )
    #La duracion en horas de un Sprint
    sprint_acu_fecha=0
    lista_sprint_acu_fecha={}
    for sp in sprint:
        for hu in hu_x:
                for h in sp.hu.all():
                    if h == hu:
                        sprint_acu_fecha=sprint_acu_fecha+hu.duracion     
        lista_sprint_acu_fecha[sp]=sprint_acu_fecha
        
    lista_hu_horas={}
    descripcion_hu={}
    lista_horas=[]
    cont2=0        
    fecha_x=[]
    pendiente=0
    dura=0
    aux=1
    hasta=1
    desde=0
    nuevo_usu=""
    #for hu in hu_x:
    for hu, u in usuario_hu.items():
        lista_horas=[]
        acumulador=0
        
        hasta+=hu.dias_hu(hu.duracion)#cantidad de dias
        aux=1
        usu=u.usuario
        
        for fecha_x in lista_fecha:
            cont2=0
            for h in hu.hu_descripcion.all():
                x=str((h.fecha+timedelta(days=-1)).strftime('%Y-%m-%d'))
                if str(fecha_x) == x[:10]:
                    cont2=cont2+h.horas_trabajadas
                    
            if nuevo_usu != usu:
                nuevo_usu=usu
                desde=1
                hasta=hu.dias_hu(hu.duracion)#cantidad de dias
                
            if aux>=desde and aux<=hasta:
                    lista_horas.append(acu_color(cont2, 1))
            else:
                lista_horas.append(acu_color(cont2, 0))
            aux+=1
                        
            acumulador=acumulador+cont2#el acumulado optiene el total de horas que realizo en varios dias de trabajo
            
            lista_hu_horas[hu]=lista_horas
            
            pendiente=hu.duracion
            pendiente=pendiente-acumulador#Lo que le resta de la duracion para terminar la HU

        dias=hu.dias_hu(hu.duracion) #retorna la cantidad de dias de la HU
        desde=hasta+1
        dura=hu.duracion#cuantas horas dura
        if pendiente==0:
            p=1
        else:
            p=0                
        descripcion_hu[hu]=descripcionHU(dias, dura, pendiente, p)
            
    return render(request,'visualizarSprintBacklog.html',{'len':longitud_para_tabla,'sprint':s, 'proyectoid':proyectoid,'usuarioid':usuario_id, 'rolid':rolid, 'HUx':hu_x, 'lista':lista_hu_horas, 'usuario_hu':usuario_hu, 'descripcionHU':descripcion_hu, 'fecha_fin_s':fecha_fin_sprint, 'lista_sprint':lista_sprint, 'fechas':lista_fecha, 'dura_sprint':lista_sprint_acu_fecha, 'dias':lista_dias, 'hu_x':hu_x, 'lep':usuario_hu})

def asignarHU_Usuario_FLujo(request,usuario_id,proyectoid,rolid,sprintid):
    """ 
    Vista de asignacion de una HU a un usuario y en un flujo
        :param func: request
        :param args: usuario_id,proyectoid,rolid,sprintid
        :returns: asignarHU_Usuario_Flujo.html 
    """
    proyectox=Proyecto.objects.get(id=proyectoid)
    sprintx=Sprint.objects.get(id=sprintid)
    hus=HU.objects.filter(proyecto=proyectox,estado='ACT',valido=True).filter(sprint=sprintx)
    hu_en_flujo={}
    
    fin=1
    for h in sprintx.hu.all():
        if h.estado_en_actividad != 'APR':
            fin=0
    if fin == 1:
        sprintx.estado='FIN'
        sprintx.save()
        
    for f in Flujo.objects.filter(sprint=Sprint.objects.get(id=sprintid)):
        for a in AsignaHU_flujo.objects.all():
            if f == a.flujo_al_que_pertenece:
                for h in a.lista_de_HU.all():
                    if h.proyecto == proyectox and h.sprint() == sprintx:
                        hu_en_flujo[f]=a.lista_de_HU.all()
                        break
    HU_no_asignada=[]
    HU_asignada={}
    for HUa in hus:
            x=0
            for d in AsignaHU_Usuario.objects.all():
                if d.hu == HUa:
                    x=1
                    HU_asignada[HUa]=d.usuario
            if x == 0:
                HU_no_asignada.append(HUa)
    flujos_aprobados=[]
    for f in Flujo.objects.filter(sprint=Sprint.objects.get(id=sprintid)):
        x=0
        if hu_en_flujo.has_key(f):
            for h in hu_en_flujo[f]:
                if h.estado_en_actividad != 'APR':
                    x=1
            if x == 0:
                flujos_aprobados.append(f)
    return render(request,"asignarHU_Usuario_Flujo.html",{'flujos_aprobados':flujos_aprobados,'hu_en_flujo':hu_en_flujo,'flujos':Flujo.objects.filter(sprint=Sprint.objects.get(id=sprintid)),'HU_no_asignada':HU_no_asignada,'HU_asignada':HU_asignada,'hus':hus,'sprint':sprintx,'proyecto':proyectox,'proyectoid':proyectoid,'usuarioid':usuario_id, 'rolid':rolid})

def asignarHU_a_FLujo(request,usuario_id,proyectoid,rolid,sprintid,flujo_id):
    """
    Vista donde se asignan las HU a un flujo dentro del spring y a un usuario del proyecto
        :param func: request
        :param args: usuario_id,proyectoid,rolid,sprintid,flujo_id
        :returns: asignarHUFlujo.html
    """
    sprintx=Sprint.objects.get(id=sprintid)
    proyectox=Proyecto.objects.get(id=proyectoid)
    flujo=Flujo.objects.get(id=flujo_id)
    jsonDec = json.decoder.JSONDecoder()
    orden=jsonDec.decode(flujo.orden_actividades)
    hus=HU.objects.filter(proyecto=proyectox,estado='ACT',valido=True).filter(sprint=sprintx)
    for f in Flujo.objects.filter(sprint=Sprint.objects.get(id=sprintid)):
        for a in AsignaHU_flujo.objects.all():
            if a.flujo_al_que_pertenece == f:
                for h in a.lista_de_HU.all():
                    if h.proyecto == proyectox:
                        hus=hus.exclude(id=h.id)
    if request.method == 'POST':
        for a in request.POST.getlist('hu'):
            h=HU.objects.get(id=a)
            h.actividad=Actividades.objects.get(id=orden[0])
            h.save()
            asig=AsignaHU_flujo.objects.filter(flujo_al_que_pertenece=flujo)
            existe_flujo_en_proyecto=0
            if asig:
                for f in asig:
                    existe_flujo_en_proyecto=0
                    for h in f.lista_de_HU.all():
                        if h.proyecto == proyectox and h.estado_en_actividad != 'APR':
                            existe_flujo_en_proyecto=1
                    if existe_flujo_en_proyecto == 1:
                        f.lista_de_HU.add(HU.objects.get(id=a))
                        f.save()
                        break
            else:
                asignar=AsignaHU_flujo.objects.create(flujo_al_que_pertenece=Flujo.objects.get(id=flujo_id))
                asignar.lista_de_HU.add(HU.objects.get(id=a))
                asignar.save()
                existe_flujo_en_proyecto=1
            if existe_flujo_en_proyecto == 0:
                asignar=AsignaHU_flujo.objects.create(flujo_al_que_pertenece=Flujo.objects.get(id=flujo_id))
                asignar.lista_de_HU.add(HU.objects.get(id=a))
                asignar.save() 

        return HttpResponseRedirect('/asignarHUFlujo/'+str(usuario_id)+'/'+str(proyectoid)+'/'+str(rolid)+'/'+str(sprintid))
    else:
        return render(request,"asignarHUFlujo.html",{'flujo':flujo,'hus':hus,'proyectoid':proyectoid,'usuarioid':usuario_id, 'rolid':rolid,'sprint':sprintx,'flujo_id':flujo_id})

def verKanban(request,usuario_id,proyectoid,rolid,sprintid):
    """
    Vista que permite acceder al template de visualizacion de un flujo graficamente en el kanban
        :param func: request
        :param args: usuario_id,proyectoid,rolid,sprintid
        :returns: verKanban.html
    """
    sprintx=Sprint.objects.get(id=sprintid)
    flujos_hu={}
    flujos_actividades={}
    kanban=1
    proyectox=Proyecto.objects.get(id=proyectoid)
    lista_hu=[]
    for f in sprintx.flujo.all():
        for a in AsignaHU_flujo.objects.filter(flujo_al_que_pertenece=f):
            lista_hu=[]
            x=0
            for h in a.lista_de_HU.all():
                if h.sprint() == sprintx and h.proyecto == proyectox:
                    x=1
                    lista_hu.append(h)
            if x == 1:
                flujos_hu[f]=lista_hu
                break
    for f in sprintx.flujo.all():
        jsonDec = json.decoder.JSONDecoder()
        orden=jsonDec.decode(f.orden_actividades)
        actividades=[]
        for o in orden:
            actividades.append(Actividades.objects.get(id=o))
        flujos_actividades[f]=actividades
    flujos_aprobados=[]
    for f in sprintx.flujo.all():
        x=0
        if flujos_hu.has_key(f):
            for h in flujos_hu[f]:
                if h.estado_en_actividad != 'APR':
                    x=1
            if x == 0:
                flujos_aprobados.append(f)
                   
    return render(request,"verKanban.html",{'flujos_aprobados':flujos_aprobados,'sprint':sprintx, 'flujos_hu':flujos_hu,'flujos_actividades':flujos_actividades,'proyectoid':proyectoid,'usuarioid':usuario_id, 'rolid':rolid, 'kanban':kanban})

def aprobarHU(request, usuario_id, proyectoid, rolid, sprintid, HU_id_rec):
    """
    Vista que permite al Scrum aprobar una HU o volver a un estado anterior del flujo.
        :param func: request
        :param args: usuario_id, proyectoid, rolid, sprintid, HU_id_rec
        :returns: aprobar_finalizacion_Flujo.html
        :rtype: actividad, estado, duracion, descripcion
    """
    HU_tratada=HU.objects.get(id=HU_id_rec)
    usuario_asignado=HU_tratada.saber_usuario()
    if request.method == 'GET':
        f=HU_tratada.flujo()
        estados=['PEN','PRO']
        jsonDec = json.decoder.JSONDecoder()
        orden=jsonDec.decode(f.orden_actividades)
        actividades=[]
        for o in orden:
            actividades.append(Actividades.objects.get(id=o))
        return render(request,"aprobar_finalizacion_Flujo.html",{'usuario_asignado':usuario_asignado,'HU':HU_tratada,'flujo':f,'estados':estados,'actividades':actividades,'sprintid':sprintid,'proyectoid':proyectoid,'usuarioid':usuario_id, 'rolid':rolid})
    else:
        guardar=0
        for g in request.POST.getlist('_save'):
            if g == 'Aprobar':
                guardar=1
        if guardar == 1:
            HU_tratada.estado_en_actividad='APR'
            HU_tratada.save()
            hd=Horas_Trabajadas.objects.create(horas_trabajadas=0,descripcion_horas_trabajadas='HU aprobada por SCRUM',fecha=datetime.now(), actividad=str(HU_tratada.actividad), estado=str(HU_tratada.estado_en_actividad))
            HU_tratada.Horas_Trabajadas.add(Horas_Trabajadas.objects.get(id=hd.id))
            hd.save()
            return HttpResponseRedirect('/verKanban/'+usuario_id+'/'+proyectoid+'/'+rolid+'/'+sprintid+'/')
        else:
            actividad=Actividades.objects.get(id=request.POST['actividad'])
            estado=request.POST['estado']
            duracion=float(request.POST['duracion'])
            if duracion >= HU_tratada.duracion:
                HU_tratada.actividad=actividad
                HU_tratada.estado_en_actividad=estado
                HU_tratada.duracion=duracion
                HU_tratada.save()
                descripcion=request.POST['descripcion']
                hd=Horas_Trabajadas.objects.create(horas_trabajadas=0,descripcion_horas_trabajadas=descripcion,fecha=datetime.now(), actividad=str(HU_tratada.actividad), estado=str(HU_tratada.estado_en_actividad))
                HU_tratada.Horas_Trabajadas.add(Horas_Trabajadas.objects.get(id=hd.id))
                hd.save()
                return HttpResponseRedirect('/verKanban/'+usuario_id+'/'+proyectoid+'/'+rolid+'/'+sprintid+'/')
            else:
                return HttpResponse('La duracion no puede ser menor a las horas ya acumuladas, que son: '+str(HU_tratada.acumulador_horas))

def reasignarhuFlujo(request,usuario_id, proyectoid,rolid,sprintid,huid,kanban):
    """
    Vista que permita reasignar una hu con tiempo agotado a otro flujo y agregar horas a su duracion prevismente establecida para
    porder continuar desarrollandola el tiempo que sea requerido
    En el template el usuario podra elegir de una lista de flujos, parecido a delegarHU la que prefiera para continuar la hu, ademas tendra un campo para aumentar
    el numero de horas de duracion de la hu, ya que necesitaba mas, la misma empezara en la actividad de orden 1 del flujo nuevo
        :param func: request
        :param args: usuario_id, proyectoid,rolid,sprintid,huid,kanban
        :returns: reasignarhuflujo.html
        :rtype: duracionmas
    """
    #Primero obtener la hu  y el sprint
    hu_now=HU.objects.get(id=huid)
    sprint_now=Sprint.objects.get(id=sprintid)
    #y tambien el proyecto por las dudas
    proyecto_now=Proyecto.objects.get(id=proyectoid)
    #y todos los flujos de este proyecto
    if request.method=='GET' :
    
        
        flujos=sprint_now.flujo.all().exclude(id=hu_now.flujo().id)
        #Necesito mandarle tambien la duracion de la hu, pero eso puede ser accedido desde hu_now
        return render(request,'reasignarhuflujo.html',{'flujo_actual':hu_now.flujo(),'kanban':kanban,'hu':hu_now,'sprint':sprint_now,'proyecto':proyecto_now,'flujos':flujos,'proyectoid':proyectoid,'usuarioid':usuario_id, 'rolid':rolid})
    else:
        """Cuando sea post se tienen que hacer ciertos cambios con los datos"""
        for a in request.POST.getlist('flujos'):
        #uno solo es lo que hay en a
            flujox=Flujo.objects.get(id=a)
            jsonDec = json.decoder.JSONDecoder()
            orden=jsonDec.decode(flujox.orden_actividades)
            hu_now.actividad=Actividades.objects.get(id=orden[0])
            hu_now.estado_en_actividad='PEN'
            hu_now.save()
            
            #remuevo el manytomany de la hu al flujo anterior
            asig=AsignaHU_flujo.objects.filter(flujo_al_que_pertenece=hu_now.flujo())
            if asig:
                for f in asig:
                    for h in f.lista_de_HU.filter(proyecto=proyecto_now):
                        if h == hu_now:
                            f.lista_de_HU.remove(h)
                            f.save()
            
            #agrego el nuevo flujo relacionado a la HU
            asig=AsignaHU_flujo.objects.filter(flujo_al_que_pertenece=flujox)
            if asig:
                for f in asig:
                    f.lista_de_HU.add(hu_now)
                    f.save()
                            
        hu_now.duracion+= float(request.POST['duracionmas'])
        hu_now.save()
        
        return HttpResponse('Se ha cambiado de flujo correctamente a'+hu_now.flujo().nombre)


def anularProyecto(request,usuario_id,proyectoid):
    if request.method=='GET' :
        return render(request,'anularProyecto.html',{'usuarioid':usuario_id,'proyectoid':proyectoid})
    else:
        proyectox=Proyecto.objects.get(id=proyectoid)

        proyectox.fecha_fin=timezone.now()
        proyectox.estado='ANU'
        proyectox.save()
        return HttpResponseRedirect('/hola/')
    
def finalizarProyecto(request,usuario_id,proyectoid,rol_id):
    if request.method=='GET' :
        return render(request,'finalizarProyecto.html',{'usuarioid':usuario_id,'proyectoid':proyectoid,'rolid':rol_id})
    else:
        proyectox=Proyecto.objects.get(id=proyectoid)


        proyectox.estado='FIN'
        proyectox.fecha_fin=timezone.now()
        proyectox.save()
        return HttpResponseRedirect('/hola/')
    
def iniciarProyecto(request,usuario_id,proyectoid,rol_id,sprintid ):
    s=Sprint.objects.get(id=sprintid)
    s.fecha_inicio=datetime.today()
    s.estado = 'CON'
    s.save()
    return HttpResponseRedirect('/scrum/'+usuario_id+'/'+proyectoid+'/'+rol_id+'/')




    
    
    
    
    
    
    
    