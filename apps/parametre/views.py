from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Configuration
from .forms import ConfigurationForm

@login_required
def index(request):
    """Vue pour gérer les paramètres de l'application"""
    config = Configuration.objects.first()
    if not config:
        config = Configuration.objects.create()
    
    if request.method == 'POST':
        form = ConfigurationForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Paramètres mis à jour avec succès.")
            return redirect('parametre:index')
    else:
        form = ConfigurationForm(instance=config)
    
    return render(request, 'parametre/index.html', {
        'form': form,
        'config': config
    })
