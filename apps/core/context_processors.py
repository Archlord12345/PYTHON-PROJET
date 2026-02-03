def sidebar_context(request):
    """
    Contexte personnalisé pour la barre latérale
    """
    sidebar_items = [
        {
            'title': 'Tableau de bord',
            'icon': 'dashboard',
            'url': 'dashboard:index',
            'app': 'dashboard',
        },
        {
            'title': 'Caisse',
            'icon': 'point_of_sale',
            'url': 'checkout:index',
            'app': 'checkout',
        },
        {
            'title': 'Articles',
            'icon': 'inventory_2',
            'url': 'handle_articles:index',
            'app': 'handle_articles',
        },
        {
            'title': 'Clients',
            'icon': 'group',
            'url': 'handle_customers:index',
            'app': 'handle_customers',
        },
        {
            'title': 'Utilisateurs',
            'icon': 'manage_accounts',
            'url': 'handle_users:index',
            'app': 'handle_users',
            'permission': 'auth.view_user',
        },
        {
            'title': 'Journal d\'audit',
            'icon': 'history',
            'url': 'audit_journal:index',
            'app': 'audit_journal',
            'permission': 'audit_journal.view_auditlog',
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
