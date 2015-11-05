#coding: utf-8
import django
django.setup()
import datetime
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from sis.models import Proyecto, HU, Rol, AsignaHU_flujo, AsignaHU_Usuario, AsignarRolProyecto, MyUser, Actividades, Flujo, Sprint, Horas_Trabajadas



"""Creacion de nuevos permisos para el Scrum y el Product Ownwer"""
content_type = ContentType.objects.get_for_model(HU)
permission1 = Permission.objects.create(codename='Puede agregar horas trabajadas',
                                       name='Agregar horas trabajadas',
                                       content_type=content_type)
permission2 = Permission.objects.create(codename='Puede cambiar HU a nivel Scrum',
                                       name='Can change hu nivel Scrum',
                                       content_type=content_type)

content_type2 = ContentType.objects.get_for_model(Proyecto)
permission3 = Permission.objects.create(codename='Visualizar proyecto',
                                       name='Visualizar proyecto',
                                       content_type=content_type2)
permission4 = Permission.objects.create(codename='Visualizar equipo',
                                       name='Visualizar equipo',
                                       content_type=content_type2)



"""Creacion de roles predefinidos a nivel proyecto Scrum,Owner, etc"""
rol_scrum=Rol.objects.create(nombre_rol='Scrum Master',descripcion='Permisos adquiridos por el ScrumMaster')
rol_owner=Rol.objects.create(nombre_rol='Product Owner',descripcion='Permisos adquiridos por el Product Owner')
rol_equipo=Rol.objects.create(nombre_rol='Equipo',descripcion='Permisos adquiridos por el Equipo')
rol_cliente=Rol.objects.create(nombre_rol='Cliente',descripcion='Permisos adquiridos por el Cliente')



"""Ahora se cargaran permisos a cada uno de esos roles predefinidos"""
"""Carga para el Scrum Master"""

"""Administracion de rol"""
per_add_rol=Permission.objects.get(name='Can add rol')
per_change_rol=Permission.objects.get(name='Can change rol')
per_delete_rol=Permission.objects.get(name='Can delete rol')


"""Administracion de actividades"""
per_add_act=Permission.objects.get(name='Can add actividad')
per_change_act=Permission.objects.get(name='Can change actividad')
per_delete_act=Permission.objects.get(name='Can delete actividad')


"""Administracion de flujo"""
per_add_flujo=Permission.objects.get(name='Can add flujo')
per_change_flujo=Permission.objects.get(name='Can change flujo')
per_delete_flujo=Permission.objects.get(name='Can delete flujo')


"""Modificacion de proyecto"""
per_change_proyecto=Permission.objects.get(name='Can change proyecto')

"""Administracion de Sprint"""
per_add_sprint=Permission.objects.get(name='Can add sprint')
per_change_sprint=Permission.objects.get(name='Can change sprint')
per_delete_sprint=Permission.objects.get(name='Can delete sprint')


"""Administracion de equipo"""
per_add_asigna=Permission.objects.get(name='Can add rol x proyecto')
per_change_asigna=Permission.objects.get(name='Can change rol x proyecto')
per_delete_asigna=Permission.objects.get(name='Can delete rol x proyecto')


"""Administracion de asignacion de HU a usuario"""
per_add_delega=Permission.objects.get(name='Can add asigna h u_ usuario')
per_change_delega=Permission.objects.get(name='Can change asigna h u_ usuario')
per_delete_delega=Permission.objects.get(name='Can delete asigna h u_ usuario')

"""Administracion asigna HU a flujo"""
per_add_asignahu=Permission.objects.get(name='Can add asigna h u_flujo')
per_change_asignahu=Permission.objects.get(name='Can change asigna h u_flujo')
per_delete_asignahu=Permission.objects.get(name='Can delete asigna h u_flujo')

"""Modificacion de hu nivel scrum"""
per_change_hu_scrum=Permission.objects.get(name='Can change hu nivel Scrum')


"""MOMENTO DE LA ASIGNACION DE TODO LO ANTERIOR AL SCRUM"""
rol_scrum.permisos.add(per_add_act,per_change_act,per_delete_act)
rol_scrum.permisos.add(per_add_flujo,per_change_flujo,per_delete_flujo,per_change_proyecto,per_add_sprint,per_change_sprint,per_delete_sprint)
rol_scrum.permisos.add(per_add_asigna,per_delete_asigna,per_change_asigna,per_add_delega,per_change_delega,per_delete_delega,per_change_hu_scrum)
rol_scrum.permisos.add(per_add_asignahu,per_change_asignahu,per_delete_asignahu,per_add_rol,per_change_rol,per_delete_rol)




"""Carga para el Product Owner"""
"""Voy a usar los permisos  ya cargados  y obtener los nuevos que se necesiten, lo mismo para los demas roles"""

per_add_hu=Permission.objects.get(name='Can add hu')
per_change_hu=Permission.objects.get(name='Can change hu')
per_delete_hu=Permission.objects.get(name='Can delete hu')

"""Y aca le asigno solamente esos 3 ultimos permisos obtenidos"""
rol_owner.permisos.add(per_add_hu,per_change_hu,per_delete_hu)




"""Carga para el Equipo"""
rol_equipo.permisos.add(permission1)


"""Carga para el Cliente"""
"""Se le asigna visualizar proyecto, visualizar equipo"""
rol_cliente.permisos.add(permission3,permission4)






"""Creacion de usuarios"""

admin=MyUser.objects.create(username='admin',email='admin@admin.com',password='pbkdf2_sha256$20000$Ao2gqCILS7bS$K6IH3coRBD0uHeHi1rrX61ZxVfZ26ohRnRF8WMwNs/U=',user_name='Administrador',last_name='Administrador',cedula='54321',is_active=True,is_admin=True)
alex=MyUser.objects.create(username='asantos',email='alexander.santos1993@gmail.com',password='pbkdf2_sha256$20000$0RDGBq3yHyA3$g36nRC8WrWsELLZ2MsJK+YZdKqMcuyjUlPlXOyX6+NE=',user_name='Alexander',last_name='Santos', cedula='5263762',is_active=True,is_admin=False)
nao=MyUser.objects.create(username='nnakagoe',email='naominakagoe@gmail.com',password='pbkdf2_sha256$20000$BgCsf64cPxhJ$RY2B9CMEte3CRveL21Zv9ijUfsVwozbrQEHxKycaqtk=',user_name='Naomi',last_name='Nakagoe', cedula='1234',is_active=True,is_admin=False)
naty=MyUser.objects.create(username='nsuarez',email='naty100494@gmail.com',password='pbkdf2_sha256$20000$jM8e5WFNMFH9$9EahH/rLMgHJpcOzWMkB230xRHX9sxtd1lWDBwvvskc=',user_name='Naty',last_name='Suarez', cedula='12345',is_active=True,is_admin=False)
julio=MyUser.objects.create(username='jpoggi',email='jotapoggi@gmail.com',password='pbkdf2_sha256$20000$fv8kctyko1l0$N6d3g7fSqHmM+3yBa1My37SiLEMlhowkbhtb4SoheOM=',user_name='Julio',last_name='Poggi', cedula='123456',is_active=True,is_admin=False)
guillermo=MyUser.objects.create(username='ggonzalez',email='g.gonzalez.pol@gmail.com',password='pbkdf2_sha256$20000$JSd4WTFTPFJM$PhavYulh8XSiCXPGHc75ICu5342H1DOjJjg46WNCJnM=',user_name='Guillermo',last_name='Gonzalez', cedula='1234567',is_active=True,is_admin=False)




"""Creacion de proyectos precargados"""
p1=Proyecto.objects.create(nombre='Proyecto 1',descripcion='Proyecto precargado 1',fecha_inicio=str(datetime.date.today()+ datetime.timedelta(days=-6)),fecha_fin=str(datetime.date.today() + datetime.timedelta(days=20)),duracion=20,cantidad_dias_transcurridos=6,estado='ACT')

p2=Proyecto.objects.create(nombre='Proyecto 2',descripcion='Proyecto precargado 2',fecha_inicio=str(datetime.date.today()- datetime.timedelta(days=20)),fecha_fin=str(datetime.date.today()),duracion=20,cantidad_dias_transcurridos=20,estado='ACT')

p3=Proyecto.objects.create(nombre='Proyecto 3',descripcion='Proyecto precargado 3',fecha_inicio=str(datetime.date.today()),fecha_fin=str(datetime.date.today() + datetime.timedelta(days=20)),duracion=20,cantidad_dias_transcurridos=0,estado='PEN')

p4=Proyecto.objects.create(nombre='Proyecto 4',descripcion='Proyecto precargado 4',fecha_inicio=str(datetime.date.today()),fecha_fin=str(datetime.date.today() + datetime.timedelta(days=20)),duracion=20,cantidad_dias_transcurridos=0,estado='PEN')




"""Asignacion de roles a usuarios dentro de un proyecto"""
AsignarRolProyecto.objects.create(usuario=nao,rol=rol_scrum,proyecto=p1) #Scrum
AsignarRolProyecto.objects.create(usuario=alex,rol=rol_owner,proyecto=p1) #Product Owner
AsignarRolProyecto.objects.create(usuario=naty,rol=rol_equipo,proyecto=p1) #Equipo
AsignarRolProyecto.objects.create(usuario=julio,rol=rol_equipo,proyecto=p1) #Equipo
AsignarRolProyecto.objects.create(usuario=guillermo,rol=rol_cliente,proyecto=p1) #Cliente
AsignarRolProyecto.objects.create(usuario=nao,rol=rol_scrum,proyecto=p2)
AsignarRolProyecto.objects.create(usuario=alex,rol=rol_owner,proyecto=p2)
AsignarRolProyecto.objects.create(usuario=naty,rol=rol_equipo,proyecto=p2)
AsignarRolProyecto.objects.create(usuario=julio,rol=rol_cliente,proyecto=p2) 
AsignarRolProyecto.objects.create(usuario=nao,rol=rol_scrum,proyecto=p3)
AsignarRolProyecto.objects.create(usuario=alex,rol=rol_owner,proyecto=p3)
AsignarRolProyecto.objects.create(usuario=julio,rol=rol_equipo,proyecto=p3)






"""Creacion de actividades para el flujo 1"""
act1=Actividades.objects.create(nombre='Analisis',descripcion='analisis')
act2=Actividades.objects.create(nombre='Disenho',descripcion='diseño')
act3=Actividades.objects.create(nombre='Despliegue',descripcion='Despliegue')
act4=Actividades.objects.create(nombre='Desarrollo',descripcion='desarrollo')
act5=Actividades.objects.create(nombre='Prueba',descripcion='prueba')


"""Creacion de actividades para el flujo 2"""
act6=Actividades.objects.create(nombre='Relevamiento',descripcion='relevamiento')
act7=Actividades.objects.create(nombre='Implementacion',descripcion='implementacion')
act8=Actividades.objects.create(nombre='Control',descripcion='control de tareas')


"""Cargar los primeros flujos"""
f1=Flujo.objects.create(nombre='Flujo1',orden_actividades='[1,2,3,4,5]')
f2=Flujo.objects.create(nombre='Flujo2',orden_actividades='[6,7,8]')
#Flujo 3, una combinacion de los flujos anteriores
f3=Flujo.objects.create(nombre='Flujo3',orden_actividades='[6,2,4,8]')



"""Cargar las actividades del flujo1"""
f1.actividades.add(act1,act2,act3,act4,act5)

"""Cargar las actividades del flujo2"""
f2.actividades.add(act6,act7,act8)

"""Cargar las actividades del flujo3"""
f3.actividades.add(act6,act2,act4,act8)



"""Creacion de HU"""
hu1=HU.objects.create(descripcion='HU1',valor_negocio=3,valor_tecnico=5,prioridad=95,duracion=15,acumulador_horas=0,estado='ACT',estado_en_actividad='PEN',valido=True,proyecto=p1)


hu2=HU.objects.create(descripcion='HU2',valor_negocio=5,valor_tecnico=7,prioridad=90,duracion=5,acumulador_horas=0,estado='ACT',estado_en_actividad='PEN',valido=True,proyecto=p1)


hu3=HU.objects.create(descripcion='HU3',valor_negocio=8,valor_tecnico=6,prioridad=85,duracion=20,acumulador_horas=0,estado='ACT',estado_en_actividad='PEN',valido=True,proyecto=p1)


hu4=HU.objects.create(descripcion='HU4',valor_negocio=2,valor_tecnico=5,prioridad=80,duracion=8,acumulador_horas=0,estado='ACT',estado_en_actividad='PEN',valido=True,proyecto=p1)


hu5=HU.objects.create(descripcion='HU5',valor_negocio=9,valor_tecnico=7,prioridad=75,duracion=5,acumulador_horas=0,estado='ACT',estado_en_actividad='PEN',valido=True,proyecto=p1)


hu6=HU.objects.create(descripcion='HU6',valor_negocio=8,valor_tecnico=6,prioridad=80,duracion=20,acumulador_horas=0,estado='ACT',estado_en_actividad='PEN',valido=True,proyecto=p1)


hu7=HU.objects.create(descripcion='HU7',valor_negocio=10,valor_tecnico=4,prioridad=68,duracion=30,acumulador_horas=0,estado='ACT',estado_en_actividad='PEN',valido=True,proyecto=p1)


hu8=HU.objects.create(descripcion='HU8',valor_negocio=5,valor_tecnico=7,prioridad=60,duracion=5,acumulador_horas=0,estado='ACT',estado_en_actividad='PEN',valido=True,proyecto=p1)


hu9=HU.objects.create(descripcion='HU9',valor_negocio=8,valor_tecnico=6,prioridad=45,duracion=20,acumulador_horas=0,estado='ACT',estado_en_actividad='PEN',valido=True,proyecto=p1)


hu10=HU.objects.create(descripcion='HU10',valor_negocio=2,valor_tecnico=5,prioridad=40,duracion=8,acumulador_horas=0,estado='ACT',estado_en_actividad='PEN',valido=True,proyecto=p1)


hu11=HU.objects.create(descripcion='HU11',valor_negocio=9,valor_tecnico=7,prioridad=35,duracion=5,acumulador_horas=0,estado='ACT',estado_en_actividad='PEN',valido=True,proyecto=p1)


hu12=HU.objects.create(descripcion='HU12',valor_negocio=10,valor_tecnico=0,prioridad=0,duracion=0,acumulador_horas=0,estado='ACT',estado_en_actividad='PEN',valido=False,proyecto=p1)





#Ahora voy a crear las hu para el sprint sp0 terminado, tienen que haber suficientes descripciones que indiquen que se finalizo su duracion
#seran 6 hus para este sprint

hu13=HU.objects.create(descripcion='HU13',valor_negocio=3,valor_tecnico=5,prioridad=95,duracion=15,acumulador_horas=15,estado='ACT',estado_en_actividad='APR',valido=True,proyecto=p1)

hu14=HU.objects.create(descripcion='HU14',valor_negocio=3,valor_tecnico=5,prioridad=85,duracion=15,acumulador_horas=15,estado='ACT',estado_en_actividad='APR',valido=True,proyecto=p1)

hu15=HU.objects.create(descripcion='HU15',valor_negocio=3,valor_tecnico=5,prioridad=75,duracion=15,acumulador_horas=15,estado='ACT',estado_en_actividad='APR',valido=True,proyecto=p1)

hu16=HU.objects.create(descripcion='HU16',valor_negocio=3,valor_tecnico=5,prioridad=65,duracion=15,acumulador_horas=15,estado='ACT',estado_en_actividad='APR',valido=True,proyecto=p1)


hu17=HU.objects.create(descripcion='HU17',valor_negocio=3,valor_tecnico=5,prioridad=55,duracion=15,acumulador_horas=15,estado='ACT',estado_en_actividad='APR',valido=True,proyecto=p1)

hu18=HU.objects.create(descripcion='HU18',valor_negocio=3,valor_tecnico=5,prioridad=45,duracion=15,acumulador_horas=15,estado='ACT',estado_en_actividad='APR',valido=True,proyecto=p1)




#Ahora voy a crear las hu que van a quedar pendientes en el sprint que finaliza anticipadamente sprint01,no les voy a cargar horas
hu19=HU.objects.create(descripcion='HU19',valor_negocio=3,valor_tecnico=5,prioridad=65,duracion=15,acumulador_horas=15,estado='ACT',estado_en_actividad='PEN',valido=True,proyecto=p1)

hu20=HU.objects.create(descripcion='HU20',valor_negocio=3,valor_tecnico=5,prioridad=55,duracion=15,acumulador_horas=15,estado='ACT',estado_en_actividad='PEN',valido=True,proyecto=p1)

hu21=HU.objects.create(descripcion='HU21',valor_negocio=3,valor_tecnico=5,prioridad=45,duracion=15,acumulador_horas=15,estado='ACT',estado_en_actividad='PEN',valido=True,proyecto=p1)




#HU para el proyeto 2 que va a finalizar

hu22=HU.objects.create(descripcion='HU22',valor_negocio=3,valor_tecnico=5,prioridad=45,duracion=15,acumulador_horas=15,estado='ACT',estado_en_actividad='APR',valido=True,proyecto=p2)

hu23=HU.objects.create(descripcion='HU23',valor_negocio=3,valor_tecnico=5,prioridad=45,duracion=15,acumulador_horas=15,estado='ACT',estado_en_actividad='APR',valido=True,proyecto=p2)

hu24=HU.objects.create(descripcion='HU24',valor_negocio=3,valor_tecnico=5,prioridad=45,duracion=15,acumulador_horas=15,estado='ACT',estado_en_actividad='APR',valido=True,proyecto=p2)

hu25=HU.objects.create(descripcion='HU25',valor_negocio=3,valor_tecnico=5,prioridad=45,duracion=15,acumulador_horas=15,estado='ACT',estado_en_actividad='APR',valido=True,proyecto=p2)

hu26=HU.objects.create(descripcion='HU26',valor_negocio=3,valor_tecnico=5,prioridad=45,duracion=15,acumulador_horas=15,estado='ACT',estado_en_actividad='APR',valido=True,proyecto=p2)

hu27=HU.objects.create(descripcion='HU27',valor_negocio=3,valor_tecnico=5,prioridad=45,duracion=15,acumulador_horas=15,estado='ACT',estado_en_actividad='APR',valido=True,proyecto=p2)

hu28=HU.objects.create(descripcion='HU28',valor_negocio=3,valor_tecnico=5,prioridad=45,duracion=15,acumulador_horas=15,estado='ACT',estado_en_actividad='APR',valido=True,proyecto=p2)

hu29=HU.objects.create(descripcion='HU29',valor_negocio=3,valor_tecnico=5,prioridad=45,duracion=15,acumulador_horas=15,estado='ACT',estado_en_actividad='APR',valido=True,proyecto=p2)

hu30=HU.objects.create(descripcion='HU30',valor_negocio=3,valor_tecnico=5,prioridad=45,duracion=15,acumulador_horas=15,estado='ACT',estado_en_actividad='APR',valido=True,proyecto=p2)

hu31=HU.objects.create(descripcion='HU31',valor_negocio=3,valor_tecnico=5,prioridad=45,duracion=15,acumulador_horas=15,estado='ACT',estado_en_actividad='APR',valido=True,proyecto=p2)

hu32=HU.objects.create(descripcion='HU32',valor_negocio=3,valor_tecnico=5,prioridad=45,duracion=15,acumulador_horas=15,estado='ACT',estado_en_actividad='ARP',valido=True,proyecto=p2)



#Agregar las actividades iniciales de las hu de acuerdo al flujo que fueron designados

hu1.actividad=act1
hu1.save()

hu2.actividad=act1
hu2.save()

hu3.actividad=act1
hu3.save()

hu4.actividad=act1
hu4.save()

hu5.actividad=act1
hu5.save()

hu6.actividad=act6
hu6.save()

hu7.actividad=act6
hu7.save()

hu8.actividad=act6
hu8.save()
 

#para el sp0 pongo las hu en actividad 5 nomas ya//parece que esto no hace falta

hu13.actividad=act5
hu13.save()
hu14.actividad=act5
hu14.save()
hu15.actividad=act5
hu15.save()
hu16.actividad=act8
hu16.save()
hu17.actividad=act8
hu17.save()
hu18.actividad=act8
hu18.save()

hu19.actividad=act8
hu19.save()
hu20.actividad=act8
hu20.save()
hu21.actividad=act8
hu21.save()




"""Creacion de un Sprint finalizado correctamente 
SPRINT0"""
#este va a ser el finalizado correctamente, con hus nuevas que tengo que crear

sp0=Sprint.objects.create(descripcion='sprint0',fecha_inicio=str(datetime.date.today()-datetime.timedelta(days=15)),duracion=7,estado='FIN',proyecto=p1)

"""Agregar hus a los sprint creados"""
sp0.hu.add(hu13,hu14,hu15,hu16,hu17,hu18)

"""Agregar hus a los sprint creados"""
sp0.flujo.add(f1,f2)

"""Agregar el quipo a los sprint creados"""
sp0.equipo.add(julio,naty)

"""Clasificar esas hus seleccionadas en flujos"""
#hu 13,14,15 en flujo 1 y 16,17,18 en flujo 2
hu13Flujo1=AsignaHU_flujo.objects.create(flujo_al_que_pertenece=f1)
hu13Flujo1.lista_de_HU.add(hu13,hu14,hu15)
hu13Flujo1.save()
hu16Flujo1=AsignaHU_flujo.objects.create(flujo_al_que_pertenece=f2)
hu16Flujo1.lista_de_HU.add(hu16,hu17,hu18)
hu16Flujo1.save()

AsignaHU_Usuario.objects.create(usuario=naty,hu=hu13)
AsignaHU_Usuario.objects.create(usuario=naty,hu=hu15)
AsignaHU_Usuario.objects.create(usuario=naty,hu=hu17)
AsignaHU_Usuario.objects.create(usuario=julio,hu=hu14)
AsignaHU_Usuario.objects.create(usuario=julio,hu=hu16)
AsignaHU_Usuario.objects.create(usuario=julio,hu=hu18)



####################################################################






#Creacion y asignacion de descripciones de hu 13,14,15

dhu131=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Analisis",estado='PRO')

dhu132=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Disenho",estado='PRO')

dhu133=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Despliegue",estado='PRO')

dhu134=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Desarrollo",estado='PRO')

dhu135=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Prueba",estado='PRO')

hu13.hu_descripcion.add(dhu131)
hu13.hu_descripcion.add(dhu132)
hu13.hu_descripcion.add(dhu133)
hu13.hu_descripcion.add(dhu134)
hu13.hu_descripcion.add(dhu135)
hu13.actividad=act5
hu13.acumulador_horas=15
hu13.save()

dhu141=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Analisis",estado='PRO')

dhu142=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Disenho",estado='PRO')

dhu143=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Despliegue",estado='PRO')

dhu144=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Desarrollo",estado='PRO')

dhu145=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Prueba",estado='PRO')

hu14.hu_descripcion.add(dhu141)
hu14.hu_descripcion.add(dhu142)
hu14.hu_descripcion.add(dhu143)
hu14.hu_descripcion.add(dhu144)
hu14.hu_descripcion.add(dhu145)
hu14.actividad=act5
hu14.acumulador_horas=15
hu14.save()

dhu151=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Analisis",estado='PRO')

dhu152=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="diseño",estado='PRO')

dhu153=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Despliegue",estado='PRO')

dhu154=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="desarrollo",estado='PRO')

dhu155=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="prueba",estado='PRO')

hu15.hu_descripcion.add(dhu151)
hu15.hu_descripcion.add(dhu152)
hu15.hu_descripcion.add(dhu153)
hu15.hu_descripcion.add(dhu154)
hu15.hu_descripcion.add(dhu155)
hu15.actividad=act5
hu15.acumulador_horas=15
hu15.save()

#Creacion y asignacion de descripciones de hu 16,17,18
dhu161=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Relevamiento",estado='PRO')

dhu162=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Implementacion",estado='PRO')

dhu163=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Control",estado='PRO')

hu16.hu_descripcion.add(dhu161)
hu16.hu_descripcion.add(dhu162)
hu16.hu_descripcion.add(dhu163)
hu16.actividad=act8
hu16.acumulador_horas=15
hu16.save()

dhu171=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Relevamiento",estado='PRO')

dhu172=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Implementacion",estado='PRO')

dhu173=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Control",estado='PRO')

hu17.hu_descripcion.add(dhu171)
hu17.hu_descripcion.add(dhu172)
hu17.hu_descripcion.add(dhu173)
hu17.actividad=act8
hu17.acumulador_horas=15
hu17.save()

dhu181=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Relevamiento",estado='PRO')

dhu182=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Implementacion",estado='PRO')

dhu183=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Control",estado='PRO')

hu18.hu_descripcion.add(dhu181)
hu18.hu_descripcion.add(dhu182)
hu18.hu_descripcion.add(dhu183)
hu18.actividad=act8
hu18.acumulador_horas=15
hu18.save()




"""--------------------------------------Creacion de un Sprint finalizado con HUs pendientes SPRINT01------------------------------"""

#este va a ser el que tenga hus pendientes las cuales tengo que crear nuevas
sp01=Sprint.objects.create(descripcion='sprint01',fecha_inicio=str(datetime.date.today()+datetime.timedelta(days=-7)),duracion=6,proyecto=p1)

"""Agregar hus a los sprint creados"""
sp01.hu.add(hu19,hu20,hu21)

"""Agregar hus a los sprint creados"""
sp01.flujo.add(f2)

"""Agregar el quipo a los sprint creados"""
sp01.equipo.add(julio,naty)

"""Clasificar esas hus seleccionadas en flujos"""
#agregar descripciones de progreso
dhu191=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Relevamiento",estado='PRO')

hu19.hu_descripcion.add(dhu191)
hu19.estado_en_actividad='PRO'
hu19.actividad=act8
hu19.acumulador_horas=3
hu19.save()

dhu201=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Relevamiento",estado='PRO')

hu20.hu_descripcion.add(dhu201)
hu20.estado_en_actividad='PRO'
hu20.actividad=act8
hu20.acumulador_horas=3
hu20.save()

dhu211=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Relevamiento",estado='PRO')

hu21.hu_descripcion.add(dhu211)
hu21.estado_en_actividad='PRO'
hu21.actividad=act8
hu21.acumulador_horas=3
hu21.save()

#hu 19,20,21 en flujo 1 para sprint01
hu19Flujo1=AsignaHU_flujo.objects.create(flujo_al_que_pertenece=f2)
hu19Flujo1.lista_de_HU.add(hu19,hu20,hu21)
hu19Flujo1.save()



"""--------------------------------------Creacion de un Sprint de consulta SPRINT1-----------------------------------------------"""

sp1=Sprint.objects.create(descripcion='sprint1',fecha_inicio=str(datetime.date.today()),duracion=10,estado='ACT',proyecto=p1)

sp1.hu.add(hu1,hu2,hu3,hu4,hu5,hu6,hu7,hu8)

sp1.flujo.add(f1,f2)

sp1.equipo.add(julio,naty)

#hu1 y hu2 estan en el flujo 1
hu1Flujo1=AsignaHU_flujo.objects.create(flujo_al_que_pertenece=f1)
hu1Flujo1.lista_de_HU.add(hu1,hu2,hu3,hu4,hu5)

#hu3 esta en el flujo 2
hu3flujo2=AsignaHU_flujo.objects.create(flujo_al_que_pertenece=f2)
hu3flujo2.lista_de_HU.add(hu6,hu7,hu8)

"""Delegacion de HU a un usuario"""
AsignaHU_Usuario.objects.create(usuario=naty,hu=hu19)
AsignaHU_Usuario.objects.create(usuario=naty,hu=hu20)
AsignaHU_Usuario.objects.create(usuario=julio,hu=hu21)


AsignaHU_Usuario.objects.create(usuario=naty,hu=hu1)

AsignaHU_Usuario.objects.create(usuario=naty,hu=hu2)

AsignaHU_Usuario.objects.create(usuario=naty,hu=hu3)

AsignaHU_Usuario.objects.create(usuario=naty,hu=hu4)

AsignaHU_Usuario.objects.create(usuario=julio,hu=hu5)

AsignaHU_Usuario.objects.create(usuario=julio,hu=hu6)

AsignaHU_Usuario.objects.create(usuario=julio,hu=hu7)

AsignaHU_Usuario.objects.create(usuario=julio,hu=hu8)




"""Creacion de descripciones para la HU1 Mensaje Finalizada a Tiempo"""

dhu1=Horas_Trabajadas.objects.create(horas_trabajadas=2,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Analisis",estado='PRO')


dhu2=Horas_Trabajadas.objects.create(horas_trabajadas=2,descripcion_horas_trabajadas='Tarea2',fecha=str(datetime.date.today()),actividad="Analisis",estado='FIN')


dhu3=Horas_Trabajadas.objects.create(horas_trabajadas=4,descripcion_horas_trabajadas='Tarea3',fecha=str(datetime.date.today()),actividad="Diseño",estado='PRO')

dhu4=Horas_Trabajadas.objects.create(horas_trabajadas=2,descripcion_horas_trabajadas='Tarea4',fecha=str(datetime.date.today() + datetime.timedelta(1)),actividad="Diseño",estado='FIN')

dhu5=Horas_Trabajadas.objects.create(horas_trabajadas=1.2,descripcion_horas_trabajadas='Tarea5',fecha=str(datetime.date.today() + datetime.timedelta(1)),actividad="Despliegue",estado='FIN')

dhu6=Horas_Trabajadas.objects.create(horas_trabajadas=1.8,descripcion_horas_trabajadas='Tarea6',fecha=str(datetime.date.today() + datetime.timedelta(1)),actividad="Desarrollo",estado='FIN')

dhu7=Horas_Trabajadas.objects.create(horas_trabajadas=2,descripcion_horas_trabajadas='Tarea7',fecha=str(datetime.date.today() + datetime.timedelta(1)),actividad="Prueba",estado='FIN')



"""Asociar la hu con una descripcion para HU1"""
hu1.hu_descripcion.add(dhu1)
hu1.hu_descripcion.add(dhu2)
hu1.hu_descripcion.add(dhu3)
hu1.hu_descripcion.add(dhu4)
hu1.hu_descripcion.add(dhu5)
hu1.hu_descripcion.add(dhu6)
hu1.hu_descripcion.add(dhu7)



"""Coloco en los campos estado y actividad de la HU a la que cargamos las descripciones los datos correctos segun la descripcion agregada"""

hu1.estado_en_actividad='FIN'
hu1.actividad=act5
hu1.acumulador_horas=15
hu1.save()

"""Creacion de descripciones para la HU2 Mensaje No finalizo. Contactar con Scrum"""

dhu1=Horas_Trabajadas.objects.create(horas_trabajadas=2,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()+ datetime.timedelta(2)),actividad="Analisis",estado='PRO')

dhu2=Horas_Trabajadas.objects.create(horas_trabajadas=2,descripcion_horas_trabajadas='Tarea2',fecha=str(datetime.date.today() + datetime.timedelta(2)),actividad="Analisis",estado='FIN')


dhu3=Horas_Trabajadas.objects.create(horas_trabajadas=1,descripcion_horas_trabajadas='Tarea3',fecha=str(datetime.date.today() + datetime.timedelta(2)),actividad="Diseño",estado='PRO')


"""Asociar la hu con una descripcion para HU2, mismo que el anterior, estan en el mismo Flujo"""
hu2.hu_descripcion.add(dhu1)
hu2.hu_descripcion.add(dhu2)
hu2.hu_descripcion.add(dhu3)

hu2.estado_en_actividad='PRO'
hu2.actividad=act2
hu2.acumulador_horas=5
hu2.save()

"""Creacion de descripciones para la HU3 Mensaje Finalizado antes de tiempo"""
dhu1=Horas_Trabajadas.objects.create(horas_trabajadas=4,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()+ datetime.timedelta(3)),actividad="Analisis",estado='FIN')

dhu2=Horas_Trabajadas.objects.create(horas_trabajadas=4,descripcion_horas_trabajadas='Tarea2',fecha=str(datetime.date.today()+ datetime.timedelta(3)),actividad="Diseño",estado='FIN')

dhu3=Horas_Trabajadas.objects.create(horas_trabajadas=4,descripcion_horas_trabajadas='Tarea3',fecha=str(datetime.date.today() + datetime.timedelta(4)),actividad="Despliegue",estado='FIN')

dhu4=Horas_Trabajadas.objects.create(horas_trabajadas=2,descripcion_horas_trabajadas='Tarea4',fecha=str(datetime.date.today() + datetime.timedelta(4)),actividad="Desarrollo",estado='FIN')


dhu5=Horas_Trabajadas.objects.create(horas_trabajadas=4,descripcion_horas_trabajadas='Tarea5',fecha=str(datetime.date.today() + datetime.timedelta(5)),actividad="Prueba",estado='FIN')



"""Asociar la hu con una descripcion para HU2, mismo que el anterior, estan en el mismo Flujo"""
hu3.hu_descripcion.add(dhu1)
hu3.hu_descripcion.add(dhu2)
hu3.hu_descripcion.add(dhu3)
hu3.hu_descripcion.add(dhu4)
hu3.hu_descripcion.add(dhu5)

hu3.estado_en_actividad='FIN'
hu3.actividad=act5
hu3.acumulador_horas=18
hu3.save()


"""Ya que se comenzo la primera HU de mas alta prioridad del sprint cambiamos su estado de ACT a CON"""

sp1.estado='CON'
sp1.save()



"""--------------------------------------Creacion de un Sprint finalizado correctamente SPRINT_FIN-----------------------------------"""

#este va a ser el finalizado correctamente, con hus nuevas que tengo que crear

spF=Sprint.objects.create(descripcion='sprint_fin',fecha_inicio=str(datetime.date.today()-datetime.timedelta(days=15)),duracion=7,estado='FIN',proyecto=p2)

"""Agregar hus a los sprint creados"""
spF.hu.add(hu22,hu23,hu24,hu25,hu26,hu27,hu28,hu29,hu30,hu31,hu32)

"""Agregar hus a los sprint creados"""
spF.flujo.add(f1,f2,f3)

"""Agregar el quipo a los sprint creados"""
spF.equipo.add(nao,naty,julio)

"""Clasificar esas hus seleccionadas en flujos"""
#hu 22,23,24,25 en flujo 1 , 26,27,28 en flujo y 29,30,31,32 en el flujo3
hu22Flujo1=AsignaHU_flujo.objects.create(flujo_al_que_pertenece=f1)
hu22Flujo1.lista_de_HU.add(hu22,hu23,hu24,hu25)
hu22Flujo1.save()
hu26Flujo2=AsignaHU_flujo.objects.create(flujo_al_que_pertenece=f2)
hu26Flujo2.lista_de_HU.add(hu26,hu27,hu28)
hu26Flujo2.save()
hu29Flujo3=AsignaHU_flujo.objects.create(flujo_al_que_pertenece=f3)
hu29Flujo3.lista_de_HU.add(hu29,hu30,hu31,hu32)
hu29Flujo3.save()

AsignaHU_Usuario.objects.create(usuario=nao,hu=hu22)
AsignaHU_Usuario.objects.create(usuario=nao,hu=hu23)
AsignaHU_Usuario.objects.create(usuario=nao,hu=hu24)
AsignaHU_Usuario.objects.create(usuario=nao,hu=hu25)
AsignaHU_Usuario.objects.create(usuario=naty,hu=hu26)
AsignaHU_Usuario.objects.create(usuario=naty,hu=hu27)
AsignaHU_Usuario.objects.create(usuario=naty,hu=hu28)
AsignaHU_Usuario.objects.create(usuario=julio,hu=hu29)
AsignaHU_Usuario.objects.create(usuario=julio,hu=hu30)
AsignaHU_Usuario.objects.create(usuario=julio,hu=hu31)
AsignaHU_Usuario.objects.create(usuario=julio,hu=hu32)




##################################################################



#Creacion y asignacion de descripciones de hu 22, 23,24,25
dhu221=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Analisis",estado='PRO')
dhu222=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Disenho",estado='PRO')
dhu223=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Despliegue",estado='PRO')
dhu224=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Desarrollo",estado='PRO')
dhu225=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Prueba",estado='PRO')
hu22.hu_descripcion.add(dhu221)
hu22.hu_descripcion.add(dhu222)
hu22.hu_descripcion.add(dhu223)
hu22.hu_descripcion.add(dhu224)
hu22.hu_descripcion.add(dhu225)
hu22.actividad=act1
hu22.acumulador_horas=15
hu22.save()

"""Coloco en los campos estado y actividad de la HU a la que cargamos las descripciones los datos correctos segun la descripcion agregada"""
hu22.estado_en_actividad='APR'
hu22.actividad=act1
hu22.acumulador_horas=15
hu22.save()


dhu231=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Analisis",estado='PRO')
dhu232=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Disenho",estado='PRO')
dhu233=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Despliegue",estado='PRO')
dhu234=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Desarrollo",estado='PRO')
dhu235=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Prueba",estado='PRO')
hu23.hu_descripcion.add(dhu231)
hu23.hu_descripcion.add(dhu232)
hu23.hu_descripcion.add(dhu233)
hu23.hu_descripcion.add(dhu234)
hu23.hu_descripcion.add(dhu235)
hu23.actividad=act1
hu23.acumulador_horas=15
hu23.save()

"""Coloco en los campos estado y actividad de la HU a la que cargamos las descripciones los datos correctos segun la descripcion agregada"""
hu23.estado_en_actividad='APR'
hu23.actividad=act1
hu23.acumulador_horas=15
hu23.save()


dhu241=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Analisis",estado='PRO')
dhu242=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Disenho",estado='PRO')
dhu243=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Despliegue",estado='PRO')
dhu244=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Desarrollo",estado='PRO')
dhu245=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Prueba",estado='PRO')
hu24.hu_descripcion.add(dhu241)
hu24.hu_descripcion.add(dhu242)
hu24.hu_descripcion.add(dhu243)
hu24.hu_descripcion.add(dhu244)
hu24.hu_descripcion.add(dhu245)
hu24.actividad=act1
hu24.acumulador_horas=15
hu24.save()


"""Coloco en los campos estado y actividad de la HU a la que cargamos las descripciones los datos correctos segun la descripcion agregada"""
hu24.estado_en_actividad='APR'
hu24.actividad=act1
hu24.acumulador_horas=15
hu24.save()


dhu251=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Analisis",estado='PRO')
dhu252=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="diseño",estado='PRO')
dhu253=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Despliegue",estado='PRO')
dhu254=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="desarrollo",estado='PRO')
dhu255=Horas_Trabajadas.objects.create(horas_trabajadas=3,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="prueba",estado='PRO')
hu25.hu_descripcion.add(dhu251)
hu25.hu_descripcion.add(dhu252)
hu25.hu_descripcion.add(dhu253)
hu25.hu_descripcion.add(dhu254)
hu25.hu_descripcion.add(dhu255)
hu25.actividad=act1
hu25.acumulador_horas=15
hu25.save()


"""Coloco en los campos estado y actividad de la HU a la que cargamos las descripciones los datos correctos segun la descripcion agregada"""
hu25.estado_en_actividad='APR'
hu25.actividad=act1
hu25.acumulador_horas=15
hu25.save()



#Creacion y asignacion de descripciones de hu 26,27,28
dhu261=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Relevamiento",estado='PRO')
dhu262=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Implementacion",estado='PRO')
dhu263=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Control",estado='PRO')
hu26.hu_descripcion.add(dhu261)
hu26.hu_descripcion.add(dhu262)
hu26.hu_descripcion.add(dhu263)
hu26.actividad=act6
hu26.acumulador_horas=15
hu26.save()


"""Coloco en los campos estado y actividad de la HU a la que cargamos las descripciones los datos correctos segun la descripcion agregada"""
hu26.estado_en_actividad='APR'
hu26.actividad=act6
hu26.acumulador_horas=15
hu26.save()


dhu271=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Relevamiento",estado='PRO')
dhu272=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Implementacion",estado='PRO')
dhu273=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Control",estado='PRO')
hu27.hu_descripcion.add(dhu271)
hu27.hu_descripcion.add(dhu272)
hu27.hu_descripcion.add(dhu273)
hu27.actividad=act6
hu27.acumulador_horas=15
hu27.save()


"""Coloco en los campos estado y actividad de la HU a la que cargamos las descripciones los datos correctos segun la descripcion agregada"""
hu27.estado_en_actividad='APR'
hu27.actividad=act6
hu27.acumulador_horas=15
hu27.save()


dhu281=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Relevamiento",estado='PRO')
dhu282=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Implementacion",estado='PRO')
dhu283=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Control",estado='PRO')
hu28.hu_descripcion.add(dhu281)
hu28.hu_descripcion.add(dhu282)
hu28.hu_descripcion.add(dhu283)
hu28.actividad=act8
hu28.acumulador_horas=15
hu28.save()

"""Coloco en los campos estado y actividad de la HU a la que cargamos las descripciones los datos correctos segun la descripcion agregada"""
hu28.estado_en_actividad='APR'
hu28.actividad=act6
hu28.acumulador_horas=15
hu28.save()


#Creacion y asignacion de descripciones de hu 29,30,31,32
dhu291=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Relevamiento",estado='PRO')
dhu292=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Disenho",estado='PRO')
dhu293=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Desarrollo",estado='PRO')
dhu294=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Control",estado='PRO')
hu29.hu_descripcion.add(dhu291)
hu29.hu_descripcion.add(dhu292)
hu29.hu_descripcion.add(dhu293)
hu29.hu_descripcion.add(dhu294)
hu29.actividad=act6
hu29.acumulador_horas=15
hu29.save()

"""Coloco en los campos estado y actividad de la HU a la que cargamos las descripciones los datos correctos segun la descripcion agregada"""
hu29.estado_en_actividad='APR'
hu29.actividad=act6
hu29.acumulador_horas=15
hu29.save()


dhu301=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Relevamiento",estado='PRO')
dhu302=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Disenho",estado='PRO')
dhu303=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Desarrollo",estado='PRO')
dhu304=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Control",estado='PRO')
hu30.hu_descripcion.add(dhu301)
hu30.hu_descripcion.add(dhu302)
hu30.hu_descripcion.add(dhu303)
hu30.hu_descripcion.add(dhu304)
hu30.actividad=act8
hu30.acumulador_horas=15
hu30.save()

"""Coloco en los campos estado y actividad de la HU a la que cargamos las descripciones los datos correctos segun la descripcion agregada"""
hu30.estado_en_actividad='APR'
hu30.actividad=act6
hu30.acumulador_horas=15
hu30.save()


dhu311=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Relevamiento",estado='PRO')
dhu312=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Disenho",estado='PRO')
dhu313=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Desarrollo",estado='PRO')
dhu314=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Control",estado='PRO')
hu31.hu_descripcion.add(dhu311)
hu31.hu_descripcion.add(dhu312)
hu31.hu_descripcion.add(dhu313)
hu31.hu_descripcion.add(dhu314)
hu31.actividad=act6
hu31.acumulador_horas=15
hu31.save()

"""Coloco en los campos estado y actividad de la HU a la que cargamos las descripciones los datos correctos segun la descripcion agregada"""
hu31.estado_en_actividad='APR'
hu31.actividad=act6
hu31.acumulador_horas=15
hu31.save()

dhu321=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Relevamiento",estado='PRO')
dhu322=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Disenho",estado='PRO')
dhu323=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Desarrollo",estado='PRO')
dhu324=Horas_Trabajadas.objects.create(horas_trabajadas=5,descripcion_horas_trabajadas='Tarea1',fecha=str(datetime.date.today()),actividad="Control",estado='PRO')
hu32.hu_descripcion.add(dhu321)
hu32.hu_descripcion.add(dhu322)
hu32.hu_descripcion.add(dhu323)
hu32.hu_descripcion.add(dhu324)
hu32.actividad=act6
hu32.acumulador_horas=15
hu32.save()

"""Coloco en los campos estado y actividad de la HU a la que cargamos las descripciones los datos correctos segun la descripcion agregada"""
hu32.estado_en_actividad='APR'
hu32.actividad=act6
hu32.acumulador_horas=15
hu32.save()













