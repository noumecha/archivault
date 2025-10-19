from django import forms
from .models import *
from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column

# form for regle de classement
class RegleClassementsForm(forms.ModelForm):
    class Meta:
        model = RegleClassement

        fields = (
            'nom', 'description_regleclassement'
        )

        labels = {
            "niveau" : "Titre du niveau d'accès",
            "description_regleclassement" : "Description de la règle de classement",
        }

        widgets = {
            "description_regleclassement": forms.Textarea(attrs={'cols': '20', 'rows': '5'}),
        }

    def __init__(self, *args, **kwargs):
        super(RegleClassementsForm, self).__init__(*args, **kwargs)
        self.helper =  FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(FloatingField("nom"), css_class='form-group col-md-12 mb-0'),
                Column(FloatingField("description_regleclassement"), css_class='form-group col-md-12 mb-0'),
                css_class='form-row p-3 pt-0'
            )
        )

# form for nivea d'accès
class NiveauAccesDocumentsForm(forms.ModelForm):
    class Meta:
        model = NiveauAccesDocument

        fields = (
            'niveau',"description_niveauaccess"
        )

        labels = {
            "niveau" : "Titre du niveau d'accès",
            "description_niveauaccess" : "Description"
        }

        widgets = {

        }

    def __init__(self, *args, **kwargs):
        super(NiveauAccesDocumentsForm, self).__init__(*args, **kwargs)
        self.helper =  FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(FloatingField("niveau"), css_class='form-group col-md-12 mb-0'),
                Column(FloatingField("description_niveauaccess"), css_class='form-group col-md-12 mb-0'),
                css_class='form-row p-3 pt-0'
            ),
        )

# form for type Document
class TypeDocumentsForm(forms.ModelForm):
    class Meta:
        model = TypeDocument

        fields = (
            'libelle',"description_typedocument"
        )

        labels = {
            "libelle" : "Libellé du type de document",
            "description_typedocument" : "Description"
        }

        widgets = {

        }

    def __init__(self, *args, **kwargs):
        super(TypeDocumentsForm, self).__init__(*args, **kwargs)
        self.helper =  FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(FloatingField("libelle"), css_class='form-group col-md-12 mb-0'),
                Column(FloatingField("description_typedocument"), css_class='form-group col-md-12 mb-0'),
                css_class='form-row p-3 pt-0'
            ),
        )

# form for theme
class ThemesForm(forms.ModelForm):
    class Meta:
        model = Theme

        fields = (
            'libelle',
            "description_theme"
        )

        labels = {
            "libelle" : "Libellé du Thème",
            "description_theme" : "Description"
        }

        widgets = {

        }

    def __init__(self, *args, **kwargs):
        super(ThemesForm, self).__init__(*args, **kwargs)
        self.helper =  FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(FloatingField("libelle"), css_class='form-group col-md-12 mb-0'),
                Column(FloatingField("description_theme"), css_class='form-group col-md-12 mb-0'),
                css_class='form-row p-3 pt-0'
            ),
        )

# Sous Type Form
class SousTypeDocumentsForm(forms.ModelForm):
    class Meta:
        model = SousTypeDocument

        fields = (
            'libelle', 'type_document',
            "description_soustypedocument"
        )

        labels = {
            "libelle" : "Libellé du sour type",
            "description_soustypedocument" : "Description",
            "type_document" : "Type du Document",
        }

        widgets = {

        }

    def __init__(self, *args, **kwargs):
        super(SousTypeDocumentsForm, self).__init__(*args, **kwargs)
        self.helper =  FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(FloatingField("libelle"), css_class='form-group col-md-12 mb-0'),
                Column(FloatingField("description_soustypedocument"), css_class='form-group col-md-12 mb-0'),
                Column(FloatingField("type_document"), css_class="form-group col-md-12 mb-0 mt-1"),
                css_class='form-row p-3 pt-0'
            ),
        )

# form for document
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class UploadMultipleForm(forms.Form):
    """fichiers = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        required=False
    )"""
    fichiers =  MultipleFileField(label='Select files', required=False)
    # autres champs
    type_document = forms.ModelChoiceField(queryset=TypeDocument.objects.all(), required=False)
    sous_type = forms.ModelChoiceField(queryset=SousTypeDocument.objects.all(), required=False)
    theme = forms.ModelChoiceField(queryset=Theme.objects.all(), required=False)
    cellule = forms.ModelChoiceField(queryset=Cellule.objects.all(), required=False)
    etat = forms.ChoiceField(choices=EtatDocument.choices, required=False)
    niveau_acces = forms.ModelChoiceField(queryset=NiveauAccesDocument.objects.all(), required=False)
    profil_document = forms.ChoiceField(choices=ProfilDoc.choices, required=False)
    regles_classement = forms.ModelMultipleChoiceField(queryset=RegleClassement.objects.all(), required=False)
    metadonnees = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        widgets = {
            #'fichiers': forms.ClearableFileInput(attrs={'multiple': True}),
        }

        labels = {
            "type_document" : "Type du Document",
            "sous_type" : "sous type du Document",
            "theme" : "Thème du Document",
            "cellule" : "Cellule du Document",
            "niveau_acces" : "Niveau accès du Document",
            "profil_document" : "Profil du Document",
            "regles_classement" : "Rèlges de classemnt",
            "metadonnees" : "Métadonnées du Document",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fichiers'].widget.attrs.update({'multiple': True})
        self.fields['fichiers'].widget.allow_multiple_selected = True  # 👈 correction clé

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("fichiers", css_class="form-group col-md-12 mb-2"),
                Column(FloatingField("type_document"), css_class="form-group col-md-6 mb-2"),
                Column(FloatingField("sous_type"), css_class="form-group col-md-6 mb-2"),
                Column(FloatingField("theme"), css_class="form-group col-md-6 mb-2"),
                Column(FloatingField("cellule"), css_class="form-group col-md-6 mb-2"),
                Column(FloatingField("niveau_acces"), css_class="form-group col-md-6 mb-2"),
                Column(FloatingField("profil_document"), css_class="form-group col-md-6 mb-2"),
                Column(FloatingField("regles_classement"), css_class="form-group col-md-12 mb-2"),
                Column(FloatingField("metadonnees"), css_class="form-group col-md-12 mb-2"),
            )
        )


class DocumentsForm(forms.ModelForm):
    class Meta:
        model = Document

        fields = (
            "titre",
            "fichier",
            "type_document",
            "sous_type",
            "theme",
            "cellule",
            "etat",
            "niveau_acces",
            "profil_document",
            "regles_classement",
            "metadonnees",
            #"cree_par",
        )

        labels = {
            "titre" : "Titre du Document",
            "type_document" : "Type du Document",
            "sous_type" : "sous type du Document",
            "theme" : "Thème du Document",
            "cellule" : "Cellule du Document",
            "niveau_acces" : "Niveau accès du Document",
            "profil_document" : "Profil du Document",
            "regles_classement" : "Rèlges de classemnt",
            "metadonnees" : "Métadonnées du Document",
        }

        widgets = {

        }

    def __init__(self, *args, **kwargs):
        super(DocumentsForm, self).__init__(*args, **kwargs)
        self.helper =  FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(FloatingField("titre"), css_class='form-group col-md-12 mb-0'),
                Column("fichier", css_class="form-group col-md-12 mb-0 mt-1"),
                Column(FloatingField("type_document"), css_class="form-group col-md-6 mb-0 mt-1"),
                Column(FloatingField("sous_type"), css_class="form-group col-md-6 mb-0 mt-1"),
                Column(FloatingField("theme"), css_class="form-group col-md-6 mb-0 mt-1"),
                Column(FloatingField("cellule"), css_class="form-group col-md-6 mb-0 mt-1"),
                Column(FloatingField("niveau_acces"), css_class="form-group col-md-6 mb-0 mt-1"),
                Column(FloatingField("profil_document"), css_class="form-group col-md-6 mb-0 mt-1"),
                Column(FloatingField("regles_classement"), css_class="form-group col-md-12 mb-0 mt-1"),
                Column(FloatingField("metadonnees"), css_class="form-group col-md-12 mb-0 mt-1"),
                css_class='form-row p-3 pt-0'
            ),
        )
