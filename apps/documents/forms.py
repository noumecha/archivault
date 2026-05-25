from django import forms
from .models import *
from apps.users.models import RoleUtilisateur, Utilisateur
from crispy_bootstrap5.bootstrap5 import FloatingField, Field
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from dal import autocomplete
from config.roles import *

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
            'libelle',"description_typedocument","parent_type","cellule"
        )

        labels = {
            "libelle" : "Libellé du type de document",
            "description_typedocument" : "Description",
            "cellule" : "Unité de gestion Correspondante",
            "parent_type" : "Type de document parent (relation de dépendance entre type)"
        }

        widgets = {

        }

    def __init__(self, *args, cellule=None, **kwargs):
        super(TypeDocumentsForm, self).__init__(*args, **kwargs)
        # management :
        if cellule:
            print("Initialising TypeDocumentsForm with cellule:", cellule)
            self.fields["cellule"].initial = cellule
            self.fields["cellule"].disabled = True
            self._forced_cellule = cellule
        self.helper =  FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(FloatingField("libelle"), css_class='form-group col-md-12 mb-0'),
                Column(FloatingField("description_typedocument"), css_class='form-group col-md-12 mb-0'),
                Column(FloatingField("cellule"), css_class='form-group col-md-12 mb-0'),
                Column(FloatingField("parent_type"), css_class='form-group col-md-12 mb-0'),
                css_class='form-row p-3 pt-0'
            ),
        )

    def save(self, commit=True):
        obj = super().save(commit=False)

        if hasattr(self, "_forced_cellule"):
            obj.cellule = self._forced_cellule

        if commit:
            obj.save()
        return obj

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
            "description_soustypedocument" : forms.Textarea(attrs={'rows': 5, 'col': 10}),
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
    fichiers =  MultipleFileField(label='Selectionner un ou plusieurs fichiers...', required=False)
    # autres champs
    type_document = forms.ModelChoiceField(queryset=TypeDocument.objects.all(), required=False)
    sous_type = forms.ModelChoiceField(queryset=SousTypeDocument.objects.all(), required=False)
    theme = forms.ModelChoiceField(queryset=Theme.objects.all(), required=False)
    cellule = forms.ModelChoiceField(queryset=Cellule.objects.filter(division__statut=True), required=False)
    etat = forms.ChoiceField(choices=EtatDocument.choices, required=False)
    niveau_acces = forms.ChoiceField(choices=NiveauAcces.choices, required=False)
    profil_document = forms.ChoiceField(choices=ProfilDoc.choices, required=False)
    metadonnees = forms.CharField(widget=forms.Textarea, required=False)
    responsable_document = forms.ModelChoiceField(queryset=Utilisateur.objects.filter(role='responsable'), required=False)

    class Meta:
        model = Document

        fields = ()

        widgets = {
            'type_document': autocomplete.ModelSelect2(url='documents:typedocument_autocomplete'),
            'sous_type': autocomplete.ModelSelect2(url='documents:soustypedocument_autocomplete'),
        }

        labels = {
            "type_document" : "Type du Document",
            "sous_type" : "Sous type du Document",
            "theme" : "Thème du Document",
            "cellule" : "Unité de traitement",
            "niveau_acces" : "Niveau accès du Document",
            "profil_document" : "Profil du Document",
            "regles_classement" : "Rèlges de classemnt",
            "metadonnees" : "Métadonnées du Document",
            'responsable_document' : "Responsable",
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if not user:
            return
        # ADMIN / SUPERADMIN
        if is_superadmin(user) or is_admin(user):
            return
        # SUPERVISEUR
        if is_superviseur(user):
            self.fields["cellule"].queryset = Cellule.objects.filter(id=user.cellule_id)
            self.fields["cellule"].initial = user.cellule
            self.fields["cellule"].disabled = True
            self.fields["type_document"].queryset = TypeDocument.objects.filter(cellule=user.cellule)
            self.fields["sous_type"].queryset = SousTypeDocument.objects.filter(
                type_document__cellule=user.cellule
            )
            self.fields["responsable_document"].queryset = Utilisateur.objects.filter(cellule=user.cellule)
        # RESPONSABLE
        if is_responsable(user):
            self.fields["cellule"].queryset = Cellule.objects.filter(id=user.cellule_id)
            self.fields["cellule"].initial = user.cellule
            self.fields["cellule"].disabled = True
            self.fields["type_document"].queryset = TypeDocument.objects.filter(cellule=user.cellule)
            self.fields["sous_type"].queryset = SousTypeDocument.objects.filter(
                type_document__cellule=user.cellule
            )
            self.fields["theme"].queryset = Theme.objects.filter(cellule=user.cellule)
            self.fields["responsable_document"].queryset = Utilisateur.objects.filter(role='responsable')
            self.fields["responsable_document"].initial = user
            self.fields["responsable_document"].disabled = True
        self.fields['fichiers'].widget.attrs.update({'multiple': True})
        self.fields['fichiers'].widget.allow_multiple_selected = True
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
                Column(FloatingField("responsable_document"), css_class="form-group col-md-12 mb-2"),
            )
        )

# edit document form
class DocumentsForm(forms.ModelForm):
    class Meta:
        model = Document

        fields = (
            "titre",
            "type_document",
            "sous_type",
            "theme",
            "cellule",
            "etat",
            "niveau_acces",
            "profil_document",
            "metadonnees",
            'responsable_document',
            'parent',
            'bailleur',
            'avenant'
        )

        labels = {
            "titre" : "Titre du Document",
            "type_document" : "Type du Document",
            "sous_type" : "sous type du Document",
            "theme" : "Thème du Document",
            "cellule" : "Unité de traitement",
            "etat" : "Définir l'état du document",
            "niveau_acces" : "Niveau accès du Document",
            "profil_document" : "Profil du Document",
            "metadonnees" : "Métadonnées du Document",
            'responsable_document' : "Responsable",
            "bailleur" : "Ajouter eventuellement un bailleur",
            "avenant" : "Ajouter eventuellement un avenant",
            "parent" : "Parent (relation de dépendance entre documents)"
        }

        widgets = {
            "metadonnees" : forms.Textarea(attrs={'rows': 5, 'col': 10}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super(DocumentsForm, self).__init__(*args, **kwargs)
        cellule = self.instance.cellule if self.instance.pk else None
        accepte_bailleurs = cellule and cellule.accepte_bailleurs
        if not accepte_bailleurs:
            self.fields.pop("bailleur")
            self.fields.pop("avenant")
        self.helper =  FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(FloatingField("titre"), css_class='form-group col-md-12 mb-0'),
                Column(FloatingField("type_document"), css_class="form-group col-md-6 mb-0 mt-1"),
                Column(FloatingField("sous_type"), css_class="form-group col-md-6 mb-0 mt-1"),
                Column(FloatingField("theme"), css_class="form-group col-md-6 mb-0 mt-1"),
                Column(FloatingField("cellule"), css_class="form-group col-md-6 mb-0 mt-1"),
                Column(FloatingField("etat"), css_class="form-group col-md-6 mb-0 mt-1"),
                Column(FloatingField("niveau_acces"), css_class="form-group col-md-6 mb-0 mt-1"),
                Column(FloatingField("profil_document"), css_class="form-group col-md-6 mb-0 mt-1"),
                Column(FloatingField("responsable_document"), css_class="form-group col-md-6 mb-2"),
                Column(FloatingField("parent"), css_class="form-group col-md-12 mb-2"),
                Column(FloatingField("metadonnees"), css_class="form-group col-md-12 mb-0 mt-1"),
                css_class='form-row p-3 pt-0'
            )
        )
        if accepte_bailleurs:
            self.helper.layout.append(
                Row(
                    Column(FloatingField("bailleur"), css_class="col-md-6"),
                    Column(FloatingField("avenant"), css_class="col-md-6"),
                    css_class='form-row p-3 pt-0'
                )
            )
        self.helper.layout.append(
            Row(
                Column(
                    Submit("submit", "Enregistrer les modifications", css_class="btn btn-outline-primary"),
                    css_class="form-group col-md-12 mb-0"
                ),
                css_class='form-row p-3 pt-0'
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        type_doc = cleaned_data.get("type_document")
        cellule = cleaned_data.get("cellule")

        if cellule and not cellule.accepte_bailleurs:
            cleaned_data["bailleur"] = None
            cleaned_data["avenant"] = None

        if type_doc.libelle == "convention":
            if not self.cleaned_data.get("bailleur"):
                raise forms.ValidationError({"bailleur": "Un bailleur est requis pour une convention."})

        if type_doc.libelle == "aide-memoire":
            if not self.cleaned_data.get("parent"):
                raise forms.ValidationError({"parent": "Un aide-mémoire doit être rattaché à une convention."})

            if self.cleaned_data["parent"].type_document.libelle != "convention":
                raise forms.ValidationError("L’aide-mémoire doit être attaché à une convention.")

        if type_doc.libelle == "rapport":
            if not self.cleaned_data.get("parent"):
                raise forms.ValidationError({"parent": "Un rapport doit être lié à un aide-mémoire."})

            if self.cleaned_data["parent"].type_document.libelle != "aide-memoire":
                raise forms.ValidationError("Un rapport doit dépendre d'un aide-mémoire.")


class VersionDocumentForm(forms.ModelForm):
    class Meta:
        model = VersionDocument

        fields = (
            "titre",
            "document",
            "numero_version",
            "fichier",
            "responsable_version"
        )

        labels = {
            "titre" : "Titre de la version",
            "document" : "Document correspondant",
            "numero_version" : "Numero de version",
            "fichier" : "Fichier",
            "responsable_version": "Responsable de la version"
        }

        widgets = {

        }

        def __init__(self, *args, **kwargs):
            super(VersionDocumentForm, self).__init__(*args, **kwargs)
            self.helper =  FormHelper()
            self.helper.layout = Layout(
                Row(
                    Column(FloatingField("titre"), css_class='form-group col-md-12 mb-0'),
                    Column(FloatingField("document"), css_class='form-group col-md-12 mb-0'),
                    Column("fichier", css_class="form-group col-md-12 mb-0 mt-1"),
                    Column(FloatingField("responsable_version"), css_class="form-group col-md-12 mb-2"),
                    css_class='form-row p-3 pt-0'
                ),
            )

class BailleursFrom(forms.ModelForm):
    class Meta:
        model = Bailleurs

        fields = (
            "abrevation",
            "libelle",
            "description",
            "cellule",
        )

        labels = {
            "abrevation" : "Abréviation du bailleur",
            "libelle" : "Nom du bailleur",
            "description" : "Description du bailleur",
            "cellule" : "Unité de traitement",
        }

        widgets = {

        }

    def __init__(self, *args, **kwargs):
        super(BailleursFrom, self).__init__(*args, **kwargs)
        self.fields['cellule'].queryset = Cellule.objects.filter(accepte_bailleurs=True)
        if not self.fields["cellule"].queryset.exists():
            self.fields["cellule"].help_text = (
                "Aucune unité de traitement n'accepte les bailleurs."
            )
        self.helper =  FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(FloatingField("abrevation"), css_class='form-group col-md-12 mb-0'),
                Column(FloatingField("libelle"), css_class='form-group col-md-12 mb-0'),
                Column(FloatingField("cellule"), css_class="form-group col-md-12 mb-0 mt-1"),
                Column(FloatingField("description"), css_class="form-group col-md-12 mb-2"),
                css_class='form-row p-3 pt-0'
            ),
        )

class AvenantsForm(forms.ModelForm):
    class Meta:
        model = Avenants

        fields = (
            "bailleur",
            "libelle",
            "numero",
        )

        labels = {
            "bailleur" : "Selectionnez le bailleur",
            "libelle" : "Libellé de l'avenant",
            "numero" : "Numéro de l'avenant",
        }

        widgets = {

        }

        def __init__(self, *args, **kwargs):
            super(AvenantsForm, self).__init__(*args, **kwargs)
            self.helper =  FormHelper()
            self.helper.layout = Layout(
                Row(
                    Column(FloatingField("bailleur"), css_class='form-group col-md-12 mb-0'),
                    Column(FloatingField("libelle"), css_class='form-group col-md-12 mb-0'),
                    Column(FloatingField("numero"), css_class="form-group col-md-12 mb-2"),
                    css_class='form-row p-3 pt-0'
                ),
            )
