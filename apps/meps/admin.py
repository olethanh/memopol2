from reps.models import WebSite, Party, Opinion, OpinionREP
from models import CountryMEP, GroupMEP, DelegationRole
from models import Committee, Delegation, Country, Group, MEP, CommitteeRole, DelegationRole, Organization , OrganizationMEP
from django.contrib import admin

admin.site.register(Committee)
admin.site.register(CommitteeRole)
admin.site.register(Delegation)
admin.site.register(DelegationRole)
admin.site.register(Country)
admin.site.register(Group)
admin.site.register(Party)
admin.site.register(Organization)
admin.site.register(OrganizationMEP)

class CountriesInline(admin.TabularInline):
    model = CountryMEP
    extra = 1

class GroupInline(admin.TabularInline):
    model = GroupMEP
    extra = 1

class DelegationInline(admin.TabularInline):
    model = DelegationRole
    extra = 1

class CommitteeInline(admin.TabularInline):
    model = CommitteeRole
    extra = 1

class OrganizationMEPInline(admin.TabularInline):
    model = OrganizationMEP
    extra = 1

class MEPAdmin(admin.ModelAdmin):
    search_fields = ['last_name']
    list_filter = ('active', 'countries', 'groups')
    list_display = ('last_name', 'first_name', 'active')
    inlines = [CountriesInline, GroupInline, DelegationInline, CommitteeInline, OrganizationMEPInline]

admin.site.register(MEP, MEPAdmin)
