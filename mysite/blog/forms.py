from django import forms
from .models import Cities_maps

class SearchRoute(forms.Form):

    city_from = forms.CharField(label="Виберіть своє місто", widget=forms.TextInput(), required=False)
    city_to = forms.MultipleChoiceField(label="Виберіть міста товару", widget=forms.CheckboxSelectMultiple,choices=[
            ("Трускавець", "Трускавець"),
            ("Сокаль", "Сокаль"),
            ("Червоноград", "Червоноград"),
        ], required=False)