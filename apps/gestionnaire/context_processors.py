from django.urls import NoReverseMatch, reverse
from apps.parametre.models import Configuration


def _safe_reverse(candidates, fallback="#"):
    for name in candidates:
        try:
            return reverse(name)
        except NoReverseMatch:
            continue
    return fallback

def sidebar_context(request):
    """
    Context processor for the sidebar.
    Filtre les éléments selon le rôle de l'utilisateur.
    """
    # Déterminer le rôle de l'utilisateur
    user_role = getattr(request.user, 'role', None) if request.user.is_authenticated else None
    
    # Tous les éléments de navigation
    all_items = [
        {
            'id': 'dashboard',
            'label': 'Tableau de bord',
            'url': _safe_reverse(['gestionnaire:dashboard', 'home']),
            'icon': 'grid_view',
            'roles': ['all'],  # Accessible à tous
        },
        {
            'id': 'caisse',
            'label': 'Caisse',
            'url': _safe_reverse(['caisse:index']),
            'icon': 'shopping_cart',
            'roles': ['all'],  # Accessible à tous
        },
        {
            'id': 'articles',
            'label': 'Articles',
            'url': _safe_reverse(['articles:liste_articles']),
            'icon': 'inventory_2',
            'roles': ['Gestionnaire'],
        },
        {
            'id': 'clients',
            'label': 'Clients',
            'url': _safe_reverse(['clients:index', 'clients:liste_clients']),
            'icon': 'group',
            'roles': ['Gestionnaire'],
        },
        {
            'id': 'reports',
            'label': 'Rapports',
            'url': _safe_reverse(['report:report', 'report:index']),
            'icon': 'analytics',
            'roles': ['Gestionnaire'],
        },
        {
            'id': 'users',
            'label': 'Utilisateurs',
            'url': _safe_reverse(['utilisateurs:index']),
            'icon': 'manage_accounts',
            'roles': ['Gestionnaire'],
        },
        {
            'id': 'settings',
            'label': 'Paramètres',
            'url': _safe_reverse(['parametre:index']),
            'icon': 'settings',
            'roles': ['Gestionnaire'],
        },
    ]
    
    # Filtrer les éléments selon le rôle
    items = []
    for item in all_items:
        if 'all' in item['roles'] or user_role in item['roles']:
            items.append(item)

    current_path = request.path or '/'
    for item in items:
        item_url = item['url']
        if item_url == '/' or item_url == '#':
            item['is_active'] = current_path == '/'
        else:
            if current_path.startswith(item_url):
                remaining = current_path[len(item_url):]
                item['is_active'] = remaining == '' or remaining.startswith('/')
            else:
                item['is_active'] = False

    try:
        config = Configuration.objects.first()
    except Exception:
        config = None
    store_name = (config.nom_magasin if config and config.nom_magasin else "Caisse Plus")
    store_description = (
        config.description_accueil
        if config and config.description_accueil
        else "L'intelligence au service de votre point de vente."
    )
    store_logo_url = config.logo.url if config and config.logo else None

    return {
        'sidebar_items': items,
        'login_url': _safe_reverse(['authentification:login', 'login']),
        'logout_url': _safe_reverse(['authentification:logout', 'logout']),
        'user_role': user_role,
        'store_name': store_name,
        'store_description': store_description,
        'store_logo_url': store_logo_url,
    }
