from django import forms
from .models import Configuration

BASE_INPUT_CLASS = (
    "w-full px-4 py-3 rounded-xl border border-zinc-300 text-zinc-900 "
    "placeholder:text-zinc-400 bg-white "
    "focus:border-green-500 focus:ring-2 focus:ring-green-500/20 transition-all "
    "dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100 dark:placeholder:text-zinc-500 "
    "dark:focus:border-green-500 dark:focus:ring-green-500/20"
)

class ConfigurationForm(forms.ModelForm):
    class Meta:
        model = Configuration
        fields = ['nom_magasin', 'description_accueil', 'adresse', 'telephone', 'email', 'tva_par_defaut', 'logo']
        widgets = {
            'nom_magasin': forms.TextInput(attrs={'class': BASE_INPUT_CLASS}),
            'description_accueil': forms.TextInput(attrs={'class': BASE_INPUT_CLASS}),
            'adresse': forms.Textarea(attrs={'class': BASE_INPUT_CLASS, 'rows': 3}),
            'telephone': forms.TextInput(attrs={'class': BASE_INPUT_CLASS}),
            'email': forms.EmailInput(attrs={'class': BASE_INPUT_CLASS}),
            'tva_par_defaut': forms.NumberInput(attrs={'class': BASE_INPUT_CLASS}),
            'logo': forms.ClearableFileInput(attrs={'class': BASE_INPUT_CLASS}),
        }
