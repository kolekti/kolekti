from django.contrib import admin

# Register your models here.
from kserver.models import Project, UserProfile, UserProject, Pack, Order, Template

admin.site.register(UserProfile)
admin.site.register(Project)
admin.site.register(UserProject)
admin.site.register(Pack)
admin.site.register(Template)
