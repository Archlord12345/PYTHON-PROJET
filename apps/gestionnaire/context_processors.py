from django.conf import settings
from django.urls import NoReverseMatch, reverse


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
    """
    items = [
        {
            'id': 'dashboard',
            'label': 'Tableau de bord',
            'url': '/',
            'icon': 'grid_view',
        },
        {
            'id': 'caisse',
            'label': 'Caisse',
            'url': '/caisse/',
            'icon': 'shopping_cart',
        },
        {
            'id': 'articles',
            'label': 'Articles',
            'url': '/articles/',
            'icon': 'inventory_2',
        },
        {
            'id': 'clients',
            'label': 'Clients',
            'url': '/clients/',
            'icon': 'group',
        },
        {
            'id': 'reports',
            'label': 'Rapports',
            'url': '/report/',
            'icon': 'analytics',
        },
        {
            'id': 'settings',
            'label': 'Paramètres',
            'url': '/gestionnaire/',
            'icon': 'settings',
        },
    ]

    current_path = request.path or '/'
    for item in items:
        if item['url'] == '/':
            item['is_active'] = current_path == '/'
        else:
            item['is_active'] = current_path.startswith(item['url'])

    return {
        'sidebar_items': items,
        'login_url': _safe_reverse(['authentification:login', 'login']),
        'logout_url': _safe_reverse(['authentification:logout', 'logout']),
    }
