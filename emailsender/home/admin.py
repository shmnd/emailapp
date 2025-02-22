from django.contrib import admin
from home.models import Subscriber,Template,EmailOpenTracking,EmailSummery,Tags
# Register your models here.
admin.site.register(Subscriber)
admin.site.register(Template)
admin.site.register(EmailOpenTracking)
admin.site.register(EmailSummery)
admin.site.register(Tags) 

