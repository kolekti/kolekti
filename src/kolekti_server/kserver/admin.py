from django.contrib import admin

# Register your models here.
from kserver.models import Project, UserProject, Pack, Order

admin.site.register(Project)
admin.site.register(UserProject)
admin.site.register(Pack)
admin.site.register(Order)
