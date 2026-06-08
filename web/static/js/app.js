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
            updateStatus();
            throw error;
        }
    },
};

let curationPreview = null;
let curationPreviewLoading = false;
let curationApplyInFlight = false;

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

    // Curation
    curationRefreshBtn: () => document.getElementById('curation-refresh-btn'),
    curationDryRunBtn: () => document.getElementById('curation-dry-run-btn'),
    curationApplyBtn: () => document.getElementById('curation-apply-btn'),
    curationSummary: () => document.getElementById('curation-summary'),
    curationGenreTree: () => document.getElementById('curation-genre-tree'),
    curationReviewPanel: () => document.getElementById('curation-review-panel'),
    curationChangePanel: () => document.getElementById('curation-change-panel'),

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
    const viewIds = {
        curation: 'curation-view',
    };
    const view = document.getElementById(viewIds[viewName] || viewName);
    if (view) {
        view.classList.add('active');
        DOM.navLinks().forEach(link => {
            link.classList.toggle('active', link.dataset.view === viewName);
        });
        app.state.currentView = viewName;
        localStorage.setItem('affective_view', viewName);

        // Update page title
        const titles = {
            dashboard: 'Dashboard',
            playlists: 'Playlists',
            enrich: 'Enrich Metadata',
            analyze: 'Analyze Mood',
            organize: 'Organize Playlists',
            curation: 'Curation Review',
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

function asArray(value) {
    return Array.isArray(value) ? value : [];
}

function asNumber(value, fallback = 0) {
    const number = Number(value);
    return Number.isFinite(number) ? number : fallback;
}

function textValue(value, fallback = '') {
    if (value === null || value === undefined || value === '') {
        return fallback;
    }
    return String(value);
}

function appendElement(parent, tagName, className, text) {
    const element = document.createElement(tagName);
    if (className) {
        element.className = className;
    }
    if (text !== undefined && text !== null) {
        element.textContent = String(text);
    }
    parent.appendChild(element);
    return element;
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
// Curation Review
// ============================================================================

const CURATION_TEMPERS = ['Frolic', 'Woe', 'Dread', 'Malice'];

function setCurationButtonsState() {
    const isBusy = curationPreviewLoading || curationApplyInFlight;
    const refreshBtn = DOM.curationRefreshBtn();
    const dryRunBtn = DOM.curationDryRunBtn();
    const applyBtn = DOM.curationApplyBtn();

    if (refreshBtn) {
        refreshBtn.disabled = isBusy;
    }
    if (dryRunBtn) {
        dryRunBtn.disabled = isBusy;
    }
    if (applyBtn) {
        applyBtn.disabled = isBusy || !curationPreview;
    }
}

async function loadCurationPreview() {
    if (curationPreviewLoading || curationApplyInFlight) {
        return;
    }

    curationPreviewLoading = true;
    setCurationButtonsState();

    try {
        showSpinner(true);
        const preview = await app.api('/curation/preview?scope=fav_songs');

        curationPreview = preview;
        renderCurationPreview(preview);
        app.state.isOnline = true;
        updateStatus();
    } catch (error) {
        curationPreview = null;
        renderCurationError('Unable to load curation preview.');
        showAlert('Failed to load curation preview: ' + error.message, 'danger');
    } finally {
        curationPreviewLoading = false;
        setCurationButtonsState();
        showSpinner(false);
    }
}

function groupCurationAssignments(assignments) {
    const groupsByGenre = new Map();

    assignments.forEach(assignment => {
        if (!assignment || typeof assignment !== 'object') {
            return;
        }

        const genre = textValue(assignment.genre_label || assignment.genre, 'Other');
        if (!groupsByGenre.has(genre)) {
            groupsByGenre.set(genre, []);
        }
        groupsByGenre.get(genre).push(assignment);
    });

    return Array.from(groupsByGenre.entries())
        .sort(([left], [right]) => left.localeCompare(right))
        .map(([genre, items], index) => ({
            genre,
            id: `curation-genre-${index}`,
            items: items.slice().sort((left, right) => {
                const leftName = textValue((left && left.item_name) || (left && left.name), 'Unnamed');
                const rightName = textValue((right && right.item_name) || (right && right.name), 'Unnamed');
                return leftName.localeCompare(rightName);
            }),
        }));
}

function renderCurationPreview(preview) {
    const summary = DOM.curationSummary();
    const tree = DOM.curationGenreTree();
    const reviewPanel = DOM.curationReviewPanel();
    const changePanel = DOM.curationChangePanel();

    if (!summary || !tree || !reviewPanel || !changePanel) {
        return;
    }

    const assignments = asArray(preview && preview.assignments);
    const changes = asArray(preview && preview.changes);
    const skippedTracks = asArray(preview && preview.skipped_tracks);
    const groups = groupCurationAssignments(assignments);
    const totalAssignments = asNumber(
        preview && preview.total_assignments !== undefined
            ? preview.total_assignments
            : assignments.length
    );
    const totalChanges = asNumber(
        preview && preview.total_changes !== undefined
            ? preview.total_changes
            : changes.length
    );
    const totalSkipped = asNumber(
        preview && preview.total_skipped !== undefined
            ? preview.total_skipped
            : skippedTracks.length
    );

    renderCurationSummary(summary, {
        totalAssignments,
        totalGenres: groups.length,
        totalChanges,
        totalSkipped,
    });
    renderCurationGenreTree(tree, groups);
    renderCurationReviewPanel(reviewPanel, groups);
    renderCurationChangePanel(changePanel, changes, skippedTracks, totalSkipped);
}

function renderCurationSummary(summary, counts) {
    summary.replaceChildren();

    [
        ['Assignments', counts.totalAssignments],
        ['Genres', counts.totalGenres],
        ['Dry-run Changes', counts.totalChanges],
        ['Skipped', counts.totalSkipped],
    ].forEach(([label, value]) => {
        const item = appendElement(summary, 'div', 'curation-summary-item');
        appendElement(item, 'div', 'curation-summary-number', value);
        appendElement(item, 'div', 'curation-summary-label', label);
    });
}

function renderCurationGenreTree(tree, groups) {
    tree.replaceChildren();
    appendElement(tree, 'h3', null, 'Genres');

    if (!groups.length) {
        appendElement(tree, 'p', 'text-muted', 'No genres found in this preview.');
        return;
    }

    const list = appendElement(tree, 'div', 'curation-genre-list');
    groups.forEach(group => {
        const button = appendElement(list, 'button', 'curation-genre-link');
        button.type = 'button';
        const label = appendElement(button, 'span', null, group.genre);
        label.title = group.genre;
        appendElement(button, 'span', 'curation-count-badge', group.items.length);
        button.addEventListener('click', () => {
            const target = document.getElementById(group.id);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
}

function renderCurationReviewPanel(panel, groups) {
    panel.replaceChildren();

    if (!groups.length) {
        const empty = appendElement(panel, 'div', 'card curation-empty-state');
        appendElement(empty, 'h3', null, 'No Favourite Songs Found');
        appendElement(empty, 'p', 'text-muted', 'The preview returned no curation assignments.');
        return;
    }

    groups.forEach(group => {
        const section = appendElement(panel, 'section', 'card curation-genre-section');
        section.id = group.id;
        const header = appendElement(section, 'div', 'curation-genre-header');
        appendElement(header, 'h3', null, group.genre);
        appendElement(header, 'span', 'curation-count-badge', group.items.length);

        const grid = appendElement(section, 'div', 'curation-temper-grid');
        CURATION_TEMPERS.forEach(temper => {
            const column = appendElement(grid, 'div', 'curation-temper-column');
            const columnHeader = appendElement(column, 'div', 'curation-temper-header');
            const temperItems = group.items.filter(item => textValue(item && item.temperament) === temper);

            appendElement(columnHeader, 'h4', null, temper);
            appendElement(columnHeader, 'span', 'curation-count-badge', temperItems.length);

            if (!temperItems.length) {
                appendElement(column, 'p', 'curation-empty-column', 'No tracks');
                return;
            }

            temperItems.forEach(item => {
                const card = appendElement(column, 'div', 'curation-track-card');
                const itemName = textValue((item && item.item_name) || (item && item.name), 'Unnamed track');
                const targetPath = asArray(item && item.target_path).map(part => textValue(part)).join(' / ');

                appendElement(card, 'div', 'curation-track-name', itemName);
                appendElement(card, 'div', 'curation-target-path', targetPath || 'No target path');
            });
        });
    });
}

function renderCurationChangePanel(panel, changes, skippedTracks, totalSkipped) {
    panel.replaceChildren();
    appendElement(panel, 'h3', null, 'Dry-run Changes');

    if (!changes.length) {
        appendElement(panel, 'p', 'text-muted', 'No dry-run changes returned.');
    } else {
        const list = appendElement(panel, 'div', 'curation-change-list');
        changes.forEach(change => {
            const item = appendElement(list, 'div', 'curation-change-item');
            const action = textValue(change && change.action, 'change');
            const description = textValue(change && change.description, 'Change planned');
            const path = asArray(change && change.path).map(part => textValue(part)).join(' / ');

            appendElement(item, 'span', 'curation-action-badge', action.replace(/_/g, ' '));
            appendElement(item, 'div', 'curation-change-description', description);
            if (path) {
                appendElement(item, 'div', 'curation-target-path', path);
            }
        });
    }

    if (totalSkipped > 0 || skippedTracks.length > 0) {
        const skipped = appendElement(panel, 'div', 'curation-skipped-section');
        appendElement(skipped, 'h3', null, `Skipped Tracks (${totalSkipped || skippedTracks.length})`);

        if (!skippedTracks.length) {
            appendElement(skipped, 'p', 'text-muted', 'Skipped track details were not returned.');
            return;
        }

        skippedTracks.forEach(track => {
            const row = appendElement(skipped, 'div', 'curation-skipped-item');
            const name = textValue((track && track.name) || (track && track.item_name), 'Unnamed track');
            const details = [
                textValue(track && track.artist),
                textValue(track && track.genre),
                textValue(track && track.reason, 'skipped'),
            ].filter(Boolean).join(' - ');

            appendElement(row, 'div', 'curation-track-name', name);
            appendElement(row, 'div', 'curation-target-path', details);
        });
    }
}

function renderCurationError(message) {
    const summary = DOM.curationSummary();
    const tree = DOM.curationGenreTree();
    const reviewPanel = DOM.curationReviewPanel();
    const changePanel = DOM.curationChangePanel();

    if (!summary || !tree || !reviewPanel || !changePanel) {
        return;
    }

    renderCurationSummary(summary, {
        totalAssignments: 0,
        totalGenres: 0,
        totalChanges: 0,
        totalSkipped: 0,
    });

    tree.replaceChildren();
    appendElement(tree, 'h3', null, 'Genres');
    appendElement(tree, 'p', 'text-muted', 'No preview loaded.');

    reviewPanel.replaceChildren();
    const empty = appendElement(reviewPanel, 'div', 'card curation-empty-state');
    appendElement(empty, 'h3', null, 'Preview Unavailable');
    appendElement(empty, 'p', 'text-muted', message);

    changePanel.replaceChildren();
    appendElement(changePanel, 'h3', null, 'Dry-run Changes');
    appendElement(changePanel, 'p', 'text-muted', 'No changes loaded.');
}

async function applyFavSongsCuration() {
    if (curationApplyInFlight || curationPreviewLoading) {
        return;
    }

    if (!curationPreview) {
        setCurationButtonsState();
        showAlert('Load a successful curation preview before applying changes.', 'warning');
        return;
    }

    const confirmed = window.confirm(
        'Apply Favourite Songs curation in Apple Music? This can create folders, playlists, and copy tracks.'
    );

    if (!confirmed) {
        return;
    }

    curationApplyInFlight = true;
    setCurationButtonsState();

    try {
        showSpinner(true);
        const result = await app.api('/curation/apply', {
            method: 'POST',
            body: { scope: 'fav_songs', confirmed: true },
        });

        const applied = asNumber(result.applied);
        const failed = asNumber(result.failed);
        showAlert(`Applied ${applied} curation change${applied === 1 ? '' : 's'}${failed ? `, ${failed} failed` : ''}.`, 'success');
        curationApplyInFlight = false;
        setCurationButtonsState();
        await loadCurationPreview();
    } catch (error) {
        showAlert('Failed to apply curation: ' + error.message, 'danger');
    } finally {
        curationApplyInFlight = false;
        setCurationButtonsState();
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
            showView(view);

            // Load view-specific data
            if (view === 'playlists') loadPlaylists();
            if (view === 'dashboard') loadDashboard();
            if (view === 'curation') loadCurationPreview();
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

    // Curation
    if (DOM.curationRefreshBtn()) {
        DOM.curationRefreshBtn().addEventListener('click', loadCurationPreview);
    }
    if (DOM.curationDryRunBtn()) {
        DOM.curationDryRunBtn().addEventListener('click', loadCurationPreview);
    }
    if (DOM.curationApplyBtn()) {
        DOM.curationApplyBtn().addEventListener('click', applyFavSongsCuration);
    }
    setCurationButtonsState();
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
        if (lastView === 'curation') {
            loadCurationPreview();
        }
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
