def sidebar_context(request):
    """
    Contexte personnalisé pour la barre latérale
    """
    sidebar_items = [
        {
            'title': 'Caisse',
            'icon': 'point_of_sale',
            'url': 'caisse:index',
            'app': 'caisse',
        },
        {
            'title': 'Phone',
            'icon': 'phone',
            'url': 'phone:index',
            'app': 'phone',
        },
        {
            'title': 'Authentification',
            'icon': 'login',
            'url': 'authentification:login',
            'app': 'authentification',
        },
    ]

    # Filtrer les éléments en fonction des permissions
    if hasattr(request, 'user'):
        sidebar_items = [
            item for item in sidebar_items 
            if 'permission' not in item or request.user.has_perm(item['permission'])
        ]

    return {
        'sidebar_items': sidebar_items,
        'current_app': request.resolver_match.app_name if hasattr(request, 'resolver_match') and request.resolver_match else None,
    }
