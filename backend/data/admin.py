from django.contrib import admin

from .models import Area, Region, Place, Record


@admin.action(description="Fetch information from Pleiades")
def fetch_from_pleiades(modeladmin, request, queryset):
    for item in queryset:
        item.fetch_from_pleiades()
        item.save()

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    actions = [fetch_from_pleiades]


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    pass


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    pass

@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    pass
