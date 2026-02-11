"""
Configuration et paramètres du module articles
"""

# Catégories d'articles
CATEGORIES = [
    ('boulangerie', 'Boulangerie'),
    ('produits_laitiers', 'Produits laitiers'),
    ('fruits_legumes', 'Fruits et légumes'),
    ('viande', 'Viande'),
    ('epicerie', 'Épicerie'),
    ('boissons', 'Boissons'),
]

# Unités de mesure
UNITE_MESURE = [
    ('unite', 'Unité'),
    ('kg', 'Kilogramme'),
    ('litre', 'Litre'),
]

# Taux de TVA par défaut
TVA_DEFAULT = 5.5

# Configuration de stock
STOCK_CONFIG = {
    'MINIMUM_DEFAULT': 5,
    'ALERT_THRESHOLD': 0.3,  # 30% du minimum
}

# Configuration d'export/import
IMPORT_EXPORT_CONFIG = {
    'MAX_FILE_SIZE': 5 * 1024 * 1024,  # 5 MB
    'CHARSET': 'utf-8',
    'ALLOWED_FORMATS': ['csv'],
}

# Configuration de pagination
PAGINATION = {
    'ARTICLES_PER_PAGE': 25,
}

# Messages
MESSAGES = {
    'ARTICLE_CREATED': 'Article créé avec succès',
    'ARTICLE_UPDATED': 'Article modifié avec succès',
    'ARTICLE_DELETED': 'Article supprimé avec succès',
    'IMPORT_SUCCESS': '{count} article(s) importé(s)',
    'IMPORT_ERROR': 'Erreur lors de l\'import',
}

# Validations
VALIDATIONS = {
    'CODE_BARRES_LENGTH': 13,
    'NOM_MAX_LENGTH': 200,
    'PRICE_DECIMAL_PLACES': 2,
    'PRICE_MAX_DIGITS': 10,
}
