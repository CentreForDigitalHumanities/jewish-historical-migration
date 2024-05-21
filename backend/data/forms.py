from django import forms


class ChoosePublicationIdentifierForm(forms.Form):
    identifier = forms.CharField()