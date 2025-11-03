from django import forms
from .models import *
from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.helper import FormHelper, Layout
from crispy_forms.layout import Layout, Row, Column, Field

class CellulesForm(forms.ModelForm):
    class Meta:
        model = Cellule

        fields = (
            "nom",
            "description_cellule",
            "division"
        )

        labels = {
            "nom" : "Nom de la Cellule",
            "description_cellule" : "Description de la Cellule",
            "division" : "Division correspondante"
        }

        widgets = {
            "description_cellule" : forms.Textarea,
        }

    def __init__(self, *args, **kwargs):
        super(CellulesForm, self).__init__(*args, **kwargs)
        self.helper =  FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(FloatingField("nom"), css_class='form-group col-md-12 mb-0'),
                Column(FloatingField("division"), css_class='form-group col-md-12 mb-0'),
                Column(FloatingField("description_cellule"), css_class='form-group col-md-12 mb-0'),
                css_class='form-row p-3 pt-0'
            ),
        )

class MinistereForm(forms.ModelForm):
    class Meta:
        model = Ministere

        fields = (
            "nom",
            "description_ministere",
            "abrevation",
            "code",
        )

        labels = {
            "nom" : "Nom de la Cellule",
            "description_ministere" : "Description du ministère",
        }

        widgets = {
            "description_ministere" : forms.Textarea(attrs={'rows': 5, 'col': 10}),
        }

    def __init__(self, *args, **kwargs):
        super(MinistereForm, self).__init__(*args, **kwargs)
        self.helper =  FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(FloatingField("nom"), css_class='form-group col-md-12 mb-0'),
                Column(FloatingField("description_ministere"), css_class='form-group col-md-12 mb-0'),
                css_class='form-row p-3 pt-0'
            ),
        )

class DirectionGeneraleForm(forms.ModelForm):
    class Meta:
        model = DirectionGenerale
        fields = (
            "nom",
            "description_direction_generale",
            "ministere"
        )
        labels = {
            "nom" : "Nom de la direction generale",
            "description_direction_generale" : "Description de la direction generale",
            "ministere" : "Ministere Correspndant"
        }
        widgets = {
            "description_direction_generale" : forms.Textarea(attrs={'rows': 5, 'col': 10}),
        }

    def __init__(self, *args, **kwargs):
        super(DirectionGeneraleForm, self).__init__(*args, **kwargs)
        self.helper =  FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(FloatingField("nom"), css_class='form-group col-md-12 mb-0'),
                Column(FloatingField("ministere"), css_class='form-group col-md-12 mb-0'),
                Column(FloatingField("description_direction_generale"), css_class='form-group col-md-12 mb-0'),
                css_class='form-row p-3 pt-0'
            ),
        )

class DivisionForm(forms.ModelForm):
    class Meta:
        model = Division

        fields = (
            "nom",
            "description_division",
            "ministere",
            "direction_generale"
        )

        labels = {
            "nom" : "Nom de la division",
            "description_division" : "Description de la Division",
            "ministere" : "Ministere Correspndant",
            "direction_generale" : "Direction generale correspondante"
        }

        widgets = {
            "description_division" : forms.Textarea(attrs={'rows': 5, 'col': 10}),
        }

    def __init__(self, *args, **kwargs):
        super(DivisionForm, self).__init__(*args, **kwargs)
        self.helper =  FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(FloatingField("nom"), css_class='form-group col-md-12 mb-0'),
                Column(FloatingField("description_division"), css_class='form-group col-md-12 mb-0'),
                Column(FloatingField("ministere"), css_class='form-group col-md-12 mb-0'),
                Column(FloatingField("direction_generale"), css_class='form-group col-md-12 mb-0'),
                css_class='form-row p-3 pt-0'
            ),
        )
