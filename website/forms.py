from django import forms
from django.core.validators import FileExtensionValidator
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .models import *

def file_size(value): 
    limit = 10 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('Veuillez limiter la taille du fichier à 10 Mo.')
    
class UploadFileForm(forms.Form):
    file = forms.FileField(
        label='Choisissez un fichier',
        help_text='max. 10 Mo',
        validators=[file_size, FileExtensionValidator(['pdf'], "Le fichier attendu est au format pdf")]
    )


class ContactForm(forms.Form):
    Nom = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Votre nom", 'class': 'form-group'}), 
                          label="Nom")
    Email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Votre e-mail", 'class': 'form-group'}),
        error_messages={"invalid": "Veuillez renseigner une adresse email correcte"},
        label="Email"
    )
    Objet = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Objet", 'class': 'form-group'}), required=False, label="Objet")
    Message = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "Votre message", 'class': 'form-group'}),
        label="Message"
    )