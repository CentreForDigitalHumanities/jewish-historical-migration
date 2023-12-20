from django.contrib import admin

from .models import (
    Area, Region, Place, Record, PrimaryCategory, SecondaryCategory,
    Language, Script, Century
)


@admin.action(description="Fetch information from Pleiades")
def fetch_from_pleiades(modeladmin, request, queryset):
    for item in queryset:
        item.fetch_from_pleiades()
        item.save()

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    actions = [fetch_from_pleiades]
    list_display = ['name', 'area', 'region', 'pleiades_id']
    list_filter = ['area', 'region']
    ordering = ['name']


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    pass


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    pass

@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = [
        'source', 'area', 'region', 'place', 'category1', 
        'category2', 'period', 'inscriptions_count'
    ]
    list_filter = [
        'area', 'region', 'estimated_centuries', 'languages', 'scripts', 
        'category1', 'category2'
    ]
    list_select_related = ["place", "category1", "category2"]
    ordering = ['source']


admin.site.register(PrimaryCategory)
admin.site.register(SecondaryCategory)
admin.site.register(Language)
admin.site.register(Script)
admin.site.register(Century)
