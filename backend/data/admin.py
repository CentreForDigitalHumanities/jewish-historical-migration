from django.contrib import admin

from .models import Area, Region, PleiadesPlace, CustomPlace


@admin.register(CustomPlace)
class CustomPlaceAdmin(admin.ModelAdmin):
    pass


@admin.action(description="Fetch information from Pleiades")
def fetch_from_pleiades(modeladmin, request, queryset):
    for item in queryset:
        item.fetch_from_pleiades()
        item.save()


@admin.register(PleiadesPlace)
class PleiadesPlaceAdmin(admin.ModelAdmin):
    actions = [fetch_from_pleiades]


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    pass


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    pass
