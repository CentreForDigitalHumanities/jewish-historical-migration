import tempfile

from django.contrib import admin
from django import forms
from django.http import HttpResponse

from django_admin_search.admin import AdvancedSearchAdmin

from .geojson import export_geojson
from .models import (
    Area, Region, Place, Record, PrimaryCategory, SecondaryCategory,
    Language, Script, Century
)


class RecordSearchForm(forms.Form):
    source = forms.CharField(required=False, widget=forms.TextInput(
        attrs={ 
            'filter_method': '__icontains',
        }
    ))
    place = forms.CharField(required=False, widget=forms.TextInput(
        attrs={ 
            'filter_method': '__name__icontains',
        }
    ))
    mentioned_placenames = forms.CharField(required=False, widget=forms.TextInput(
        attrs={ 
            'filter_method': '__icontains',
        }
    ))
    religious_profession = forms.CharField(required=False, widget=forms.TextInput(
        attrs={ 
            'filter_method': '__icontains',
        }
    ))
    symbol = forms.CharField(required=False, widget=forms.TextInput(
        attrs={ 
            'filter_method': '__icontains',
        }
    ))


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
class RecordAdmin(AdvancedSearchAdmin):
    list_display = [
        'source', 'area', 'region', 'place', 'category1', 
        'category2', 'period', 'inscriptions_count'
    ]
    list_filter = [
        'area', 'region', 'estimated_centuries', 'languages', ('scripts', admin.RelatedOnlyFieldListFilter), 
        'category1', 'category2', 'sex_dedicator', 'sex_deceased'
    ]
    list_select_related = ["place", "category1", "category2"]
    ordering = ['source']
    search_form = RecordSearchForm


admin.site.register(PrimaryCategory)
admin.site.register(SecondaryCategory)
admin.site.register(Language)
admin.site.register(Script)
admin.site.register(Century)
