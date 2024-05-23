from django.contrib import admin
from kerberos_profiles.models import Profile

# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('kerberosID', 'name', 'uniqueiitdid', 'category', 'department')
    search_fields = ('kerberosID', 'name', 'uniqueiitdid', 'category', 'department', 'deviceUUID')
    list_filter = ('category', 'department')
    
admin.site.register(Profile, ProfileAdmin)
    
