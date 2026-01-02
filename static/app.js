// Configurazione
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000/api'
    : '/api';

let currentData = {
    categorie: [],
    clienti: [],
    progetti: [],
    veicoli: [],
    spese: [],
    chilometriche: []
};

// ========== INIT ==========

document.addEventListener('DOMContentLoaded', () => {
    initApp();
    initNavigation();
    initForms();
    registerServiceWorker();
});

async function initApp() {
    showLoader();
    
    try {
        await Promise.all([
            loadCategorie(),
            loadClienti(),
            loadVeicoli()
        ]);
        
        await loadDashboard();
        setDefaultDates();
    } catch (error) {
        console.error('Errore inizializzazione:', error);
        showError('Errore di connessione al server');
    } finally {
        hideLoader();
    }
}

function setDefaultDates() {
    const oggi = new Date();
    const primoGiorno = new Date(oggi.getFullYear(), oggi.getMonth(), 1);
    const ultimoGiorno = new Date(oggi.getFullYear(), oggi.getMonth() + 1, 0);
    
    const formatDate = (d) => d.toISOString().split('T')[0];
    
    // Filtri spese
    document.getElementById('filter-spese-da').value = formatDate(primoGiorno);
    document.getElementById('filter-spese-a').value = formatDate(ultimoGiorno);
    
    // Filtri km
    document.getElementById('filter-km-da').value = formatDate(primoGiorno);
    document.getElementById('filter-km-a').value = formatDate(ultimoGiorno);
    
    // Export
    document.getElementById('export-spese-da').value = formatDate(primoGiorno);
    document.getElementById('export-spese-a').value = formatDate(ultimoGiorno);
    document.getElementById('export-km-da').value = formatDate(primoGiorno);
    document.getElementById('export-km-a').value = formatDate(ultimoGiorno);
    
    // Form spesa e km
    document.getElementById('spesa-data').value = formatDate(oggi);
    document.getElementById('km-data').value = formatDate(oggi);
}

function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/service-worker.js')
            .then(() => console.log('Service Worker registrato'))
            .catch(err => console.error('Errore Service Worker:', err));
    }
}

// ========== NAVIGATION ==========

function initNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => {
            const page = item.dataset.page;
            navigateToPage(page);
        });
    });
}

function navigateToPage(page) {
    // Rimuovi active da tutti
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelectorAll('.page').forEach(p => {
        p.classList.remove('active');
    });
    
    // Aggiungi active
    document.querySelector(`[data-page="${page}"]`).classList.add('active');
    document.getElementById(`page-${page}`).classList.add('active');
    
    // Carica dati se necessario
    if (page === 'spese') loadSpese();
    if (page === 'km') loadChilometriche();
    if (page === 'clienti') loadClientiTable();
    if (page === 'veicoli') loadVeicoliTable();
}

// ========== API CALLS ==========

async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    const response = await fetch(`${API_URL}${endpoint}`, options);
    const result = await response.json();
    
    if (!result.success) {
        throw new Error(result.error || 'Errore API');
    }
    
    return result.data;
}

// ========== LOAD DATA ==========

async function loadCategorie() {
    currentData.categorie = await apiCall('/categorie');
    populateCategorieSelects();
}

async function loadClienti() {
    currentData.clienti = await apiCall('/clienti');
    populateClientiSelects();
}

async function loadVeicoli() {
    currentData.veicoli = await apiCall('/veicoli');
    populateVeicoliSelects();
}

async function loadSpese() {
    showLoader();
    try {
        const params = new URLSearchParams();
        const da = document.getElementById('filter-spese-da').value;
        const a = document.getElementById('filter-spese-a').value;
        const cliente = document.getElementById('filter-spese-cliente').value;
        const categoria = document.getElementById('filter-spese-categoria').value;
        const addebitabili = document.getElementById('filter-spese-addebitabili').checked;
        
        if (da) params.append('data_inizio', da);
        if (a) params.append('data_fine', a);
        if (cliente) params.append('cliente_id', cliente);
        if (categoria) params.append('categoria_id', categoria);
        if (addebitabili) params.append('addebitabile', 'true');
        
        currentData.spese = await apiCall(`/spese?${params}`);
        renderSpeseTable();
    } finally {
        hideLoader();
    }
}

async function loadChilometriche() {
    showLoader();
    try {
        const params = new URLSearchParams();
        const da = document.getElementById('filter-km-da').value;
        const a = document.getElementById('filter-km-a').value;
        const veicolo = document.getElementById('filter-km-veicolo').value;
        
        if (da) params.append('data_inizio', da);
        if (a) params.append('data_fine', a);
        if (veicolo) params.append('veicolo_id', veicolo);
        
        currentData.chilometriche = await apiCall(`/chilometriche?${params}`);
        renderKmTable();
        updateKmTotals();
    } finally {
        hideLoader();
    }
}

async function loadDashboard() {
    try {
        const stats = await apiCall('/stats/dashboard');
        updateDashboardStats(stats);
        
        // Carica ultime spese
        const recentSpese = await apiCall('/spese?data_inizio=' + 
            new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]);
        renderRecentSpese(recentSpese.slice(0, 10));
    } catch (error) {
        console.error('Errore dashboard:', error);
    }
}

async function loadClientiTable() {
    showLoader();
    try {
        currentData.clienti = await apiCall('/clienti');
        renderClientiTable();
    } finally {
        hideLoader();
    }
}

async function loadVeicoliTable() {
    showLoader();
    try {
        currentData.veicoli = await apiCall('/veicoli');
        renderVeicoliTable();
    } finally {
        hideLoader();
    }
}

// ========== POPULATE SELECTS ==========

function populateCategorieSelects() {
    const selects = ['spesa-categoria', 'filter-spese-categoria'];
    
    selects.forEach(id => {
        const select = document.getElementById(id);
        select.innerHTML = id.includes('filter') ? '<option value="">Tutte</option>' : '<option value="">-- Seleziona --</option>';
        
        currentData.categorie.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.id;
            option.textContent = cat.nome;
            select.appendChild(option);
        });
    });
}

function populateClientiSelects() {
    const selects = ['spesa-cliente', 'km-cliente', 'filter-spese-cliente', 'export-spese-cliente'];
    
    selects.forEach(id => {
        const select = document.getElementById(id);
        select.innerHTML = id.includes('filter') || id.includes('export') 
            ? '<option value="">Tutti</option>' 
            : '<option value="">-- Nessuno --</option>';
        
        currentData.clienti.forEach(cliente => {
            const option = document.createElement('option');
            option.value = cliente.id;
            option.textContent = cliente.nome;
            select.appendChild(option);
        });
    });
}

function populateVeicoliSelects() {
    const selects = ['km-veicolo', 'filter-km-veicolo'];
    
    selects.forEach(id => {
        const select = document.getElementById(id);
        select.innerHTML = id.includes('filter') ? '<option value="">Tutti</option>' : '<option value="">-- Seleziona --</option>';
        
        currentData.veicoli.forEach(veicolo => {
            const option = document.createElement('option');
            option.value = veicolo.id;
            option.textContent = `${veicolo.targa} - ${veicolo.marca || ''} ${veicolo.modello || ''}`;
            option.dataset.tariffa = veicolo.usa_tariffa_custom && veicolo.tariffa_km_custom 
                ? veicolo.tariffa_km_custom 
                : veicolo.tariffa_km_aci;
            select.appendChild(option);
        });
    });
}

// ========== RENDER TABLES ==========

function renderSpeseTable() {
    const tbody = document.getElementById('spese-tbody');
    tbody.innerHTML = '';
    
    if (currentData.spese.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center">Nessuna spesa trovata</td></tr>';
        return;
    }
    
    currentData.spese.forEach(spesa => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${formatDate(spesa.data_spesa)}</td>
            <td>
                ${spesa.categorie ? `<span class="category-color" style="background:${spesa.categorie.colore}"></span>${spesa.categorie.nome}` : '-'}
            </td>
            <td>${spesa.clienti ? spesa.clienti.nome : '-'}</td>
            <td>${spesa.descrizione}</td>
            <td><strong>€ ${parseFloat(spesa.importo).toFixed(2)}</strong></td>
            <td>
                ${spesa.addebitabile ? '<span class="badge badge-success">Sì</span>' : '<span class="badge badge-secondary">No</span>'}
            </td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editSpesa(${spesa.id})">✏️</button>
                <button class="btn btn-sm btn-danger" onclick="deleteSpesa(${spesa.id})">🗑️</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function renderKmTable() {
    const tbody = document.getElementById('km-tbody');
    tbody.innerHTML = '';
    
    if (currentData.chilometriche.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center">Nessun viaggio trovato</td></tr>';
        return;
    }
    
    currentData.chilometriche.forEach(km => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${formatDate(km.data_viaggio)}</td>
            <td>${km.veicoli ? km.veicoli.targa : '-'}</td>
            <td>${km.partenza} → ${km.arrivo}</td>
            <td>${km.clienti ? km.clienti.nome : '-'}</td>
            <td><strong>${parseFloat(km.km_percorsi).toFixed(1)} km</strong></td>
            <td>€ ${parseFloat(km.tariffa_applicata).toFixed(3)}</td>
            <td><strong>€ ${parseFloat(km.rimborso_calcolato).toFixed(2)}</strong></td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editKm(${km.id})">✏️</button>
                <button class="btn btn-sm btn-danger" onclick="deleteKm(${km.id})">🗑️</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function renderClientiTable() {
    const tbody = document.getElementById('clienti-tbody');
    tbody.innerHTML = '';
    
    currentData.clienti.forEach(cliente => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${cliente.nome}</strong></td>
            <td>${cliente.codice || '-'}</td>
            <td>${cliente.partita_iva || '-'}</td>
            <td>${cliente.email || '-'}</td>
            <td>${cliente.telefono || '-'}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editCliente(${cliente.id})">✏️</button>
                <button class="btn btn-sm btn-danger" onclick="deleteCliente(${cliente.id})">🗑️</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function renderVeicoliTable() {
    const tbody = document.getElementById('veicoli-tbody');
    tbody.innerHTML = '';
    
    currentData.veicoli.forEach(veicolo => {
        const tr = document.createElement('tr');
        const tariffa = veicolo.usa_tariffa_custom && veicolo.tariffa_km_custom 
            ? `€ ${parseFloat(veicolo.tariffa_km_custom).toFixed(3)} (Custom)`
            : `€ ${parseFloat(veicolo.tariffa_km_aci).toFixed(3)} (ACI)`;
        
        tr.innerHTML = `
            <td><strong>${veicolo.targa}</strong></td>
            <td>${veicolo.tipo}</td>
            <td>${veicolo.marca || ''} ${veicolo.modello || ''}</td>
            <td>€ ${parseFloat(veicolo.tariffa_km_aci).toFixed(3)}</td>
            <td>${veicolo.tariffa_km_custom ? `€ ${parseFloat(veicolo.tariffa_km_custom).toFixed(3)}` : '-'}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editVeicolo(${veicolo.id})">✏️</button>
                <button class="btn btn-sm btn-danger" onclick="deleteVeicolo(${veicolo.id})">🗑️</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function renderRecentSpese(spese) {
    const container = document.getElementById('recent-spese');
    container.innerHTML = '';
    
    if (spese.length === 0) {
        container.innerHTML = '<p>Nessuna spesa recente</p>';
        return;
    }
    
    spese.forEach(spesa => {
        const div = document.createElement('div');
        div.className = 'activity-item';
        div.innerHTML = `
            <div class="activity-info">
                <div class="activity-date">${formatDate(spesa.data_spesa)}</div>
                <div class="activity-desc">${spesa.descrizione}</div>
                <div class="activity-category">
                    ${spesa.categorie ? `<span class="category-color" style="background:${spesa.categorie.colore}"></span>${spesa.categorie.nome}` : ''}
                </div>
            </div>
            <div class="activity-amount">€ ${parseFloat(spesa.importo).toFixed(2)}</div>
        `;
        container.appendChild(div);
    });
}

// ========== DASHBOARD ==========

function updateDashboardStats(stats) {
    document.getElementById('stat-spese-mese').textContent = `€ ${stats.totale_spese_mese.toFixed(2)}`;
    document.getElementById('stat-addebitabili').textContent = `€ ${stats.totale_addebitabili.toFixed(2)}`;
    document.getElementById('stat-km-mese').textContent = `${stats.totale_km_mese.toFixed(0)} km`;
    document.getElementById('stat-rimborsi-km').textContent = `€ ${stats.totale_rimborsi_km.toFixed(2)}`;
    
    renderCategorieChart(stats.spese_per_categoria);
}

function renderCategorieChart(categorie) {
    const container = document.getElementById('chart-categorie');
    container.innerHTML = '';
    
    const totale = Object.values(categorie).reduce((sum, cat) => sum + cat.totale, 0);
    
    if (totale === 0) {
        container.innerHTML = '<p style="text-align:center; padding:2rem;">Nessuna spesa nel mese corrente</p>';
        return;
    }
    
    Object.entries(categorie).forEach(([nome, data]) => {
        const percentuale = (data.totale / totale * 100).toFixed(1);
        
        const bar = document.createElement('div');
        bar.style.marginBottom = '1rem';
        bar.innerHTML = `
            <div style="display:flex; justify-content:space-between; margin-bottom:0.25rem;">
                <span>
                    <span class="category-color" style="background:${data.colore}"></span>
                    ${nome}
                </span>
                <span><strong>€ ${data.totale.toFixed(2)}</strong> (${percentuale}%)</span>
            </div>
            <div style="background:#e9ecef; height:24px; border-radius:4px; overflow:hidden;">
                <div style="background:${data.colore}; height:100%; width:${percentuale}%; transition:width 0.3s;"></div>
            </div>
        `;
        container.appendChild(bar);
    });
}

function updateKmTotals() {
    const totaleKm = currentData.chilometriche.reduce((sum, km) => sum + parseFloat(km.km_percorsi), 0);
    const totaleRimborsi = currentData.chilometriche.reduce((sum, km) => sum + parseFloat(km.rimborso_calcolato), 0);
    
    document.getElementById('totale-km-filtrato').textContent = `${totaleKm.toFixed(1)} km`;
    document.getElementById('totale-rimborsi-filtrato').textContent = `€ ${totaleRimborsi.toFixed(2)}`;
}

// ========== FORMS ==========

function initForms() {
    document.getElementById('form-spesa').addEventListener('submit', saveSpesa);
    document.getElementById('form-km').addEventListener('submit', saveKm);
    document.getElementById('form-cliente').addEventListener('submit', saveCliente);
    document.getElementById('form-veicolo').addEventListener('submit', saveVeicolo);
}

// Spesa
function openSpesaModal(id = null) {
    document.getElementById('modal-spesa').classList.add('active');
    document.getElementById('form-spesa').reset();
    document.getElementById('spesa-id').value = '';
    document.getElementById('modal-spesa-title').textContent = 'Nuova Spesa';
    document.getElementById('ocr-preview').classList.remove('active');
    
    if (id) {
        const spesa = currentData.spese.find(s => s.id === id);
        if (spesa) {
            document.getElementById('spesa-id').value = spesa.id;
            document.getElementById('spesa-data').value = spesa.data_spesa;
            document.getElementById('spesa-importo').value = spesa.importo;
            document.getElementById('spesa-categoria').value = spesa.categoria_id || '';
            document.getElementById('spesa-fornitore').value = spesa.fornitore || '';
            document.getElementById('spesa-cliente').value = spesa.cliente_id || '';
            document.getElementById('spesa-progetto').value = spesa.progetto_id || '';
            document.getElementById('spesa-descrizione').value = spesa.descrizione;
            document.getElementById('spesa-addebitabile').checked = spesa.addebitabile;
            document.getElementById('spesa-note').value = spesa.note || '';
            document.getElementById('modal-spesa-title').textContent = 'Modifica Spesa';
        }
    }
}

function closeSpesaModal() {
    document.getElementById('modal-spesa').classList.remove('active');
}

async function saveSpesa(e) {
    e.preventDefault();
    showLoader();
    
    try {
        const id = document.getElementById('spesa-id').value;
        const data = {
            data_spesa: document.getElementById('spesa-data').value,
            importo: parseFloat(document.getElementById('spesa-importo').value),
            categoria_id: parseInt(document.getElementById('spesa-categoria').value) || null,
            fornitore: document.getElementById('spesa-fornitore').value || null,
            cliente_id: parseInt(document.getElementById('spesa-cliente').value) || null,
            progetto_id: parseInt(document.getElementById('spesa-progetto').value) || null,
            descrizione: document.getElementById('spesa-descrizione').value,
            addebitabile: document.getElementById('spesa-addebitabile').checked,
            note: document.getElementById('spesa-note').value || null
        };
        
        if (id) {
            await apiCall(`/spese/${id}`, 'PUT', data);
        } else {
            await apiCall('/spese', 'POST', data);
        }
        
        closeSpesaModal();
        await loadSpese();
        await loadDashboard();
        showSuccess('Spesa salvata con successo');
    } catch (error) {
        showError('Errore nel salvare la spesa: ' + error.message);
    } finally {
        hideLoader();
    }
}

function editSpesa(id) {
    openSpesaModal(id);
}

async function deleteSpesa(id) {
    if (!confirm('Eliminare questa spesa?')) return;
    
    showLoader();
    try {
        await apiCall(`/spese/${id}`, 'DELETE');
        await loadSpese();
        await loadDashboard();
        showSuccess('Spesa eliminata');
    } catch (error) {
        showError('Errore: ' + error.message);
    } finally {
        hideLoader();
    }
}

// Chilometrica
function openKmModal(id = null) {
    document.getElementById('modal-km').classList.add('active');
    document.getElementById('form-km').reset();
    document.getElementById('km-id').value = '';
    document.getElementById('modal-km-title').textContent = 'Nuovo Viaggio';
    document.getElementById('km-rimborso').value = '';
    
    if (id) {
        const km = currentData.chilometriche.find(k => k.id === id);
        if (km) {
            document.getElementById('km-id').value = km.id;
            document.getElementById('km-data').value = km.data_viaggio;
            document.getElementById('km-veicolo').value = km.veicolo_id || '';
            document.getElementById('km-partenza').value = km.partenza;
            document.getElementById('km-arrivo').value = km.arrivo;
            document.getElementById('km-percorsi').value = km.km_percorsi;
            document.getElementById('km-tariffa').value = km.tariffa_applicata;
            document.getElementById('km-cliente').value = km.cliente_id || '';
            document.getElementById('km-progetto').value = km.progetto_id || '';
            document.getElementById('km-addebitabile').checked = km.addebitabile;
            document.getElementById('km-descrizione').value = km.descrizione || '';
            calcolaRimborso();
            document.getElementById('modal-km-title').textContent = 'Modifica Viaggio';
        }
    }
}

function closeKmModal() {
    document.getElementById('modal-km').classList.remove('active');
}

function updateTariffaKm() {
    const select = document.getElementById('km-veicolo');
    const option = select.options[select.selectedIndex];
    if (option && option.dataset.tariffa) {
        document.getElementById('km-tariffa').value = option.dataset.tariffa;
        calcolaRimborso();
    }
}

function calcolaRimborso() {
    const km = parseFloat(document.getElementById('km-percorsi').value) || 0;
    const tariffa = parseFloat(document.getElementById('km-tariffa').value) || 0;
    const rimborso = km * tariffa;
    document.getElementById('km-rimborso').value = `€ ${rimborso.toFixed(2)}`;
}

async function saveKm(e) {
    e.preventDefault();
    showLoader();
    
    try {
        const id = document.getElementById('km-id').value;
        const data = {
            data_viaggio: document.getElementById('km-data').value,
            veicolo_id: parseInt(document.getElementById('km-veicolo').value) || null,
            partenza: document.getElementById('km-partenza').value,
            arrivo: document.getElementById('km-arrivo').value,
            km_percorsi: parseFloat(document.getElementById('km-percorsi').value),
            tariffa_applicata: parseFloat(document.getElementById('km-tariffa').value),
            cliente_id: parseInt(document.getElementById('km-cliente').value) || null,
            progetto_id: parseInt(document.getElementById('km-progetto').value) || null,
            addebitabile: document.getElementById('km-addebitabile').checked,
            descrizione: document.getElementById('km-descrizione').value || null
        };
        
        if (id) {
            await apiCall(`/chilometriche/${id}`, 'PUT', data);
        } else {
            await apiCall('/chilometriche', 'POST', data);
        }
        
        closeKmModal();
        await loadChilometriche();
        await loadDashboard();
        showSuccess('Viaggio salvato con successo');
    } catch (error) {
        showError('Errore: ' + error.message);
    } finally {
        hideLoader();
    }
}

function editKm(id) {
    openKmModal(id);
}

async function deleteKm(id) {
    if (!confirm('Eliminare questo viaggio?')) return;
    
    showLoader();
    try {
        await apiCall(`/chilometriche/${id}`, 'DELETE');
        await loadChilometriche();
        await loadDashboard();
        showSuccess('Viaggio eliminato');
    } catch (error) {
        showError('Errore: ' + error.message);
    } finally {
        hideLoader();
    }
}

// Cliente
function openClienteModal(id = null) {
    document.getElementById('modal-cliente').classList.add('active');
    document.getElementById('form-cliente').reset();
    document.getElementById('cliente-id').value = '';
    document.getElementById('modal-cliente-title').textContent = 'Nuovo Cliente';
    
    if (id) {
        const cliente = currentData.clienti.find(c => c.id === id);
        if (cliente) {
            document.getElementById('cliente-id').value = cliente.id;
            document.getElementById('cliente-nome').value = cliente.nome;
            document.getElementById('cliente-codice').value = cliente.codice || '';
            document.getElementById('cliente-piva').value = cliente.partita_iva || '';
            document.getElementById('cliente-email').value = cliente.email || '';
            document.getElementById('cliente-telefono').value = cliente.telefono || '';
            document.getElementById('modal-cliente-title').textContent = 'Modifica Cliente';
        }
    }
}

function closeClienteModal() {
    document.getElementById('modal-cliente').classList.remove('active');
}

async function saveCliente(e) {
    e.preventDefault();
    showLoader();
    
    try {
        const id = document.getElementById('cliente-id').value;
        const data = {
            nome: document.getElementById('cliente-nome').value,
            codice: document.getElementById('cliente-codice').value || null,
            partita_iva: document.getElementById('cliente-piva').value || null,
            email: document.getElementById('cliente-email').value || null,
            telefono: document.getElementById('cliente-telefono').value || null
        };
        
        if (id) {
            await apiCall(`/clienti/${id}`, 'PUT', data);
        } else {
            await apiCall('/clienti', 'POST', data);
        }
        
        closeClienteModal();
        await loadClienti();
        await loadClientiTable();
        showSuccess('Cliente salvato con successo');
    } catch (error) {
        showError('Errore: ' + error.message);
    } finally {
        hideLoader();
    }
}

function editCliente(id) {
    openClienteModal(id);
}

async function deleteCliente(id) {
    if (!confirm('Disattivare questo cliente?')) return;
    
    showLoader();
    try {
        await apiCall(`/clienti/${id}`, 'DELETE');
        await loadClienti();
        await loadClientiTable();
        showSuccess('Cliente disattivato');
    } catch (error) {
        showError('Errore: ' + error.message);
    } finally {
        hideLoader();
    }
}

// Veicolo
function openVeicoloModal(id = null) {
    document.getElementById('modal-veicolo').classList.add('active');
    document.getElementById('form-veicolo').reset();
    document.getElementById('veicolo-id').value = '';
    document.getElementById('modal-veicolo-title').textContent = 'Nuovo Veicolo';
    
    if (id) {
        const veicolo = currentData.veicoli.find(v => v.id === id);
        if (veicolo) {
            document.getElementById('veicolo-id').value = veicolo.id;
            document.getElementById('veicolo-targa').value = veicolo.targa;
            document.getElementById('veicolo-tipo').value = veicolo.tipo;
            document.getElementById('veicolo-marca').value = veicolo.marca || '';
            document.getElementById('veicolo-modello').value = veicolo.modello || '';
            document.getElementById('veicolo-tariffa-aci').value = veicolo.tariffa_km_aci;
            document.getElementById('veicolo-tariffa-custom').value = veicolo.tariffa_km_custom || '';
            document.getElementById('veicolo-usa-custom').checked = veicolo.usa_tariffa_custom;
            document.getElementById('modal-veicolo-title').textContent = 'Modifica Veicolo';
        }
    }
}

function closeVeicoloModal() {
    document.getElementById('modal-veicolo').classList.remove('active');
}

async function saveVeicolo(e) {
    e.preventDefault();
    showLoader();
    
    try {
        const id = document.getElementById('veicolo-id').value;
        const data = {
            targa: document.getElementById('veicolo-targa').value,
            tipo: document.getElementById('veicolo-tipo').value,
            marca: document.getElementById('veicolo-marca').value || null,
            modello: document.getElementById('veicolo-modello').value || null,
            tariffa_km_aci: parseFloat(document.getElementById('veicolo-tariffa-aci').value),
            tariffa_km_custom: parseFloat(document.getElementById('veicolo-tariffa-custom').value) || null,
            usa_tariffa_custom: document.getElementById('veicolo-usa-custom').checked
        };
        
        if (id) {
            await apiCall(`/veicoli/${id}`, 'PUT', data);
        } else {
            await apiCall('/veicoli', 'POST', data);
        }
        
        closeVeicoloModal();
        await loadVeicoli();
        await loadVeicoliTable();
        showSuccess('Veicolo salvato con successo');
    } catch (error) {
        showError('Errore: ' + error.message);
    } finally {
        hideLoader();
    }
}

function editVeicolo(id) {
    openVeicoloModal(id);
}

async function deleteVeicolo(id) {
    if (!confirm('Disattivare questo veicolo?')) return;
    
    showLoader();
    try {
        await apiCall(`/veicoli/${id}`, 'DELETE');
        await loadVeicoli();
        await loadVeicoliTable();
        showSuccess('Veicolo disattivato');
    } catch (error) {
        showError('Errore: ' + error.message);
    } finally {
        hideLoader();
    }
}

// ========== UPLOAD RICEVUTA E OCR ==========

async function uploadRicevuta(input) {
    if (!input.files || !input.files[0]) return;
    
    showLoader();
    const preview = document.getElementById('ocr-preview');
    
    try {
        const formData = new FormData();
        formData.append('image', input.files[0]);
        
        const response = await fetch(`${API_URL}/upload-ricevuta`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success && result.ocr_data) {
            // Compila campi automaticamente
            if (result.ocr_data.importo) {
                document.getElementById('spesa-importo').value = result.ocr_data.importo;
            }
            if (result.ocr_data.data) {
                // Prova a convertire la data
                const dateMatch = result.ocr_data.data.match(/(\d{2})[\/\-\.](\d{2})[\/\-\.](\d{4})/);
                if (dateMatch) {
                    const [, giorno, mese, anno] = dateMatch;
                    document.getElementById('spesa-data').value = `${anno}-${mese}-${giorno}`;
                }
            }
            
            // Mostra anteprima OCR
            preview.innerHTML = `
                <h4>Dati estratti da OCR:</h4>
                <pre>${JSON.stringify(result.ocr_data, null, 2)}</pre>
            `;
            preview.classList.add('active');
            
            showSuccess('Ricevuta scansionata con successo!');
        }
    } catch (error) {
        showError('Errore nella scansione: ' + error.message);
    } finally {
        hideLoader();
    }
}

// ========== FILTRI ==========

function applySpeseFiltri() {
    loadSpese();
}

function applyKmFiltri() {
    loadChilometriche();
}

// ========== EXPORT ==========

async function exportSpese() {
    showLoader();
    
    try {
        const da = document.getElementById('export-spese-da').value;
        const a = document.getElementById('export-spese-a').value;
        const cliente = document.getElementById('export-spese-cliente').value;
        
        const response = await fetch(`${API_URL}/export/excel`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                tipo: 'spese',
                filtri: { data_inizio: da, data_fine: a, cliente_id: cliente }
            })
        });
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `spese_${new Date().toISOString().split('T')[0]}.xlsx`;
        a.click();
        
        showSuccess('Export completato!');
    } catch (error) {
        showError('Errore export: ' + error.message);
    } finally {
        hideLoader();
    }
}

async function exportKm() {
    showLoader();
    
    try {
        const da = document.getElementById('export-km-da').value;
        const a = document.getElementById('export-km-a').value;
        
        const response = await fetch(`${API_URL}/export/excel`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                tipo: 'chilometriche',
                filtri: { data_inizio: da, data_fine: a }
            })
        });
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chilometriche_${new Date().toISOString().split('T')[0]}.xlsx`;
        a.click();
        
        showSuccess('Export completato!');
    } catch (error) {
        showError('Errore export: ' + error.message);
    } finally {
        hideLoader();
    }
}

// ========== UTILS ==========

function showLoader() {
    document.getElementById('loader').classList.remove('hidden');
}

function hideLoader() {
    document.getElementById('loader').classList.add('hidden');
}

function showSuccess(message) {
    alert(message); // TODO: sostituire con toast notification
}

function showError(message) {
    alert('ERRORE: ' + message); // TODO: sostituire con toast notification
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
}
