// Cart state
let cart = [];
let nextItemId = 1;
let lastSearchResults = []; // Stockage temporaire des derniers résultats de recherche
let discount = {
    type: null, // 'percent' | 'amount'
    value: 0,
    amount: 0
};

// Initialize
document.addEventListener('DOMContentLoaded', function () {
    setupEventListeners();
    setupKeyboardShortcuts();
    updateCart();
});

// Event Listeners
function setupEventListeners() {
    const searchInput = document.getElementById('searchInput');
    const modalSearchInput = document.getElementById('modalSearchInput');

    // Barre de recherche principale (scan direct)
    searchInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            searchArticleByBarcode(e.target.value);
            e.target.value = '';
        }
    });

    // Ajouter effet de flou quand le champ est focus
    searchInput.addEventListener('focus', function () {
        document.body.classList.add('search-active');
    });

    searchInput.addEventListener('blur', function () {
        document.body.classList.remove('search-active');
    });

    // Barre de recherche dans la fenêtre modale (avec délai/debounce)
    modalSearchInput.addEventListener('input', debounce(function (e) {
        searchArticles(e.target.value);
    }, 300));

    ['searchModal', 'receiptModal', 'historyModal', 'discountModal'].forEach((id) => {
        const modal = document.getElementById(id);
        if (!modal) return;
        modal.addEventListener('click', function (e) {
            if (e.target !== modal) return;
            if (id === 'searchModal') closeSearchModal();
            if (id === 'receiptModal') closeReceiptModal();
            if (id === 'historyModal') closeHistoryModal();
            if (id === 'discountModal') closeDiscountModal();
        });
    });
}

// --- GESTION DES RACCOURCIS CLAVIER ---
/**
 * Configure les touches Rapides pour améliorer la productivité du caissier.
 * F1: Recherche rapide | F5: Passer au paiement | ESC: Annuler/Fermer
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', async function (e) {
        // F1 - Ouvre la recherche d'articles
        if (e.key === 'F1') {
            e.preventDefault();
            openSearchModal();
        }
        // F5 - Ouvre la fenêtre de paiement si le panier n'est pas vide
        else if (e.key === 'F5') {
            e.preventDefault();
            if (cart.length > 0) {
                openPaymentModal();
            }
        }
        // F2 - Appliquer une remise
        else if (e.key === 'F2') {
            e.preventDefault();
            openDiscountModal();
        }
        // ESC - Gestion de la fermeture des fenêtres ou vidage du panier
        else if (e.key === 'Escape') {
            if (!document.getElementById('searchModal').classList.contains('hidden')) {
                closeSearchModal();
            } else if (!document.getElementById('discountModal').classList.contains('hidden')) {
                closeDiscountModal();
            } else if (!document.getElementById('historyModal').classList.contains('hidden')) {
                closeHistoryModal();
            } else if (!document.getElementById('receiptModal').classList.contains('hidden')) {
                closeReceiptModal();
            } else if (cart.length > 0) {
                if (window.AppNotify && await window.AppNotify.confirm('Vider le panier ?')) {
                    clearCart();
                }
            }
        }
    });
}

// --- COMMUNICATIONS AVEC LE SERVEUR (API) ---

/**
 * Récupère le jeton CSRF nécessaire pour sécuriser les requêtes POST vers Django.
 * Sans ce jeton, le serveur rejettera toute tentative d'enregistrement par sécurité.
 */
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

/**
 * Recherche un article par son code-barres via l'API Django.
 * Utilisé lors d'un scan direct ou d'une saisie manuelle rapide.
 */
function searchArticleByBarcode(barcode) {
    if (!barcode) return;

    // Appel asynchrone au backend
    fetch(`/caisse/api/search/?q=${barcode}`)
        .then(response => response.json())
        .then(data => {
            if (data.articles && data.articles.length > 0) {
                // On prend le premier article correspondant trouvé en base de données
                const article = data.articles[0];
                addToCart(article);
            } else {
                if (window.AppNotify) {
                    window.AppNotify.warning('Article non trouvé dans la base de donnees');
                }
            }
        })
        .catch(error => console.error('Erreur lors de la recherche:', error));
}

// Search articles (modal)
function searchArticles(query) {
    // Si vide, charger tous les articles
    if (!query || query.length === 0) {
        fetch(`/caisse/api/search/?q=`)
            .then(response => response.json())
            .then(data => {
                lastSearchResults = data.articles;
                displaySearchResults(data.articles);
            })
            .catch(error => console.error('Erreur:', error));
        return;
    }

    fetch(`/caisse/api/search/?q=${query}`)
        .then(response => response.json())
        .then(data => {
            lastSearchResults = data.articles;
            displaySearchResults(data.articles);
        })
        .catch(error => console.error('Erreur:', error));
}

// Display search results
function displaySearchResults(articles) {
    const container = document.getElementById('searchResults');

    if (articles.length === 0) {
        container.innerHTML = '<p class="text-center text-slate-500 dark:text-zinc-400 py-8">Aucun article trouvé</p>';
        return;
    }

    container.innerHTML = articles.map((article, index) => `
        <div class="search-result-item p-4 border-b border-slate-200 dark:border-zinc-800 hover:bg-slate-50 dark:hover:bg-zinc-800" onclick='addToCartFromIndex(${index})'>
            <div class="flex justify-between items-start">
                <div class="flex-1">
                    <h4 class="font-semibold text-slate-900 dark:text-zinc-100">${article.nom}</h4>
                    <p class="text-sm text-slate-500 dark:text-zinc-400">${article.code_barres}</p>
                </div>
                <div class="text-right">
                    <p class="font-bold text-lg text-slate-900 dark:text-zinc-100">${article.prix_ttc.toFixed(2)} FCFA</p>
                    <p class="text-sm text-slate-500 dark:text-zinc-400">Stock: ${article.stock}</p>
                </div>
            </div>
        </div>
    `).join('');
}

/**
 * Ajoute un article au panier depuis son index dans les résultats de recherche.
 * Évite les problèmes de caractères spéciaux dans le JSON.
 */
function addToCartFromIndex(index) {
    const article = lastSearchResults[index];
    if (article) {
        addToCart(article);
        closeSearchModal();
    }
}

// Add item to cart
function addToCart(article) {
    const existingItem = cart.find(item => item.article_id === article.id);

    if (existingItem) {
        existingItem.quantite++;
        existingItem.total = existingItem.quantite * existingItem.prix_unitaire;
    } else {
        cart.push({
            id: nextItemId++,
            article_id: article.id,
            nom: article.nom,
            code_barres: article.code_barres,
            prix_unitaire: article.prix_ttc,
            prix_ht: article.prix_ht,
            quantite: 1,
            total: article.prix_ttc,
            tva_rate: article.tva_rate ?? 0
        });
    }

    updateCart();
}

// Update quantity
function updateQuantity(itemId, delta) {
    const item = cart.find(i => i.id === itemId);
    if (!item) return;

    item.quantite += delta;

    if (item.quantite <= 0) {
        removeFromCart(itemId);
    } else {
        item.total = item.quantite * item.prix_unitaire;
        updateCart();
    }
}

// Remove from cart
function removeFromCart(itemId) {
    cart = cart.filter(item => item.id !== itemId);
    updateCart();
}

// Clear cart
function clearCart() {
    cart = [];
    discount = { type: null, value: 0, amount: 0 };
    updateCart();
}

function computeDiscountAmount(totalTTC) {
    if (!discount.type || discount.value <= 0) return 0;
    if (discount.type === 'percent') {
        return Math.min(totalTTC, (totalTTC * discount.value) / 100);
    }
    return Math.min(totalTTC, discount.value);
}

// Update cart display
function updateCart() {
    const cartItemsContainer = document.getElementById('cartItems');
    const emptyCart = document.getElementById('emptyCart');
    const cartTitle = document.getElementById('cartTitle');
    const paymentBtn = document.getElementById('paymentBtn');

    // Calculate totals
    const totalItems = cart.reduce((sum, item) => sum + item.quantite, 0);
    const totalHT = cart.reduce((sum, item) => sum + (item.prix_ht * item.quantite), 0);
    const totalTTCBrut = cart.reduce((sum, item) => sum + item.total, 0);
    const totalTVABrut = totalTTCBrut - totalHT;
    discount.amount = computeDiscountAmount(totalTTCBrut);
    const totalTTC = Math.max(0, totalTTCBrut - discount.amount);
    const ratio = totalTTCBrut > 0 ? (totalTTC / totalTTCBrut) : 1;
    const totalTVA = totalTVABrut * ratio;
    const totalHTNet = totalHT * ratio;

    // Update title
    cartTitle.textContent = `Panier (${totalItems} article${totalItems > 1 ? 's' : ''})`;

    // Update totals
    document.getElementById('totalHT').textContent = totalHTNet.toFixed(2) + ' FCFA';
    document.getElementById('totalTVA').textContent = totalTVA.toFixed(2) + ' FCFA';
    document.getElementById('totalTTC').textContent = totalTTC.toFixed(2) + ' FCFA';
    document.getElementById('totalRemise').textContent = '- ' + discount.amount.toFixed(2) + ' FCFA';
    document.getElementById('itemCount').textContent = totalItems;

    // Enable/disable payment button
    paymentBtn.disabled = cart.length === 0;

    // Show/hide empty state
    if (cart.length === 0) {
        emptyCart.classList.remove('hidden');
        const existingItems = cartItemsContainer.querySelectorAll('.cart-item');
        existingItems.forEach(item => item.remove());
    } else {
        emptyCart.classList.add('hidden');

        // Render cart items
        const existingItems = cartItemsContainer.querySelectorAll('.cart-item');
        existingItems.forEach(item => item.remove());

        cart.forEach(item => {
            const itemElement = document.createElement('div');
            itemElement.className = 'cart-item p-4';
            itemElement.innerHTML = `
                <div class="flex items-center justify-between">
                    <div class="flex-1">
                        <h4 class="font-semibold text-slate-900 dark:text-zinc-100">${item.nom}</h4>
                        <p class="text-sm text-slate-500 dark:text-zinc-400">${item.prix_unitaire.toFixed(2)} FCFA • TVA ${item.tva_rate}%</p>
                    </div>
                    <div class="flex items-center gap-4">
                        <div class="flex items-center gap-2">
                            <button onclick="updateQuantity(${item.id}, -1)" class="quantity-btn w-8 h-8 rounded-lg border border-slate-300 dark:border-zinc-700 flex items-center justify-center hover:bg-slate-100 dark:hover:bg-zinc-800 text-slate-900 dark:text-zinc-100">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"></path>
                                </svg>
                            </button>
                            <span class="w-12 text-center font-medium text-slate-900 dark:text-zinc-100">${item.quantite}</span>
                            <button onclick="updateQuantity(${item.id}, 1)" class="quantity-btn w-8 h-8 rounded-lg border border-slate-300 dark:border-zinc-700 flex items-center justify-center hover:bg-slate-100 dark:hover:bg-zinc-800 text-slate-900 dark:text-zinc-100">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                                </svg>
                            </button>
                        </div>
                        <span class="font-bold text-lg w-24 text-right text-slate-900 dark:text-zinc-100">${item.total.toFixed(2)} FCFA</span>
                        <button onclick="removeFromCart(${item.id})" class="text-red-500 hover:text-red-700">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                            </svg>
                        </button>
                    </div>
                </div>
            `;
            cartItemsContainer.appendChild(itemElement);
        });
    }
}

// Modal functions
function openSearchModal() {
    document.getElementById('searchModal').classList.remove('hidden');
    document.getElementById('modalSearchInput').focus();
    // Load all articles immediately
    searchArticles('');
}

function closeSearchModal() {
    document.getElementById('searchModal').classList.add('hidden');
    document.getElementById('modalSearchInput').value = '';
    document.getElementById('searchResults').innerHTML = '';
}

function openHistoryModal() {
    const modal = document.getElementById('historyModal');
    const content = document.getElementById('historyContent');
    if (!modal || !content) return;

    modal.classList.remove('hidden');
    content.innerHTML = '<p class="text-sm text-slate-500 dark:text-zinc-400">Chargement...</p>';

    fetch('/caisse/api/factures/recent/')
        .then(response => response.json())
        .then(data => {
            const factures = data.factures || [];
            if (!factures.length) {
                content.innerHTML = '<p class="text-sm text-slate-500 dark:text-zinc-400">Aucune facture recente.</p>';
                return;
            }
            content.innerHTML = `
                <div class="overflow-x-auto">
                    <table class="w-full text-left">
                        <thead class="bg-slate-50 dark:bg-zinc-800/50 border-b border-slate-200 dark:border-zinc-800">
                            <tr>
                                <th class="px-3 py-2 text-xs font-semibold text-slate-500 dark:text-zinc-400 uppercase">Numero</th>
                                <th class="px-3 py-2 text-xs font-semibold text-slate-500 dark:text-zinc-400 uppercase">Date</th>
                                <th class="px-3 py-2 text-xs font-semibold text-slate-500 dark:text-zinc-400 uppercase">Client</th>
                                <th class="px-3 py-2 text-xs font-semibold text-slate-500 dark:text-zinc-400 uppercase">Paiement</th>
                                <th class="px-3 py-2 text-xs font-semibold text-slate-500 dark:text-zinc-400 uppercase text-right">Total TTC</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-100 dark:divide-zinc-800">
                            ${factures.map(f => `
                                <tr class="hover:bg-slate-50 dark:hover:bg-zinc-800/30">
                                    <td class="px-3 py-2 text-sm font-medium text-slate-900 dark:text-zinc-100">${f.numero}</td>
                                    <td class="px-3 py-2 text-sm text-slate-600 dark:text-zinc-300">${f.date}</td>
                                    <td class="px-3 py-2 text-sm text-slate-600 dark:text-zinc-300">${f.client}</td>
                                    <td class="px-3 py-2 text-sm text-slate-600 dark:text-zinc-300">${f.mode_paiement}</td>
                                    <td class="px-3 py-2 text-sm font-semibold text-slate-900 dark:text-zinc-100 text-right">${Number(f.total_ttc).toFixed(2)} FCFA</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        })
        .catch(() => {
            content.innerHTML = '<p class="text-sm text-red-600">Impossible de charger l\'historique.</p>';
        });
}

function closeHistoryModal() {
    const modal = document.getElementById('historyModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

function openDiscountModal() {
    const modal = document.getElementById('discountModal');
    if (!modal) return;
    document.getElementById('discountType').value = discount.type || 'percent';
    document.getElementById('discountValue').value = discount.value || '';
    modal.classList.remove('hidden');
}

function closeDiscountModal() {
    const modal = document.getElementById('discountModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

function clearDiscount() {
    discount = { type: null, value: 0, amount: 0 };
    closeDiscountModal();
    updateCart();
    if (window.AppNotify) {
        window.AppNotify.info('Remise retiree');
    }
}

function applyDiscount() {
    const type = document.getElementById('discountType').value;
    const value = Number(document.getElementById('discountValue').value || 0);

    if (!cart.length) {
        if (window.AppNotify) window.AppNotify.warning('Le panier est vide');
        return;
    }

    if (!value || value <= 0) {
        if (window.AppNotify) window.AppNotify.warning('Valeur de remise invalide');
        return;
    }

    discount.type = type;
    discount.value = value;
    closeDiscountModal();
    updateCart();
    if (window.AppNotify) {
        window.AppNotify.success('Remise appliquee');
    }
}

function openPaymentModal() {
    if (cart.length === 0) return;

    // Generate receipt
    const receiptNumber = 'FAC-' + Math.floor(Math.random() * 100000000).toString().padStart(8, '0');
    const now = new Date();
    const dateStr = now.toLocaleDateString('fr-FR') + ' ' + now.toLocaleTimeString('fr-FR');

    document.getElementById('receiptNumber').textContent = receiptNumber;
    document.getElementById('receiptDate').textContent = dateStr;

    // Calculate totals
    const totalHTBrut = cart.reduce((sum, item) => sum + (item.prix_ht * item.quantite), 0);
    const totalTTCBrut = cart.reduce((sum, item) => sum + item.total, 0);
    const discountAmount = computeDiscountAmount(totalTTCBrut);
    const totalTTC = Math.max(0, totalTTCBrut - discountAmount);
    const ratio = totalTTCBrut > 0 ? (totalTTC / totalTTCBrut) : 1;
    const totalHT = totalHTBrut * ratio;
    const totalTVA = totalTTC - totalHT;

    document.getElementById('receiptHT').textContent = totalHT.toFixed(2) + ' FCFA';
    document.getElementById('receiptTVA').textContent = totalTVA.toFixed(2) + ' FCFA';
    document.getElementById('receiptTTC').textContent = totalTTC.toFixed(2) + ' FCFA';
    document.getElementById('receiptRemise').textContent = '- ' + discountAmount.toFixed(2) + ' FCFA';

    // Render items
    const receiptItems = document.getElementById('receiptItems');
    receiptItems.innerHTML = cart.map(item => `
        <div class="flex justify-between text-sm">
            <span>${item.nom} x${item.quantite}</span>
            <span class="font-medium">${item.total.toFixed(2)} FCFA</span>
        </div>
    `).join('');

    document.getElementById('receiptModal').classList.remove('hidden');
}

function closeReceiptModal() {
    document.getElementById('receiptModal').classList.add('hidden');
    // Clear client name input for next transaction
    document.getElementById('clientNameInput').value = '';
}

function printReceipt() {
    window.print();
}

/**
 * ACTION FINALE : Enregistrement de la vente.
 * Envoie le contenu du panier au serveur pour créer une Facture officielle
 * et mettre à jour les stocks en base de données.
 */
function finishTransaction() {
    // Sécurité : ne rien faire si le panier est vide
    if (cart.length === 0) return;

    // Récupérer le nom du client (s'il est fourni)
    const clientName = document.getElementById('clientNameInput').value.trim();

    // Récupérer le mode de paiement sélectionné
    const paymentMethod = document.getElementById('paymentMethod').value;

    // Préparation des données pour le serveur
    const data = {
        items: cart.map(item => ({
            article_id: item.article_id,
            quantite: item.quantite,
            prix_unitaire: item.prix_unitaire,
            total: item.total
        })),
        client_name: clientName,  // Nom du client (peut être vide pour anonyme)
        mode_paiement: paymentMethod // Mode de paiement sélectionné
        ,
        remise: {
            type: discount.type,
            value: discount.value,
            amount: discount.amount
        }
    };

    // Envoi de la requête POST au serveur Django
    fetch('/caisse/api/facture/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken() // Protection contre les attaques CSRF
        },
        body: JSON.stringify(data) // Conversion de l'objet JS en texte (JSON)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Si le serveur confirme l'enregistrement (Code 200)
                if (window.AppNotify) {
                    window.AppNotify.success(`Transaction terminee avec succes. Facture: ${data.numero_facture}`);
                }
                clearCart();         // Vide le panier
                closeReceiptModal(); // Ferme la fenêtre
            } else {
                // Si le serveur renvoie une erreur (ex: rupture de stock)
                if (window.AppNotify) {
                    window.AppNotify.error('Erreur serveur lors de la creation de la facture: ' + data.error);
                }
            }
        })
        .catch(error => {
            console.error('Erreur fatale:', error);
            if (window.AppNotify) {
                window.AppNotify.error('Impossible de contacter le serveur. Verifiez votre connexion.');
            }
        });
}

/**
 * Fonction Utilitaire : Debounce
 * Permet de retarder l'exécution d'une fonction (évite de lancer 50 requêtes quand on tape vite).
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const context = this; // On capture le contexte 'this' original
        const later = () => {
            clearTimeout(timeout);
            func.apply(context, args); // On appelle la fonction avec le bon 'this' et les bons arguments
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
