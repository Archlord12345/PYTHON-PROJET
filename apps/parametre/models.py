from django.db import models

class Configuration(models.Model):
    nom_magasin = models.CharField(max_length=255, default="Caisse Plus")
    description_accueil = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default="L'intelligence au service de votre point de vente.",
    )
    adresse = models.TextField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    tva_par_defaut = models.DecimalField(max_digits=5, decimal_places=2, default=20.0)
    logo = models.ImageField(upload_to='branding/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Configuration"
        verbose_name_plural = "Configurations"

    def __str__(self):
        return self.nom_magasin
