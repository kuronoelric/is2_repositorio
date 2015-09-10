#coding: utf-8
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from sis.models import MyUser, Proyecto, Rol, AsignarRolProyecto, Flujo,\
    Actividades
from django.contrib.auth.models import Group



class UserCreationForm(forms.ModelForm):
    """Un formulario para crear nuevos usuarios, incluyendo todos los campos requeridos
    mas un campo dende se repite la contraseña"""
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    class Meta:
        """Clase meta de un ModelForm donde se indica el Modelo relacionado y los campos a mostrar"""
        model = MyUser
        fields = ('username', 'cedula', 'email', 'user_name', 'last_name')

    def clean_password2(self):
        """metodo que resetea los campos de contraseñas en caso de que no coincidan
        las contraseñas ingresadas"""
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password2

    def save(self, commit=True):
        """metodo que permite guardar los datos ingresados en el formulario"""
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """Formulario para actualizar usuarios. incluye todos los campo de usuario
    ,pero reemplaza el campo de contraseña con el campo hash de contraseña
    del admin"""
    #password = ReadOnlyPasswordHashField()

    class Meta:
        """Clase meta de un ModelForm donde se indica el Modelo relacionado y los campos a mostrar"""
        model = MyUser
        fields = ('username', 'cedula', 'email', 'is_active', 'is_admin',)



class MyUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on gestor_MyUser
    list_display = ('username','email', 'is_admin','is_active',)
    list_filter = ('is_admin','is_active',)
    fieldsets = (
       (None, {'fields': ('username',)}),
       ('Informacion personal', {'fields': ('cedula', 'email','user_name', 'last_name')}),
       ('Estado', {'fields': ('is_active',)}),
       ('Privilegio', {'fields': ('is_admin',)})
   )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
       (None, {
           'classes': ('wide',),
           'fields': ('username', 'cedula', 'email', 'user_name', 'last_name', 'password1', 'password2')}
       ),
    )
    search_fields = ('username',)
    ordering = ('username',)
    filter_horizontal = ()
    
    
#-----------------------------------------------------------------------------------------------------------


class FormularioProyecto(forms.ModelForm):
    """
    Formulario del modelo Proyecto con sus campos seleccionados.
    """
    class Meta:
        model=Proyecto
        fields=('nombre','descripcion','fecha_inicio','fecha_fin') #el estado en el momento de creacion tendra valor por defecto el usuario no decide  
    
class ProyectoAdmin(admin.ModelAdmin):
    """Configura la vista de administracion de Proyecto para un usuario administrador,
    para establecer los proyectos en estado ACTIVO en la creacion"""
    form=FormularioProyecto
    list_display = ('nombre', 'id', 'fecha_inicio','fecha_fin','duracion')
    list_filter = ('estado',)
    ordering = ('nombre',)
    save_as = True 
    def save_model(self,request,obj,form,change):
        """Permite establecer el Estado por defecto en el momento de la creacion que es PENDIENTE"""
        obj.estado='PEN'
        obj.duracion=int(str((obj.fecha_fin.date()-obj.fecha_inicio.date()).days))
        obj.cantidad_dias_transcurridos=0
        obj.save()
        pass


#-----------------------------------------------------------------------------------------------------------


class FormularioRol(forms.ModelForm):
    """
    Formulario del modelo Rol con sus campos seleccionados.
    """
    class Meta:
        model=Rol
        fields=('permisos','nombre_rol','descripcion')


class RolAdmin(admin.ModelAdmin):
    """Configura la vista de administracion, modificacion y creacion de roles para un administrador,
    lsta nombre y desprpcion y al crear, automaticamente establece al usuario actual como creador del rol"""
    form=FormularioRol
    list_display = ('nombre_rol', 'descripcion')
    list_filter = ('id',)
    ordering = ('id',)
    filter_horizontal = ('permisos',)
    save_as = True


#-----------------------------------------------------------------------------------------------------------














    

#-----------------------------------------------------------------------------------------------------------


class FormularioFlujo(forms.ModelForm):
    """
    Formulario del modelo Flujo con sus campos seleccionados.
    """
    class Meta:
        model=Flujo
        fields=('nombre','actividades') #el estado en el momento de creacion tendra valor por defecto el usuario no decide  
         

class FlujoAdmin(admin.ModelAdmin):
    """Configura la vista de administracion de Flujos para un usuario administrador,
    lista nombre y estado y al modificar permite guardar como"""
    form=FormularioFlujo
    list_display = ('nombre',)#, 'estado')
    #list_filter = ('estado',)
    ordering = ('id',)
    filter_horizontal = ('actividades',)
    exclude = ('proyecto',)
    save_as = True 
    def save_model(self,request,obj,form,change):
        """Permite establecer el Estado por defecto en el momento de la creacion que es ACTIVO"""
        #obj.estado='ACT'
        obj.save()

    

admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Proyecto, ProyectoAdmin)
admin.site.register(Rol, RolAdmin)
admin.site.register(AsignarRolProyecto)
#admin.site.register(Flujo,FlujoAdmin)
#admin.site.register(Actividades)



admin.site.unregister(Group)