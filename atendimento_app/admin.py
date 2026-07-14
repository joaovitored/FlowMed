from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Consultorio, Senha, Perfil

# Register your models here.
class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = [PerfilInline]

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Consultorio)
class ConsultorioAdmin(admin.ModelAdmin):
    list_display=('nome','profissional','ativo')
    search_fields=('nome',)
    
@admin.register(Senha)
class SenhaAdmin(admin.ModelAdmin):
    list_display=('nome_paciente','numero','tipo_servico','prioridade','status','criado_em')
    search_fields=('nome_paciente','numero')
    list_filter=('tipo_servico','prioridade','status')
    date_hierarchy = 'criado_em'
    
@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display=('usuario','tipo','consultorio')
    list_filter=('tipo',)
    search_fields=('usuario__username',)

