#coding: utf-8
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from sis.models import MyUser



class UserCreationForm(forms.ModelForm):
    """Un formulario para crear nuevos usuarios, incluyendo todos los campos requeridos
    mas un campo dende se repite la contraseña"""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        """Clase meta de un ModelForm donde se indica el Modelo relacionado y los campos a mostrar"""
        model = MyUser
        fields = ('username', 'email', 'user_name', 'last_name')

    def clean_password2(self):
        """metodo que resetea los campos de contraseñas en caso de que no coincidan
        las contraseñas ingresadas"""
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
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
    password = ReadOnlyPasswordHashField()
    class Meta:
        """Clase meta de un ModelForm donde se indica el Modelo relacionado y los campos a mostrar"""
        model = MyUser
        fields = ('username','email', 'password',  'is_active', 'is_admin',)

    def clean_password(self):
        """metodo que resetea los campos de contraseñas en caso de que no coincidan
        las contraseñas ingresadas"""
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class MyUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on gestor_MyUser
    list_display = ('username','email', 'is_admin','is_active',)
    list_filter = ('is_admin','is_active',)
    fieldsets = (
       (None, {'fields': ('username', 'password')}),
       ('Personal info', {'fields': ('email','user_name', 'last_name')}),
       ('Permissions', {'fields': ('is_admin','is_active',)}),
   )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
       (None, {
           'classes': ('wide',),
           'fields': ('username', 'email', 'user_name', 'last_name', 'password1', 'password2')}
       ),
    )
    search_fields = ('username',)
    ordering = ('username',)
    filter_horizontal = ()

admin.site.register(MyUser, MyUserAdmin)