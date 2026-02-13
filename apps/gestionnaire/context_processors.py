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
            'url': reverse('home'),
            'icon': 'grid_view',
        },
        {
            'id': 'caisse',
            'label': 'Caisse',
            'url': _safe_reverse(['caisse:index']),
            'icon': 'shopping_cart',
        },
        {
            'id': 'articles',
            'label': 'Articles',
            'url': _safe_reverse(['articles:liste_articles']),
            'icon': 'inventory_2',
        },
        {
            'id': 'clients',
            'label': 'Clients',
            'url': _safe_reverse(['clients:index', 'clients:liste_clients']),
            'icon': 'group',
        },
        {
            'id': 'reports',
            'label': 'Rapports',
            'url': _safe_reverse(['report:report', 'report:index']),
            'icon': 'analytics',
        },
        {
            'id': 'settings',
            'label': 'Paramètres',
            'url': _safe_reverse(['parametre:index']),
            'icon': 'settings',
        },
    ]

    current_path = request.path or '/'
    for item in items:
        item_url = item['url']
        if item_url == '/' or item_url == '#':
            item['is_active'] = current_path == '/'
        else:
            # Ensure we match the full path segment, not just partial starts
            # For example, /clients/ should match /clients/, /clients/create/, etc.
            # But /articles/ should NOT match /clients/
            if current_path.startswith(item_url):
                # Additional check: either exact match, or next char is /
                remaining = current_path[len(item_url):]
                item['is_active'] = remaining == '' or remaining.startswith('/')
            else:
                item['is_active'] = False

    return {
        'sidebar_items': items,
        'login_url': _safe_reverse(['authentification:login', 'login']),
        'logout_url': _safe_reverse(['authentification:logout', 'logout']),
    }
