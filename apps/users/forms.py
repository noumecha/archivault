from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import *
from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.bootstrap import InlineRadios, PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from dal import autocomplete, forward
from django.template.loader import render_to_string


class LoginForm(AuthenticationForm):
    # Add any custom fields or modifications here
    pass

# users form
class UtilisateurForm(forms.ModelForm):
    class Meta:
        model = Utilisateur

        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
        )
        labels = {
            'username' : "login utilisateur",
            'first_name' : "Prenom utilisateur",
            'last_name' : "Nom utilisateur",
            'email' : "Email utilisateur",
        }
        
        widgets = {
            'Date_delivrance_cni'  :  forms.TextInput(attrs={'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        super(UtilisateurForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        self.helper =  FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(FloatingField("username"), css_class='overflow-hidden form-group col-md-12 mb-0'),
                Column(FloatingField("first_name"), css_class='overflow-hidden form-group col-md-12 mb-0'),
                Column(FloatingField("last_name"), css_class='overflow-hidden form-group col-md-12 mb-0'),
                Column(FloatingField("email"), css_class='overflow-hidden form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
        )