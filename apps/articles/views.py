from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from urllib.parse import urlencode
from django.views.decorators.http import require_GET
from facturation.models import Article
from .forms import ArticleFormCreate, ArticleFormEdit
from .services import ArticleService
from apps.gestionnaire.decorators import gestionnaire_required


@login_required
@gestionnaire_required
@require_GET
def dashboard(request):
    """Affiche le dashboard avec statistiques"""
    stats = ArticleService.get_statistics()
    low_stock_articles = ArticleService.get_articles_low_stock()[:5]
    
    context = {
        'stats': stats,
        'low_stock_articles': low_stock_articles,
    }
    
    return render(request, 'articles/dashboard.html', context)


@login_required
@gestionnaire_required
def liste_articles(request):
    """Affiche la liste des articles avec filtres"""
    articles = Article.objects.all()
    
    # Filtrage par recherche (nom ou code-barres)
    search = request.GET.get('search', '')
    if search:
        articles = articles.filter(
            Q(nom__icontains=search) | Q(code_barres__icontains=search)
        )
    
    # Filtrage par catégorie
    categorie = request.GET.get('categorie', '')
    if categorie:
        articles = articles.filter(categorie=categorie)
    
    # Filtrer les inactifs
    show_inactive = request.GET.get('show_inactive', '0') == '1'
    if not show_inactive:
        articles = articles.filter(actif=True)
    
    # Tri
    sort_by = request.GET.get('sort', 'nom')
    order = request.GET.get('order', 'asc')
    
    valid_sort_fields = {
        'code_barres': 'code_barres',
        'nom': 'nom',
        'categorie': 'categorie',
        'prix': 'prix_HT',
        'stock': 'stock_actuel',
    }
    
    db_field = valid_sort_fields.get(sort_by, 'nom')
    if order == 'desc':
        db_field = '-' + db_field
        
    articles = articles.order_by(db_field)

    # Pagination
    page_sizes = [10, 25, 50]
    page_size_raw = request.GET.get('page_size', '10')
    try:
        page_size = int(page_size_raw)
    except ValueError:
        page_size = 10
    if page_size not in page_sizes:
        page_size = 10
    paginator = Paginator(articles, page_size)
    page_obj = paginator.get_page(request.GET.get('page'))

    def build_query(**overrides):
        params = request.GET.copy()
        for key, value in overrides.items():
            if value is None:
                params.pop(key, None)
            else:
                params[key] = str(value)
        return urlencode(params, doseq=True)

    sort_urls = {}
    for key in valid_sort_fields.keys():
        next_order = 'desc' if (sort_by == key and order == 'asc') else 'asc'
        sort_urls[key] = f"?{build_query(sort=key, order=next_order, page=1)}"
    
    # Comptage
    total_articles = Article.objects.count()
    stats = ArticleService.get_statistics()
    
    context = {
        'articles': page_obj.object_list,
        'page_obj': page_obj,
        'total_articles': total_articles,
        'search': search,
        'categorie': categorie,
        'categorie_choices': Article.CATEGORIE_CHOICES,
        'stats': stats,
        'show_inactive': show_inactive,
        'sort_by': sort_by,
        'order': order,
        'sort_urls': sort_urls,
        'page_sizes': page_sizes,
        'current_page_size': page_size,
    }
    
    return render(request, 'articles/liste_articles.html', context)


@login_required
@gestionnaire_required
def creer_article(request):
    """Crée un nouvel article"""
    if request.method == 'POST':
        form = ArticleFormCreate(request.POST)
        if form.is_valid():
            article = form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Article créé avec succès',
                    'article_id': article.id
                })
            return redirect('articles:liste_articles')
    else:
        form = ArticleFormCreate()
    
    return render(request, 'articles/creer_article.html', {'form': form})


@login_required
@gestionnaire_required
def editer_article(request, pk):
    """Édite un article existant"""
    article = get_object_or_404(Article, pk=pk)
    
    if request.method == 'POST':
        form = ArticleFormEdit(request.POST, instance=article)
        if form.is_valid():
            article = form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Article modifié avec succès'
                })
            return redirect('articles:liste_articles')
    else:
        form = ArticleFormEdit(instance=article)
    
    return render(request, 'articles/editer_article.html', {
        'form': form,
        'article': article
    })


@login_required
@gestionnaire_required
def supprimer_article(request, pk):
    """Supprime un article"""
    article = get_object_or_404(Article, pk=pk)
    
    if request.method == 'POST':
        article.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Article supprimé'})
        return redirect('articles:liste_articles')
    
    return render(request, 'articles/confirmer_suppression.html', {'article': article})


@login_required
@gestionnaire_required
def supprimer_tout_articles(request):
    """Supprime tous les articles du catalogue"""
    if request.method == 'POST':
        count = Article.objects.count()
        Article.objects.all().delete()
        messages.success(request, f'{count} articles ont été supprimés du catalogue.')
        return redirect('articles:liste_articles')
    return redirect('articles:liste_articles')


@login_required
@gestionnaire_required
def importer_articles(request):
    """Importe les articles depuis un fichier CSV"""
    import csv
    import io
    
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        try:
            if not csv_file.name.endswith('.csv'):
                return render(request, 'articles/importer_articles.html', {
                    'error': 'Le fichier doit être au format CSV'
                })
            
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            imported_count = 0
            errors = []
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Vérifier les champs requis
                    if not all([row.get('Code-barres'), row.get('Nom'), 
                               row.get('Prix HT'), row.get('Prix TTC')]):
                        errors.append(f"Ligne {row_num}: Champs requis manquants")
                        continue
                    
                    def clean_float(val):
                        if not val: return 0.0
                        return float(str(val).replace(',', '.').strip())

                    # Créer ou mettre à jour l'article
                    article, created = Article.objects.update_or_create(
                        code_barres=row.get('Code-barres', '').strip(),
                        defaults={
                            'nom': row.get('Nom', '').strip(),
                            'description': row.get('Description', '').strip(),
                            'prix_HT': clean_float(row.get('Prix HT', 0)),
                            'prix_TTC': clean_float(row.get('Prix TTC', 0)),
                            'taux_tva': clean_float(row.get('TVA', 5.5)) / 100,
                            'categorie': row.get('Catégorie', 'Epicerie').strip(),
                            'unite_mesure': row.get('Unité', 'Unite').strip(),
                            'stock_actuel': int(float(str(row.get('Stock actuel', 0)).replace(',', '.'))),
                            'stock_minimum': int(float(str(row.get('Stock minimum', 5)).replace(',', '.'))),
                            'actif': row.get('Actif', 'Oui').strip().lower() in ['oui', 'yes', '1', 'true', 'active'],
                        }
                    )
                    imported_count += 1
                    
                except (ValueError, KeyError) as e:
                    errors.append(f"Ligne {row_num}: Erreur de format - {str(e)}")
                except Exception as e:
                    errors.append(f"Ligne {row_num}: {str(e)}")
            
            message = f"{imported_count} article(s) importé(s) avec succès"
            if errors:
                message += f" (avec {len(errors)} erreur(s))"
            
            context = {
                'success': True,
                'message': message,
                'imported_count': imported_count,
                'errors': errors,
            }
            return render(request, 'articles/importer_articles.html', context)
            
        except Exception as e:
            return render(request, 'articles/importer_articles.html', {
                'error': f'Erreur lors de la lecture du fichier: {str(e)}'
            })
    
    return render(request, 'articles/importer_articles.html')


@login_required
@gestionnaire_required
def export_articles(request):
    """Exporte les articles en CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="articles.csv"'
    response.write('\ufeff')  # BOM pour Excel
    
    writer = csv.writer(response)
    writer.writerow([
        'Code-barres', 'Nom', 'Description', 'Prix HT', 'Prix TTC',
        'TVA', 'Catégorie', 'Unité', 'Stock actuel', 'Stock minimum', 'Actif'
    ])
    
    for article in Article.objects.all():
        writer.writerow([
            article.code_barres,
            article.nom,
            article.description,
            article.prix_HT,
            article.prix_TTC,
            article.taux_tva,
            article.get_categorie_display(),
            article.get_unite_mesure_display(),
            article.stock_actuel,
            article.stock_minimum,
            'Oui' if article.actif else 'Non'
        ])
    
    return response
