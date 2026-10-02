// ===============================================================
// PriceWatch Frontend - Application JavaScript Vanilla
// Développé pour le projet L3 MIAGE - Université de Toulouse
// ===============================================================

let currentPriceChart = null;

// Initialisation au chargement du DOM
document.addEventListener("DOMContentLoaded", () => {
    setupNavigation();
    loadDashboardStats();
    loadStoresDropdown();
    setupAddProductForm();
    setupAddSourceForm();
});

// ---------------------------------------------------------------
// Gestion de la navigation par onglets
// ---------------------------------------------------------------
function setupNavigation() {
    const navButtons = document.querySelectorAll(".nav-btn");
    navButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTab = btn.getAttribute("data-tab");
            switchTab(targetTab);
        });
    });
}

function switchTab(tabId) {
    document.querySelectorAll(".nav-btn").forEach(btn => {
        btn.classList.toggle("active", btn.getAttribute("data-tab") === tabId);
    });

    document.querySelectorAll(".tab-content").forEach(tab => {
        tab.classList.toggle("active", tab.id === tabId);
    });

    // Chargement dynamique des données selon l'onglet affiché
    if (tabId === "tab-dashboard") {
        loadDashboardStats();
    } else if (tabId === "tab-products") {
        loadProducts();
    } else if (tabId === "tab-history") {
        loadHistoryTab();
    } else if (tabId === "tab-alerts") {
        loadAlerts();
    }
}

// ---------------------------------------------------------------
// Notifications Toast
// ---------------------------------------------------------------
function showToast(message, isError = false) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.style.background = isError ? "#dc2626" : "#1e293b";
    toast.style.display = "block";
    setTimeout(() => {
        toast.style.display = "none";
    }, 4000);
}

// ---------------------------------------------------------------
// Action globale : Déclenchement du Scraping
// ---------------------------------------------------------------
async function triggerScraping() {
    const btn = document.getElementById("btn-trigger-scrape");
    btn.disabled = true;
    btn.textContent = "⏳ Scraping en cours...";

    try {
        const response = await fetch("/api/scrape", { method: "POST" });
        if (!response.ok) throw new Error("Erreur HTTP lors du scraping");
        const data = await response.json();

        showToast(`✅ Scraping terminé : ${data.prices_recorded} prix relevés, ${data.alerts_created} nouvelle(s) alerte(s).`);

        // Rafraîchir l'onglet actif
        const activeTab = document.querySelector(".tab-content.active").id;
        if (activeTab === "tab-dashboard") loadDashboardStats();
        if (activeTab === "tab-products") loadProducts();
        if (activeTab === "tab-history") loadProductHistory();
        if (activeTab === "tab-alerts") loadAlerts();

    } catch (err) {
        showToast("Erreur lors de la collecte des prix : " + err.message, true);
    } finally {
        btn.disabled = false;
        btn.innerHTML = "🔄 Actualiser les prix";
    }
}

// ---------------------------------------------------------------
// Onglet 1 : Dashboard (Statistiques)
// ---------------------------------------------------------------
async function loadDashboardStats() {
    try {
        const res = await fetch("/api/stats");
        const stats = await res.json();

        document.getElementById("stat-products").textContent = stats.products_count;
        document.getElementById("stat-stores").textContent = stats.stores_count;
        document.getElementById("stat-prices").textContent = stats.prices_count;
        document.getElementById("stat-alerts").textContent = stats.unread_alerts_count;

        // Mise à jour du badge de notification sur l'onglet Alertes
        const alertBadge = document.getElementById("nav-alerts-badge");
        if (alertBadge) {
            alertBadge.textContent = stats.unread_alerts_count;
            alertBadge.style.display = stats.unread_alerts_count > 0 ? "inline-block" : "none";
        }

        // Rendu des dernières alertes
        const alertsContainer = document.getElementById("dashboard-latest-alerts");
        if (stats.latest_alerts && stats.latest_alerts.length > 0) {
            alertsContainer.innerHTML = stats.latest_alerts.map(a => `
                <div style="padding: 10px 0; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>${escapeHtml(a.product_name)}</strong> sur <em>${escapeHtml(a.store_name)}</em> :
                        <span style="color: #16a34a; font-weight: bold;">${a.price} €</span>
                        <div style="font-size: 0.8rem; color: #64748b;">${new Date(a.created_at).toLocaleString("fr-FR")}</div>
                    </div>
                    <span class="badge ${a.is_read ? 'badge-pill' : 'badge-danger'}">${a.is_read ? 'Lue' : 'Nouvelle'}</span>
                </div>
            `).join("");
        } else {
            alertsContainer.innerHTML = "<p style='color: #64748b;'>Aucune alerte active pour le moment.</p>";
        }

        // Chargement du comparateur résumé sur le dashboard
        loadDashboardComparison();

    } catch (err) {
        console.error("Erreur stats dashboard:", err);
    }
}

async function loadDashboardComparison() {
    try {
        const res = await fetch("/api/products");
        const products = await res.json();
        const tbody = document.getElementById("dashboard-comparison-tbody");

        if (!products || products.length === 0) {
            tbody.innerHTML = "<tr><td colspan='4' style='text-align: center; color: #64748b;'>Aucun produit surveillé. Ajoutez-en un dans l'onglet Produits !</td></tr>";
            return;
        }

        tbody.innerHTML = products.map(p => {
            const bestPriceText = p.best_price !== null ? `${p.best_price} € (${p.best_store})` : "En attente de scraping";
            const sourcesList = p.sources.map(s => `
                <span class="badge ${s.current_price === p.best_price && p.best_price !== null ? 'badge-success' : 'badge-pill'}">
                    ${escapeHtml(s.store_name)}: ${s.current_price !== null ? s.current_price + ' €' : '-'}
                </span>
            `).join(" ");

            return `
                <tr>
                    <td><strong>${escapeHtml(p.name)}</strong></td>
                    <td>${p.sources.length} site(s)</td>
                    <td>${sourcesList || "Aucune source"}</td>
                    <td><span class="badge badge-success">${bestPriceText}</span></td>
                </tr>
            `;
        }).join("");

    } catch (err) {
        console.error("Erreur chargement comparaison dashboard:", err);
    }
}

// ---------------------------------------------------------------
// Onglet 2 : Produits & Comparaison Détaillée
// ---------------------------------------------------------------
async function loadProducts() {
    try {
        const res = await fetch("/api/products");
        const products = await res.json();
        const container = document.getElementById("products-list-container");

        if (!products || products.length === 0) {
            container.innerHTML = "<p style='color: #64748b; padding: 20px 0;'>Aucun produit enregistré. Utilisez le formulaire ci-dessus pour ajouter votre premier produit !</p>";
            return;
        }

        container.innerHTML = products.map(p => {
            const bestBadge = p.best_price !== null 
                ? `<span class="best-price-badge">🏆 Meilleur prix : ${p.best_price} € (${escapeHtml(p.best_store)})</span>`
                : `<span class="badge badge-warning">Scraping en attente</span>`;

            // Tableau des sources pour ce produit
            const rows = p.sources.map(s => {
                const isBest = (s.current_price !== null && s.current_price === p.best_price);
                const priceFormatted = s.current_price !== null ? `<strong>${s.current_price} €</strong>` : "<em style='color:#64748b'>Non relevé</em>";
                const thresholdFormatted = s.alert_threshold !== null ? `${s.alert_threshold} €` : "-";
                const updatedFormatted = s.last_updated ? new Date(s.last_updated).toLocaleString("fr-FR") : "-";

                return `
                    <tr class="${isBest ? 'highlight-best' : ''}">
                        <td><strong>${escapeHtml(s.store_name)}</strong></td>
                        <td>${priceFormatted} ${isBest ? '<span class="badge badge-success">Moins cher</span>' : ''}</td>
                        <td>${thresholdFormatted}</td>
                        <td style="font-size: 0.85rem; color: #475569;">${updatedFormatted}</td>
                        <td>
                            <a href="${s.url}" target="_blank" class="btn btn-secondary btn-sm" style="margin-right: 5px;">Voir l'offre</a>
                            <button onclick="deleteSource(${s.id})" class="btn btn-danger btn-sm" title="Supprimer cette source">Retirer</button>
                        </td>
                    </tr>
                `;
            }).join("");

            return `
                <div class="comparison-card">
                    <div class="comparison-header">
                        <div>
                            <h3>${escapeHtml(p.name)}</h3>
                            <span style="font-size: 0.8rem; color: #64748b;">Ajouté le ${new Date(p.created_at).toLocaleDateString("fr-FR")}</span>
                        </div>
                        <div style="display: flex; gap: 10px; align-items: center;">
                            ${bestBadge}
                            <button onclick="openAddSourceModal(${p.id}, '${escapeHtml(p.name)}')" class="btn btn-secondary btn-sm">+ Ajouter un magasin</button>
                            <button onclick="deleteProduct(${p.id})" class="btn btn-danger btn-sm">Supprimer le produit</button>
                        </div>
                    </div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Boutique</th>
                                    <th>Prix actuel</th>
                                    <th>Seuil d'alerte</th>
                                    <th>Dernière mise à jour</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${rows || "<tr><td colspan='5' style='color:#64748b;'>Aucune source marchande associée.</td></tr>"}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }).join("");

    } catch (err) {
        console.error("Erreur chargement produits:", err);
    }
}

// Formulaire : Ajouter un produit
function setupAddProductForm() {
    const form = document.getElementById("form-add-product");
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = document.getElementById("product-name").value.trim();
        const storeName = document.getElementById("product-store").value;
        const url = document.getElementById("product-url").value.trim();
        const thresholdVal = document.getElementById("product-threshold").value;
        const threshold = thresholdVal ? parseFloat(thresholdVal) : null;

        if (!name) return;

        try {
            const res = await fetch("/api/products", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    name: name,
                    store_name: storeName || null,
                    url: url || null,
                    alert_threshold: threshold
                })
            });

            if (!res.ok) throw new Error("Erreur lors de la création du produit");

            showToast("Produit ajouté avec succès !");
            form.reset();
            loadProducts();
            loadDashboardStats();

            // Si une URL a été fournie, proposer de scraper directement
            if (url) {
                triggerScraping();
            }

        } catch (err) {
            showToast(err.message, true);
        }
    });
}

async function deleteProduct(productId) {
    if (!confirm("Êtes-vous sûr de vouloir supprimer ce produit et tout son historique ?")) return;

    try {
        const res = await fetch(`/api/products/${productId}`, { method: "DELETE" });
        if (!res.ok) throw new Error("Erreur suppression produit");
        showToast("Produit supprimé");
        loadProducts();
        loadDashboardStats();
    } catch (err) {
        showToast(err.message, true);
    }
}

async function deleteSource(sourceId) {
    if (!confirm("Retirer ce magasin de la surveillance ?")) return;

    try {
        const res = await fetch(`/api/sources/${sourceId}`, { method: "DELETE" });
        if (!res.ok) throw new Error("Erreur suppression source");
        showToast("Source marchande retirée");
        loadProducts();
        loadDashboardStats();
    } catch (err) {
        showToast(err.message, true);
    }
}

// Modal : Associer un nouveau magasin à un produit existant
function openAddSourceModal(productId, productName) {
    document.getElementById("modal-source-product-id").value = productId;
    document.getElementById("modal-source-product-name").textContent = productName;
    document.getElementById("modal-add-source").style.display = "flex";
}

function closeAddSourceModal() {
    document.getElementById("modal-add-source").style.display = "none";
    document.getElementById("form-modal-source").reset();
}

function setupAddSourceForm() {
    const form = document.getElementById("form-modal-source");
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const productId = document.getElementById("modal-source-product-id").value;
        const storeId = document.getElementById("modal-source-store-id").value;
        const url = document.getElementById("modal-source-url").value.trim();
        const thresholdVal = document.getElementById("modal-source-threshold").value;
        const threshold = thresholdVal ? parseFloat(thresholdVal) : null;

        try {
            const res = await fetch(`/api/products/${productId}/sources`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    store_id: parseInt(storeId),
                    url: url,
                    alert_threshold: threshold
                })
            });

            if (!res.ok) throw new Error("Erreur lors de l'ajout de la source");

            showToast("Nouvelle source associée avec succès !");
            closeAddSourceModal();
            loadProducts();
            loadDashboardStats();
            triggerScraping();

        } catch (err) {
            showToast(err.message, true);
        }
    });
}

// Chargement des magasins dans les listes déroulantes
async function loadStoresDropdown() {
    try {
        const res = await fetch("/api/stores");
        const stores = await res.json();

        // Sélecteur dans le modal
        const modalSelect = document.getElementById("modal-source-store-id");
        if (modalSelect) {
            modalSelect.innerHTML = stores.map(s => `<option value="${s.id}">${escapeHtml(s.name)}</option>`).join("");
        }

        // Sélecteur dans le formulaire principal
        const mainSelect = document.getElementById("product-store");
        if (mainSelect) {
            mainSelect.innerHTML = `<option value="">Sélectionner une boutique...</option>` +
                stores.map(s => `<option value="${escapeHtml(s.name)}">${escapeHtml(s.name)}</option>`).join("");
        }
    } catch (err) {
        console.error("Erreur chargement magasins:", err);
    }
}

// ---------------------------------------------------------------
// Onglet 3 : Historique & Graphique d'évolution des prix
// ---------------------------------------------------------------
async function loadHistoryTab() {
    try {
        const res = await fetch("/api/products");
        const products = await res.json();
        const select = document.getElementById("history-product-select");

        if (!products || products.length === 0) {
            select.innerHTML = "<option value=''>Aucun produit disponible</option>";
            return;
        }

        select.innerHTML = products.map(p => `<option value="${p.id}">${escapeHtml(p.name)}</option>`).join("");
        select.addEventListener("change", () => loadProductHistory());

        // Charge le premier produit par défaut
        loadProductHistory();
    } catch (err) {
        console.error("Erreur chargement onglet historique:", err);
    }
}

async function loadProductHistory() {
    const select = document.getElementById("history-product-select");
    const productId = select.value;
    if (!productId) return;

    try {
        const res = await fetch(`/api/products/${productId}/prices`);
        const data = await res.json();

        renderHistoryChart(data);
        renderHistoryTable(data);
    } catch (err) {
        console.error("Erreur récupération historique produit:", err);
    }
}

function renderHistoryChart(data) {
    const ctx = document.getElementById("priceChart").getContext("2d");

    if (currentPriceChart) {
        currentPriceChart.destroy();
    }

    // Récupérer toutes les dates uniques pour l'axe des abscisses (X)
    const dateSet = new Set();
    data.stores.forEach(st => {
        st.history.forEach(pt => {
            dateSet.add(pt.collected_at);
        });
    });
    const sortedDates = Array.from(dateSet).sort();
    const formattedLabels = sortedDates.map(d => new Date(d).toLocaleDateString("fr-FR", {
        month: "short", day: "numeric", hour: "2-digit", minute: "2-digit"
    }));

    // Couleurs distinctes pour les courbes de magasins
    const colors = [
        { border: "#2563eb", bg: "rgba(37, 99, 235, 0.1)" },
        { border: "#dc2626", bg: "rgba(220, 38, 38, 0.1)" },
        { border: "#0891b2", bg: "rgba(8, 145, 178, 0.1)" },
        { border: "#d97706", bg: "rgba(217, 119, 6, 0.1)" }
    ];

    const datasets = data.stores.map((st, index) => {
        const color = colors[index % colors.length];
        // Mapper chaque date vers le prix ou null si pas de relevé
        const priceMap = {};
        st.history.forEach(pt => {
            priceMap[pt.collected_at] = pt.price;
        });

        const seriesData = sortedDates.map(d => priceMap[d] !== undefined ? priceMap[d] : null);

        return {
            label: st.store_name,
            data: seriesData,
            borderColor: color.border,
            backgroundColor: color.bg,
            borderWidth: 2,
            tension: 0.2,
            fill: false,
            pointRadius: 4,
            spanGaps: true
        };
    });

    currentPriceChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: formattedLabels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `Évolution des prix : ${data.product_name}`
                },
                tooltip: {
                    callbacks: {
                        label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y} €`
                    }
                }
            },
            scales: {
                y: {
                    title: {
                        display: true,
                        text: "Prix en euros (€)"
                    },
                    beginAtZero: false
                },
                x: {
                    title: {
                        display: true,
                        text: "Date du relevé"
                    }
                }
            }
        }
    });
}

function renderHistoryTable(data) {
    const tbody = document.getElementById("history-table-tbody");
    const rows = [];

    data.stores.forEach(st => {
        st.history.forEach(pt => {
            rows.push({
                store: st.store_name,
                price: pt.price,
                date: pt.collected_at
            });
        });
    });

    // Trier du plus récent au plus ancien
    rows.sort((a, b) => new Date(b.date) - new Date(a.date));

    if (rows.length === 0) {
        tbody.innerHTML = "<tr><td colspan='3' style='text-align:center; color:#64748b;'>Aucun historique enregistré pour ce produit.</td></tr>";
        return;
    }

    tbody.innerHTML = rows.map(r => `
        <tr>
            <td><strong>${escapeHtml(r.store)}</strong></td>
            <td><span style="font-weight:600; color:#16a34a;">${r.price} €</span></td>
            <td>${new Date(r.date).toLocaleString("fr-FR")}</td>
        </tr>
    `).join("");
}

// ---------------------------------------------------------------
// Onglet 4 : Alertes
// ---------------------------------------------------------------
async function loadAlerts() {
    try {
        const res = await fetch("/api/alerts");
        const alerts = await res.json();
        const container = document.getElementById("alerts-list-container");

        if (!alerts || alerts.length === 0) {
            container.innerHTML = "<p style='color: #64748b; padding: 20px 0;'>Aucune alerte n'a encore été déclenchée. Les alertes apparaissent automatiquement lorsqu'un prix passe sous le seuil configuré !</p>";
            return;
        }

        container.innerHTML = alerts.map(a => `
            <div class="card" style="border-left: 4px solid ${a.is_read ? '#94a3b8' : '#dc2626'};">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 15px; flex-wrap: wrap;">
                    <div>
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
                            <span style="font-size: 1.1rem; font-weight: 700; color: #1e293b;">${escapeHtml(a.message)}</span>
                            <span class="badge ${a.is_read ? 'badge-pill' : 'badge-danger'}">${a.is_read ? 'Lue' : 'Active'}</span>
                        </div>
                        <div style="font-size: 0.85rem; color: #64748b;">
                            Produit : <strong>${escapeHtml(a.product_name)}</strong> | 
                            Boutique : <strong>${escapeHtml(a.store_name)}</strong> | 
                            Date : ${new Date(a.created_at).toLocaleString("fr-FR")}
                        </div>
                    </div>
                    <div style="display: flex; gap: 8px;">
                        ${!a.is_read ? `<button onclick="markAlertAsRead(${a.id})" class="btn btn-secondary btn-sm">Marquer comme lue</button>` : ''}
                        <button onclick="deleteAlert(${a.id})" class="btn btn-danger btn-sm">Supprimer</button>
                    </div>
                </div>
            </div>
        `).join("");

    } catch (err) {
        console.error("Erreur chargement alertes:", err);
    }
}

async function markAlertAsRead(alertId) {
    try {
        const res = await fetch(`/api/alerts/${alertId}/read`, { method: "PATCH" });
        if (!res.ok) throw new Error("Erreur mise à jour alerte");
        loadAlerts();
        loadDashboardStats();
    } catch (err) {
        showToast(err.message, true);
    }
}

async function deleteAlert(alertId) {
    try {
        const res = await fetch(`/api/alerts/${alertId}`, { method: "DELETE" });
        if (!res.ok) throw new Error("Erreur suppression alerte");
        showToast("Alerte supprimée");
        loadAlerts();
        loadDashboardStats();
    } catch (err) {
        showToast(err.message, true);
    }
}

// ---------------------------------------------------------------
// Helper de sécurisation contre les failles XSS
// ---------------------------------------------------------------
function escapeHtml(str) {
    if (!str) return "";
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
