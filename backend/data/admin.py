from django.contrib import admin
from django import forms
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from django_admin_search.admin import AdvancedSearchAdmin

from .forms import ChoosePublicationIdentifierForm
from .models import (
    Area, Region, Place, Record, PrimaryCategory, SecondaryCategory,
    Language, Script, Century, Publication
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
        'category2', 'period', 'inscriptions_count', 'publication'
    ]
    list_filter = [
        'area', 'region', 'estimated_centuries', 'languages', ('scripts', admin.RelatedOnlyFieldListFilter), 
        'category1', 'category2', 'sex_dedicator', 'sex_deceased', 'publication'
    ]
    list_select_related = ["place", "category1", "category2"]
    ordering = ['source']
    search_form = RecordSearchForm
    actions = ["add_publication_record"]

    @admin.action(description="Add publication record to records")
    def add_publication_record(self, request: HttpRequest, queryset: QuerySet["Record"]) -> HttpResponse:
        if "apply" in request.POST:
            form = ChoosePublicationIdentifierForm(request.POST)
            if form.is_valid():
                identifier = form.cleaned_data['identifier']
                publication_created = False
                try:
                    with transaction.atomic():
                        publication, publication_created = Publication.objects.get_or_create(identifier=identifier)
                        for record in queryset:
                            if not record.source.startswith(identifier):
                                raise RuntimeError(f"Not all sources of the selected records start with '{identifier}'.")
                            # Use the rest of the "source" attribute as the location within the publication
                            location = record.source[len(identifier):].strip()
                            record.location_in_publication = location
                            record.publication = publication
                            record.save()
                except RuntimeError as e:
                    form.add_error(None, str(e))
                else:
                    # Success
                    createdtext = "created and " if publication_created else ""
                    self.message_user(request, f"Publication record {createdtext}added to {queryset.count()} records.")
                    return HttpResponseRedirect(request.get_full_path())


        else:
            form = ChoosePublicationIdentifierForm()
        return render(
            request,
            "data/add_publication_record.html",
            {"records": queryset, "form": form}
        )


admin.site.register(PrimaryCategory)
admin.site.register(SecondaryCategory)
admin.site.register(Language)
admin.site.register(Script)
admin.site.register(Century)
admin.site.register(Publication)
