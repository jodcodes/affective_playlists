/**
 * affective_playlists - Browser Frontend
 * Main application logic and state management
 */

// ============================================================================
// Global State
// ============================================================================

const app = {
    config: {
        apiBase: '/api',
        pollInterval: 2000, // ms
        timeout: 30000, // ms
    },
    state: {
        currentView: 'dashboard',
        theme: localStorage.getItem('affective_theme') || 'light',
        isOnline: true,
        playlists: [],
        enrichmentRunning: false,
        enrichmentProgress: 0,
    },
    async api(endpoint, options = {}) {
        const url = `${this.config.apiBase}${endpoint}`;
        const timeout = options.timeout || this.config.timeout;

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeout);

            const response = await fetch(url, {
                method: options.method || 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
                body: options.body ? JSON.stringify(options.body) : undefined,
                signal: controller.signal,
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            app.state.isOnline = false;
            app.updateStatus();
            throw error;
        }
    },
};

// ============================================================================
// DOM Elements
// ============================================================================

const DOM = {
    navbar: () => document.querySelector('.navbar'),
    pageTitle: () => document.getElementById('pageTitle'),
    statusIndicator: () => document.getElementById('statusIndicator'),
    alertBanner: () => document.getElementById('alertBanner'),
    views: () => document.querySelectorAll('.view'),
    loadingSpinner: () => document.getElementById('loadingSpinner'),
    navLinks: () => document.querySelectorAll('.nav-link'),
    themeToggle: () => document.getElementById('themeToggle'),
    menuToggle: () => document.getElementById('menuToggle'),
    navMenu: () => document.getElementById('navMenu'),

    // Dashboard
    statPlaylists: () => document.getElementById('statPlaylists'),
    statTracks: () => document.getElementById('statTracks'),
    statClassified: () => document.getElementById('statClassified'),
    statPlatform: () => document.getElementById('statPlatform'),
    recentActivity: () => document.getElementById('recentActivity'),

    // Playlists
    playlistsBody: () => document.getElementById('playlistsBody'),
    playlistsTable: () => document.getElementById('playlistsTable'),
    playlistSearch: () => document.getElementById('playlistSearch'),
    genreFilter: () => document.getElementById('genreFilter'),

    // Enrichment
    startEnrichmentBtn: () => document.getElementById('startEnrichmentBtn'),
    cancelEnrichmentBtn: () => document.getElementById('cancelEnrichmentBtn'),
    enrichmentProgress: () => document.getElementById('enrichmentProgress'),
    enrichmentProgressBar: () => document.getElementById('enrichmentProgressBar'),
    enrichmentStatus: () => document.getElementById('enrichmentStatus'),
    enrichmentResults: () => document.getElementById('enrichmentResults'),

    // Analysis
    startAnalysisBtn: () => document.getElementById('startAnalysisBtn'),
    analyzePlaylists: () => document.getElementById('analyzePlaylists'),
    analysisResults: () => document.getElementById('analysisResults'),
    temperamentChart: () => document.getElementById('temperamentChart'),

    // Organization
    reviewChangesBtn: () => document.getElementById('reviewChangesBtn'),
    platformWarning: () => document.getElementById('platformWarning'),
    organizationPreview: () => document.getElementById('organizationPreview'),
    previewTable: () => document.getElementById('previewTable'),
    previewBody: () => document.getElementById('previewBody'),
    confirmMoveBtn: () => document.getElementById('confirmMoveBtn'),
    cancelMoveBtn: () => document.getElementById('cancelMoveBtn'),

    // Modal
    confirmModal: () => document.getElementById('confirmModal'),
    modalBackdrop: () => document.getElementById('modalBackdrop'),
    confirmTitle: () => document.getElementById('confirmTitle'),
    confirmMessage: () => document.getElementById('confirmMessage'),
    confirmYes: () => document.getElementById('confirmYes'),
    confirmNo: () => document.getElementById('confirmNo'),
};

// ============================================================================
// UI Utilities
// ============================================================================

function showAlert(message, type = 'info') {
    const banner = DOM.alertBanner();
    banner.textContent = message;
    banner.className = `alert alert-${type}`;
    setTimeout(() => {
        banner.classList.add('alert-hidden');
    }, 5000);
}

function showSpinner(show = true) {
    const spinner = DOM.loadingSpinner();
    if (show) {
        spinner.classList.remove('hidden');
    } else {
        spinner.classList.add('hidden');
    }
}

function showView(viewName) {
    DOM.views().forEach(view => view.classList.remove('active'));
    const view = document.getElementById(viewName);
    if (view) {
        view.classList.add('active');
        app.state.currentView = viewName;
        localStorage.setItem('affective_view', viewName);

        // Update page title
        const titles = {
            dashboard: 'Dashboard',
            playlists: 'Playlists',
            enrich: 'Enrich Metadata',
            analyze: 'Analyze Mood',
            organize: 'Organize Playlists',
        };
        DOM.pageTitle().textContent = titles[viewName] || viewName;
    }
}

function showModal(title, message) {
    return new Promise((resolve) => {
        DOM.confirmTitle().textContent = title;
        DOM.confirmMessage().textContent = message;
        DOM.confirmModal().classList.remove('hidden');
        DOM.modalBackdrop().classList.remove('hidden');

        DOM.confirmYes().onclick = () => {
            closeModal();
            resolve(true);
        };

        DOM.confirmNo().onclick = () => {
            closeModal();
            resolve(false);
        };

        DOM.modalBackdrop().onclick = () => {
            closeModal();
            resolve(false);
        };
    });
}

function closeModal() {
    DOM.confirmModal().classList.add('hidden');
    DOM.modalBackdrop().classList.add('hidden');
}

function updateStatus() {
    const indicator = DOM.statusIndicator();
    if (app.state.isOnline) {
        indicator.className = 'status-online';
        indicator.textContent = '● Online';
    } else {
        indicator.className = 'status-offline';
        indicator.textContent = '● Offline';
    }
}

// ============================================================================
// Theme Management
// ============================================================================

function initTheme() {
    const theme = app.state.theme;
    document.documentElement.classList.toggle('dark', theme === 'dark');
    updateThemeToggleButton();
}

function toggleTheme() {
    app.state.theme = app.state.theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('affective_theme', app.state.theme);
    document.documentElement.classList.toggle('dark');
    updateThemeToggleButton();
}

function updateThemeToggleButton() {
    const btn = DOM.themeToggle();
    btn.textContent = app.state.theme === 'dark' ? '☀️' : '🌙';
}

// ============================================================================
// Dashboard
// ============================================================================

async function loadDashboard() {
    try {
        showSpinner(true);
        const health = await app.api('/health');

        DOM.statPlaylists().textContent = health.playlists_count || 0;
        DOM.statTracks().textContent = health.tracks_count || 0;
        DOM.statClassified().textContent = health.playlists_count || 0; // TODO: track classified
        DOM.statPlatform().textContent = health.platform.includes('darwin') ? 'macOS' : 'Other';

        app.state.isOnline = true;
        updateStatus();
    } catch (error) {
        showAlert('Failed to load dashboard: ' + error.message, 'danger');
    } finally {
        showSpinner(false);
    }
}

// ============================================================================
// Playlists
// ============================================================================

async function loadPlaylists() {
    try {
        showSpinner(true);
        const playlists = await app.api('/playlists');
        app.state.playlists = playlists;

        renderPlaylistsTable(playlists);
        app.state.isOnline = true;
        updateStatus();
    } catch (error) {
        showAlert('Failed to load playlists: ' + error.message, 'danger');
    } finally {
        showSpinner(false);
    }
}

function renderPlaylistsTable(playlists) {
    const body = DOM.playlistsBody();
    if (!playlists || playlists.length === 0) {
        body.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No playlists found. Open Music.app and allow Automation access for Terminal/Python in macOS Privacy settings.</td></tr>';
        return;
    }

    body.innerHTML = playlists.map(p => `
        <tr>
            <td><strong>${p.name || 'Unnamed'}</strong></td>
            <td>${p.track_count || 0}</td>
            <td>${p.genre ? `<span style="color: var(--color-primary);">${p.genre}</span>` : '-'}</td>
            <td>${p.classified ? '✓ Classified' : '-'}</td>
            <td>
                <div class="table-actions">
                    <button class="btn btn-primary btn-sm" onclick="classifyPlaylist('${p.id}')">Classify</button>
                </div>
            </td>
        </tr>
    `).join('');
}

async function classifyPlaylist(playlistId) {
    try {
        showSpinner(true);
        const result = await app.api(`/playlists/${playlistId}/classify`, { method: 'POST' });

        if (result.success) {
            showAlert(`✓ Classified as ${result.genre}`, 'success');
            loadPlaylists(); // Reload
        } else {
            showAlert('Could not classify this playlist', 'warning');
        }
    } catch (error) {
        showAlert('Classification failed: ' + error.message, 'danger');
    } finally {
        showSpinner(false);
    }
}

// ============================================================================
// Enrichment
// ============================================================================

async function startEnrichment() {
    try {
        showSpinner(true);
        const result = await app.api('/enrichment/start', { method: 'POST' });

        if (result.success) {
            app.state.enrichmentRunning = true;
            DOM.startEnrichmentBtn().style.display = 'none';
            DOM.enrichmentProgress().style.display = 'block';
            showAlert('Enrichment started...', 'info');
            pollEnrichmentProgress();
        }
    } catch (error) {
        showAlert('Failed to start enrichment: ' + error.message, 'danger');
    } finally {
        showSpinner(false);
    }
}

async function pollEnrichmentProgress() {
    if (!app.state.enrichmentRunning) return;

    try {
        const status = await app.api('/enrichment/status');

        if (status.running) {
            app.state.enrichmentProgress = status.progress || 0;
            const progressBar = DOM.enrichmentProgressBar();
            progressBar.style.width = app.state.enrichmentProgress + '%';
            progressBar.textContent = app.state.enrichmentProgress + '%';

            const statusText = status.current_operation || 'Processing...';
            DOM.enrichmentStatus().textContent = statusText;

            setTimeout(pollEnrichmentProgress, app.config.pollInterval);
        } else if (status.progress === 100) {
            // Completed
            app.state.enrichmentRunning = false;
            showAlert('✓ Enrichment completed!', 'success');
            DOM.enrichmentProgress().style.display = 'none';
            loadEnrichmentResults();
        }
    } catch (error) {
        showAlert('Error polling progress: ' + error.message, 'danger');
    }
}

async function cancelEnrichment() {
    try {
        await app.api('/enrichment/cancel', { method: 'POST' });
        app.state.enrichmentRunning = false;
        DOM.enrichmentProgress().style.display = 'none';
        DOM.startEnrichmentBtn().style.display = 'block';
        showAlert('✓ Enrichment cancelled', 'success');
    } catch (error) {
        showAlert('Failed to cancel enrichment: ' + error.message, 'danger');
    }
}

async function loadEnrichmentResults() {
    try {
        const results = await app.api('/enrichment/results');

        if (results.tracks_enriched > 0) {
            DOM.enrichmentResults().style.display = 'block';
            DOM.enrichmentResultsSummary().textContent = 
                `✓ Enriched ${results.tracks_enriched} tracks with ${results.fields_added} fields in ${results.duration_seconds}s`;
        }
    } catch (error) {
        console.error('Failed to load enrichment results:', error);
    }
}

// ============================================================================
// Analysis (Temperament)
// ============================================================================

async function startAnalysis() {
    try {
        const select = DOM.analyzePlaylists();
        const selectedIds = Array.from(select.selectedOptions).map(o => o.value).filter(Boolean);

        if (!selectedIds.length) {
            showAlert('Please select at least one playlist', 'warning');
            return;
        }

        showSpinner(true);
        const result = await app.api('/temperament/classify', {
            method: 'POST',
            body: { playlist_ids: selectedIds },
        });

        if (result.success) {
            showAlert('Analysis started...', 'info');
            setTimeout(loadAnalysisResults, 2000); // Wait for analysis to complete
        }
    } catch (error) {
        showAlert('Failed to start analysis: ' + error.message, 'danger');
    } finally {
        showSpinner(false);
    }
}

async function loadAnalysisResults() {
    try {
        const results = await app.api('/temperament/results');

        if (results.length > 0) {
            DOM.analysisResults().style.display = 'block';
            renderTemperamentChart(results);
        }
    } catch (error) {
        console.error('Failed to load analysis results:', error);
    }
}

function renderTemperamentChart(results) {
    const chart = DOM.temperamentChart();
    chart.innerHTML = results.map(r => `
        <div class="temperament-item ${r.primary_temperament}">
            <div class="temperament-track-name">${r.track_name}</div>
            <div class="temperament-value">
                ${r.primary_temperament}
                <span class="confidence-badge">${(r.confidence * 100).toFixed(0)}%</span>
            </div>
        </div>
    `).join('');
}

// ============================================================================
// Organization
// ============================================================================

async function reviewChanges() {
    try {
        showSpinner(true);
        const result = await app.api('/playlists/organize', {
            method: 'POST',
            body: { dry_run: true },
        });

        if (result.changes && result.changes.length > 0) {
            renderOrganizationPreview(result.changes, result.total_changes);
            DOM.organizationPreview().style.display = 'block';
        } else {
            showAlert('No playlists to organize', 'info');
        }
    } catch (error) {
        showAlert('Failed to review changes: ' + error.message, 'danger');
    } finally {
        showSpinner(false);
    }
}

function renderOrganizationPreview(changes, total) {
    const body = DOM.previewBody();
    body.innerHTML = changes.map(change => `
        <tr>
            <td>${change.playlist_id}</td>
            <td>${change.current_location}</td>
            <td><strong>${change.proposed_location}</strong></td>
            <td>${change.genre}</td>
        </tr>
    `).join('');

    document.getElementById('previewSummary').textContent = 
        `Ready to move ${total} playlist${total !== 1 ? 's' : ''} to organized folders.`;
}

async function confirmMove() {
    const ok = await showModal(
        'Confirm Playlist Organization',
        'This will move playlists to their genre folders. Continue?'
    );

    if (!ok) return;

    try {
        showSpinner(true);
        const result = await app.api('/playlists/move', {
            method: 'POST',
            body: { confirmed: true },
        });

        showAlert(`✓ Moved ${result.moved} playlists successfully!`, 'success');
        DOM.organizationPreview().style.display = 'none';
        loadPlaylists();
    } catch (error) {
        showAlert('Failed to move playlists: ' + error.message, 'danger');
    } finally {
        showSpinner(false);
    }
}

// ============================================================================
// Event Listeners
// ============================================================================

function setupEventListeners() {
    // Navigation
    DOM.navLinks().forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const view = link.dataset.view;
            DOM.navLinks().forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            showView(view);

            // Load view-specific data
            if (view === 'playlists') loadPlaylists();
            if (view === 'dashboard') loadDashboard();
        });
    });

    // Mobile menu
    DOM.menuToggle().addEventListener('click', () => {
        DOM.navMenu().classList.toggle('show');
    });

    // Theme toggle
    DOM.themeToggle().addEventListener('click', toggleTheme);

    // Dashboard actions
    document.querySelectorAll('[data-action]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const action = btn.dataset.action;
            const views = { classify: 'playlists', enrich: 'enrich', analyze: 'analyze', organize: 'organize' };
            if (views[action]) showView(views[action]);
        });
    });

    // Enrichment
    DOM.startEnrichmentBtn().addEventListener('click', startEnrichment);
    DOM.cancelEnrichmentBtn().addEventListener('click', cancelEnrichment);

    // Analysis
    DOM.startAnalysisBtn().addEventListener('click', startAnalysis);

    // Organization
    DOM.reviewChangesBtn().addEventListener('click', reviewChanges);
    DOM.confirmMoveBtn().addEventListener('click', confirmMove);
    DOM.cancelMoveBtn().addEventListener('click', () => {
        DOM.organizationPreview().style.display = 'none';
    });
}

// ============================================================================
// Initialization
// ============================================================================

async function init() {
    try {
        // Setup theme
        initTheme();

        // Setup event listeners
        setupEventListeners();

        // Load initial data
        await app.api('/config');
        app.state.isOnline = true;
        updateStatus();

        // Load dashboard
        loadDashboard();

        // Restore last view
        const lastView = localStorage.getItem('affective_view') || 'dashboard';
        showView(lastView);
    } catch (error) {
        showAlert('Failed to initialize application: ' + error.message, 'danger');
        app.state.isOnline = false;
        updateStatus();
    }
}

// Start application when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
