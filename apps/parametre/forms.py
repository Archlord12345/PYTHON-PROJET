from django import forms
from .models import Configuration

class ConfigurationForm(forms.ModelForm):
    class Meta:
        model = Configuration
        fields = ['nom_magasin', 'adresse', 'telephone', 'email', 'tva_par_defaut', 'logo']
        widgets = {
            'nom_magasin': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-zinc-200 focus:border-green-500 focus:ring-green-500 transition-all bg-white/50'}),
            'adresse': forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-xl border-zinc-200 focus:border-green-500 focus:ring-green-500 transition-all bg-white/50', 'rows': 3}),
            'telephone': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-zinc-200 focus:border-green-500 focus:ring-green-500 transition-all bg-white/50'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-zinc-200 focus:border-green-500 focus:ring-green-500 transition-all bg-white/50'}),
            'tva_par_defaut': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-zinc-200 focus:border-green-500 focus:ring-green-500 transition-all bg-white/50'}),
            'logo': forms.FileInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-zinc-200 focus:border-green-500 focus:ring-green-500 transition-all bg-white/50'}),
        }
