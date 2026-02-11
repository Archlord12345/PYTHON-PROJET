from django.contrib import admin
from facturation.models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('code_barres', 'nom', 'categorie', 'prix_HT', 'prix_TTC', 'stock_actuel', 'actif')
    list_filter = ('categorie', 'actif')
    search_fields = ('code_barres', 'nom', 'description')
    readonly_fields = ()
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('code_barres', 'nom', 'description', 'categorie', 'unite_mesure', 'actif')
        }),
        ('Tarification', {
            'fields': ('prix_HT', 'prix_TTC', 'taux_TVA')
        }),
        ('Stock', {
            'fields': ('stock_actuel', 'stock_minimum')
        }),
    )
