from django.contrib import admin

from accounts.models import TermsAndConditions
from master.models import *

# Register your models here.
admin.site.register(CategoryMaster)
admin.site.register(BranchMaster)
admin.site.register(LocationMaster)
admin.site.register(LocationExportStatus)
class EmiratesAdmin(admin.ModelAdmin):
    list_display = ['created_by','created_date','name']
admin.site.register(EmirateMaster,EmiratesAdmin)

class PrivacyPolicyAdmin(admin.ModelAdmin):
    list_display = ['created_by','created_date','content']
admin.site.register(PrivacyPolicy,PrivacyPolicyAdmin)

class TermsAndConditionsAdmin(admin.ModelAdmin):
    list_display = ['created_by','created_date','description']
admin.site.register(TermsAndConditions,TermsAndConditionsAdmin)