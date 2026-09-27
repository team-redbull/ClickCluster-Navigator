// OpenShift Cluster Navigator - JavaScript (Read-Only Mode)

const API_BASE_URL = '/api';

// Session storage for admin credentials
let adminCredentials = null;

// Global data storage
let allSites = [];
let allClusters = [];
let currentViewMode = 'grouped';
let availabilityMap = {};

// Get logger instance
const logger = window.loggers ? window.loggers.app : console;

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    logger.info('Application initializing...');
    loadClusters();
    setupEventListeners();
    initializeDarkMode();
    checkAdminSession();
    loadSyncStatus();
    logger.info('Application initialized successfully');
});

// Set up event listeners
function setupEventListeners() {
    const loginForm = document.getElementById('adminLoginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
}

// Dark Mode Functions
function initializeDarkMode() {
    const darkMode = localStorage.getItem('darkMode') === 'true';
    if (darkMode) {
        document.body.classList.add('dark-mode');
        updateDarkModeIcon(true);
    }
}

function toggleDarkMode() {
    const isDark = document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', isDark);
    updateDarkModeIcon(isDark);
}

function updateDarkModeIcon(isDark) {
    const icon = document.getElementById('darkModeIcon');
    if (isDark) {
        // Sun icon for light mode
        icon.innerHTML = '<circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>';
    } else {
        // Moon icon for dark mode
        icon.innerHTML = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>';
    }
}

// Admin Authentication
function toggleAdminPanel() {
    const loginPanel = document.getElementById('adminLoginPanel');
    const controlPanel = document.getElementById('adminControlPanel');

    if (adminCredentials) {
        // Already logged in, show control panel
        loginPanel.style.display = 'none';
        const isVisible = controlPanel.style.display !== 'none';
        controlPanel.style.display = isVisible ? 'none' : 'block';
    } else {
        // Not logged in, show login panel
        controlPanel.style.display = 'none';
        const isVisible = loginPanel.style.display !== 'none';
        loginPanel.style.display = isVisible ? 'none' : 'block';
    }
}

async function handleLogin(event) {
    event.preventDefault();

    const username = document.getElementById('adminUsername').value;
    const password = document.getElementById('adminPassword').value;

    // Store credentials (Base64 encoded for HTTP Basic Auth)
    const credentials = btoa(`${username}:${password}`);

    // Test credentials by making an authenticated request
    try {
        const response = await fetch(`${API_BASE_URL}/auth/verify`, {
            headers: {
                'Authorization': `Basic ${credentials}`
            }
        });

        if (response.ok) {
            adminCredentials = credentials;
            sessionStorage.setItem('adminAuth', credentials);
            showLoginMessage('Login successful!', 'success');

            // Hide login panel and show control panel
            setTimeout(() => {
                document.getElementById('adminLoginPanel').style.display = 'none';
                document.getElementById('adminControlPanel').style.display = 'block';
                loadSyncStatus();
            }, 1000);
        } else {
            showLoginMessage('Invalid credentials', 'error');
        }
    } catch (error) {
        showLoginMessage('Login failed', 'error');
    }
}

function showLoginMessage(message, type) {
    const messageElement = document.getElementById('loginMessage');
    if (!messageElement) return;

    messageElement.textContent = message;
    messageElement.className = `message ${type}`;
    messageElement.style.display = 'block';

    setTimeout(() => {
        messageElement.style.display = 'none';
    }, 3000);
}

function showRefreshStatus(message, type) {
    const messageElement = document.getElementById('refreshStatus');
    if (!messageElement) return;

    messageElement.textContent = message;
    messageElement.className = `message ${type}`;
    messageElement.style.display = 'block';

    setTimeout(() => {
        messageElement.style.display = 'none';
    }, 5000);
}

function checkAdminSession() {
    const stored = sessionStorage.getItem('adminAuth');
    if (stored) {
        adminCredentials = stored;
    }
}

function logout() {
    adminCredentials = null;
    sessionStorage.removeItem('adminAuth');
    document.getElementById('adminControlPanel').style.display = 'none';
    document.getElementById('adminUsername').value = '';
    document.getElementById('adminPassword').value = '';
    showLoginMessage('Logged out successfully', 'success');
}

// Hard Refresh Function
async function hardRefresh() {
    const btn = document.getElementById('hardRefreshBtn');
    if (!btn) return;

    btn.disabled = true;
    btn.textContent = 'Syncing...';

    try {
        const response = await fetch(`${API_BASE_URL}/segments-sync/sync`, {
            method: 'POST',
            headers: {
                'Authorization': `Basic ${adminCredentials}`
            }
        });

        if (response.ok) {
            const result = await response.json();
            showRefreshStatus(`Sync successful! Found ${result.data.stats.total_clusters} clusters`, 'success');
            loadSyncStatus();
            loadClusters();
            // Refresh dashboard if visible
            if (document.getElementById('statisticsDashboard').style.display !== 'none') {
                loadStatistics();
            }
        } else {
            showRefreshStatus('Sync failed', 'error');
        }
    } catch (error) {
        showRefreshStatus(`Sync error: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/></svg> Hard Refresh from Segments Manager';
    }
}

// Load sync status
async function loadSyncStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/segments-sync/status`);
        if (response.ok) {
            const status = await response.json();
            const lastSyncElement = document.getElementById('lastSyncTime');
            const lastSyncTimeDisplay = document.getElementById('lastSyncTimeValue');
            const statsElement = document.getElementById('syncStats');

            // Update admin panel sync time
            if (lastSyncElement && status.last_updated) {
                const date = new Date(status.last_updated);
                lastSyncElement.textContent = date.toLocaleString();
            }

            // Update header sync time display
            if (lastSyncTimeDisplay) {
                if (status.last_updated) {
                    const date = new Date(status.last_updated);
                    const now = new Date();
                    const diffMs = now - date;
                    const diffMins = Math.floor(diffMs / 60000);
                    const diffHours = Math.floor(diffMins / 60);
                    const diffDays = Math.floor(diffHours / 24);
                    
                    let timeAgo;
                    if (diffMins < 1) {
                        timeAgo = 'Just now';
                    } else if (diffMins < 60) {
                        timeAgo = `${diffMins} min${diffMins !== 1 ? 's' : ''} ago`;
                    } else if (diffHours < 24) {
                        timeAgo = `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
                    } else {
                        timeAgo = `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
                    }
                    
                    lastSyncTimeDisplay.textContent = timeAgo;
                    lastSyncTimeDisplay.title = date.toLocaleString();
                } else {
                    lastSyncTimeDisplay.textContent = 'Never';
                }
            }

            if (statsElement && status.cache_age_minutes !== null) {
                const dataResponse = await fetch(`${API_BASE_URL}/segments-sync/data`);
                if (dataResponse.ok) {
                    const data = await dataResponse.json();
                    statsElement.textContent = `${data.stats.total_clusters} clusters, ${data.stats.total_sites} sites, ${data.stats.total_segments} segments (Cache age: ${status.cache_age_minutes.toFixed(1)} min)`;
                }
            }
        }
    } catch (error) {
        console.error('Failed to load sync status:', error);
    }
}

// Load and display all clusters organized by site
async function loadClusters() {
    const startTime = performance.now();
    const loadingSpinner = document.getElementById('loadingSpinner');
    const clustersContainer = document.getElementById('clustersContainer');
    const emptyState = document.getElementById('emptyState');

    // Show loading spinner
    loadingSpinner.classList.remove('hidden');
    clustersContainer.innerHTML = '';
    emptyState.style.display = 'none';

    try {
        logger.info('Fetching clusters data...');
        const response = await fetch(`${API_BASE_URL}/sites-combined`);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const sites = await response.json();
        const duration = performance.now() - startTime;

        logger.info(`Loaded ${sites.length} sites in ${duration.toFixed(2)}ms`);

        // Hide loading spinner
        loadingSpinner.classList.add('hidden');

        if (sites.length === 0) {
            logger.warn('No sites found');
            emptyState.style.display = 'block';
            return;
        }

        // Sort sites by name
        sites.sort((a, b) => a.site.localeCompare(b.site));

        // Store globally for filtering
        allSites = sites;
        allClusters = sites.flatMap(site => site.clusters);

        logger.info(`Total clusters: ${allClusters.length}`);

        // Populate filter dropdowns
        populateSiteFilter(sites);
        populateDomainFilter(allClusters);

        // Render clusters
        renderClusters(sites);

        // Update statistics
        updateStats(sites);

        // Check availability in background — dots update when done
        loadAvailability();

    } catch (error) {
        logger.error('Failed to load clusters:', error);
        loadingSpinner.classList.add('hidden');
        clustersContainer.innerHTML = `<p class="error-message">Error loading clusters: ${error.message}</p>`;
    }
}

// Check cluster availability and re-render dots when done
async function loadAvailability() {
    try {
        const response = await fetch(`${API_BASE_URL}/clusters/availability`);
        if (!response.ok) return;
        availabilityMap = await response.json();
        filterClusters();
    } catch (e) {
        // silent — dots stay grey
    }
}

// Populate the site filter dropdown
function populateSiteFilter(sites) {
    const siteFilter = document.getElementById('siteFilter');
    const currentValue = siteFilter.value;

    // Clear existing options except the first one
    siteFilter.innerHTML = '<option value="">All Sites</option>';

    // Add site options
    sites.forEach(site => {
        const option = document.createElement('option');
        option.value = site.site;
        option.textContent = `${site.site} (${site.clusterCount})`;
        siteFilter.appendChild(option);
    });

    // Restore previous selection
    siteFilter.value = currentValue;
}

// Populate the domain filter dropdown
function populateDomainFilter(clusters) {
    const domainFilter = document.getElementById('domainFilter');
    if (!domainFilter) return;
    const currentValue = domainFilter.value;
    domainFilter.innerHTML = '<option value="">All Domains</option>';
    const domains = [...new Set(clusters.map(c => c.domainName).filter(Boolean))].sort();
    domains.forEach(domain => {
        const option = document.createElement('option');
        option.value = domain;
        option.textContent = domain;
        domainFilter.appendChild(option);
    });
    domainFilter.value = currentValue;
}

// Filter clusters
function filterClusters() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const siteFilter = document.getElementById('siteFilter').value;
    const domainFilter = document.getElementById('domainFilter')?.value || '';

    // Shallow copy instead of deep clone for better performance
    let filteredSites = allSites.map(site => ({ ...site, clusters: [...site.clusters] }));

    // Filter by site
    if (siteFilter) {
        filteredSites = filteredSites.filter(site => site.site === siteFilter);
    }

    // Filter by domain
    if (domainFilter) {
        filteredSites = filteredSites.map(site => {
            const filteredClusters = site.clusters.filter(c => c.domainName === domainFilter);
            return { ...site, clusters: filteredClusters, clusterCount: filteredClusters.length };
        }).filter(site => site.clusterCount > 0);
    }

    // Filter by search term
    if (searchTerm) {
        filteredSites = filteredSites.map(site => {
            const filteredClusters = site.clusters.filter(cluster => {
                return cluster.clusterName.toLowerCase().includes(searchTerm) ||
                       cluster.site.toLowerCase().includes(searchTerm) ||
                       cluster.segments.some(segment => segment.toLowerCase().includes(searchTerm));
            });
            return { ...site, clusters: filteredClusters, clusterCount: filteredClusters.length };
        }).filter(site => site.clusterCount > 0);
    }

    renderClusters(filteredSites);
    updateStats(filteredSites);
}

// Render clusters based on current view mode
function renderClusters(sites) {
    const container = document.getElementById('clustersContainer');
    container.innerHTML = '';

    if (currentViewMode === 'grouped') {
        renderGroupedView(sites, container);
    } else if (currentViewMode === 'list') {
        renderListView(sites, container);
    } else if (currentViewMode === 'compact') {
        renderCompactView(sites, container);
    }
}

// Render grouped by site view
function renderGroupedView(sites, container) {
    sites.forEach(site => {
        const siteSection = document.createElement('div');
        siteSection.className = 'site-section';
        siteSection.innerHTML = `
            <h3 class="site-title">${site.site} <span class="cluster-count">(${site.clusterCount} clusters)</span></h3>
            <div class="clusters-grid"></div>
        `;

        const clustersGrid = siteSection.querySelector('.clusters-grid');
        site.clusters.forEach(cluster => {
            clustersGrid.appendChild(createClusterCard(cluster));
        });

        container.appendChild(siteSection);
    });
}

// Render list view
function renderListView(sites, container) {
    const listContainer = document.createElement('div');
    listContainer.className = 'clusters-list';

    sites.forEach(site => {
        site.clusters.forEach(cluster => {
            const card = createClusterCard(cluster);
            card.classList.add('list-item');
            listContainer.appendChild(card);
        });
    });

    container.appendChild(listContainer);
}

// Render compact grid view
function renderCompactView(sites, container) {
    const compactGrid = document.createElement('div');
    compactGrid.className = 'clusters-compact-grid';

    sites.forEach(site => {
        site.clusters.forEach(cluster => {
            const card = createClusterCard(cluster);
            card.classList.add('compact');
            compactGrid.appendChild(card);
        });
    });

    container.appendChild(compactGrid);
}

// Create a cluster card element
function createClusterCard(cluster) {
    const card = document.createElement('div');
    card.className = 'cluster-card';

    const sourceIndicator = cluster.source === 'segments-manager' ?
        '<span class="source-badge segments-manager">Segments Manager</span>' :
        '<span class="source-badge manual">Manual</span>';

    // Add delete button for manual clusters if admin is logged in
    const isManual = cluster.source === 'manual';
    const isAdmin = adminCredentials !== null;
    const deleteButton = (isManual && isAdmin) ? `
        <button class="btn-delete btn-small" onclick="deleteCluster('${cluster.id}', '${cluster.clusterName}', event)" title="Delete cluster">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                <line x1="10" y1="11" x2="10" y2="17"></line>
                <line x1="14" y1="11" x2="14" y2="17"></line>
            </svg>
        </button>
    ` : '';

    // LoadBalancer IP display (if available) - supports multiple IPs
    let loadBalancerIPDisplay = '';
    if (cluster.loadBalancerIP) {
        // Handle both array and single string (backward compatibility)
        const ipList = Array.isArray(cluster.loadBalancerIP) 
            ? cluster.loadBalancerIP 
            : (cluster.loadBalancerIP ? [cluster.loadBalancerIP] : []);
        
        if (ipList.length > 0) {
            const ipBadges = ipList.map(ip => 
                `<span class="ip-address-badge" onclick="copyToClipboard('${ip}', 'LoadBalancer IP')" title="Click to copy">
                    ${ip}
                </span>`
            ).join('');
            
            const labelText = ipList.length === 1 ? 'LoadBalancer IP:' : `LoadBalancer IPs (${ipList.length}):`;
            loadBalancerIPDisplay = `
                <div class="info-item">
                    <strong>${labelText}</strong>
                    <div class="ip-address-container">
                        ${ipBadges}
                    </div>
                </div>
            `;
        }
    }

    const avail = availabilityMap[cluster.id];
    const dotClass = avail === undefined ? 'grey' : avail ? 'green' : 'red';
    const dotTitle = avail === undefined ? 'Checking availability...' : avail ? 'Available' : 'Unavailable';

    card.innerHTML = `
        <div class="cluster-header">
            <div class="cluster-header-name">
                <span class="availability-dot ${dotClass}" title="${dotTitle}"></span>
                <h4>${cluster.clusterName}</h4>
            </div>
            ${sourceIndicator}
        </div>
        <div class="cluster-info">
            <div class="info-item">
                <strong>Site:</strong> ${cluster.site}
            </div>
            <div class="info-item">
                <strong>Domain:</strong> ${cluster.domainName}
            </div>
            ${loadBalancerIPDisplay}
            <div class="info-item">
                <strong>Segments:</strong>
                <div class="segments-list">
                    ${cluster.segments.map(segment =>
                        `<span class="segment-badge">${segment}</span>`
                    ).join('')}
                </div>
            </div>
        </div>
        <div class="cluster-actions">
            <a href="${cluster.consoleUrl}" target="_blank" class="btn-primary btn-small">
                Open Console
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                    <polyline points="15 3 21 3 21 9"></polyline>
                    <line x1="10" y1="14" x2="21" y2="3"></line>
                </svg>
            </a>
            ${deleteButton}
        </div>
    `;

    return card;
}

// Change view mode
function changeViewMode() {
    const viewMode = document.getElementById('viewMode').value;
    currentViewMode = viewMode;
    filterClusters();
}

// Update statistics
function updateStats(sites) {
    const totalClusters = sites.reduce((sum, site) => sum + site.clusterCount, 0);
    const totalSites = sites.length;

    document.getElementById('clusterCount').textContent = `${totalClusters} cluster${totalClusters !== 1 ? 's' : ''}`;
    document.getElementById('siteCount').textContent = `${totalSites} site${totalSites !== 1 ? 's' : ''}`;
}

// Export data function
function exportData(format) {
    const url = `${API_BASE_URL}/export/${format}`;
    const link = document.createElement('a');
    link.href = url;
    link.download = '';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    if (typeof showToast === 'function') {
        showToast(`Exporting as ${format.toUpperCase()}...`, 'info', 2000);
    }
}

// Toggle create cluster form
async function toggleCreateClusterForm() {
    const form = document.getElementById('createClusterForm');
    if (form.style.display === 'none') {
        form.style.display = 'block';
        document.getElementById('clusterForm').reset();
        document.getElementById('createClusterMessage').style.display = 'none';

        // Load sites for dropdown
        await loadSitesDropdown();
    } else {
        form.style.display = 'none';
    }
}

// Load sites into dropdown
async function loadSitesDropdown() {
    const siteSelect = document.getElementById('newClusterSite');

    try {
        const response = await fetch(`${API_BASE_URL}/segments-sync/sites`);
        if (response.ok) {
            const data = await response.json();

            // Clear existing options except the first one
            siteSelect.innerHTML = '<option value="">Select a site...</option>';

            // Add sites from Segments Manager
            if (data.sites && data.sites.length > 0) {
                data.sites.forEach(site => {
                    const option = document.createElement('option');
                    option.value = site;
                    option.textContent = site;
                    siteSelect.appendChild(option);
                });
            } else {
                // If no sites, add a message option
                const option = document.createElement('option');
                option.value = '';
                option.textContent = 'No sites available';
                option.disabled = true;
                siteSelect.appendChild(option);
            }
        } else {
            console.error('Failed to load sites');
        }
    } catch (error) {
        console.error('Error loading sites:', error);
    }
}

// Create cluster function
async function createCluster(event) {
    event.preventDefault();

    const form = event.target;

    // Check if admin is logged in
    if (!adminCredentials) {
        showClusterMessage('You must be logged in as admin to create clusters', 'error');
        return;
    }

    // Get form data
    const clusterName = document.getElementById('newClusterName').value.trim().toLowerCase();
    const site = document.getElementById('newClusterSite').value.trim();
    const segmentsText = document.getElementById('newClusterSegments').value.trim();
    const domainName = document.getElementById('newClusterDomain').value.trim();
    const loadBalancerIP = document.getElementById('newClusterLoadBalancerIP').value.trim();

    // Parse segments (one per line)
    const segments = segmentsText.split('\n').map(s => s.trim()).filter(s => s.length > 0);

    if (segments.length === 0) {
        showClusterMessage('Please enter at least one network segment', 'error');
        return;
    }

    if (!site) {
        showClusterMessage('Please select a site', 'error');
        return;
    }

    // Create cluster data
    const clusterData = {
        clusterName: clusterName,
        site: site,
        segments: segments,
        domainName: domainName || 'example.com'
    };

    // Add LoadBalancer IP if provided
    if (loadBalancerIP) {
        clusterData.loadBalancerIP = loadBalancerIP;
    }


    // Disable submit button
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Creating...';

    try {
        const response = await fetch(`${API_BASE_URL}/clusters`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Basic ${adminCredentials}`
            },
            body: JSON.stringify(clusterData)
        });

        if (response.ok) {
            await response.json();
            showClusterMessage(`Cluster "${clusterName}" created successfully!`, 'success');

            // Reset form
            form.reset();

            // Reload clusters
            setTimeout(() => {
                loadClusters();
                toggleCreateClusterForm();
            }, 1500);
        } else {
            const error = await response.json();
            showClusterMessage(error.detail || 'Failed to create cluster', 'error');
        }
    } catch (error) {
        showClusterMessage(`Error: ${error.message}`, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}

// Show cluster creation message
function showClusterMessage(message, type) {
    const messageElement = document.getElementById('createClusterMessage');
    if (!messageElement) return;

    messageElement.textContent = message;
    messageElement.className = `message ${type}`;
    messageElement.style.display = 'block';

    if (type === 'success') {
        setTimeout(() => {
            messageElement.style.display = 'none';
        }, 3000);
    }
}

// Delete cluster function
async function deleteCluster(clusterId, clusterName, event) {
    event.preventDefault();
    event.stopPropagation();

    // Confirm deletion
    if (!confirm(`Are you sure you want to delete the cluster "${clusterName}"?\n\nThis action cannot be undone.`)) {
        return;
    }

    if (!adminCredentials) {
        alert('You must be logged in as admin to delete clusters');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/clusters/${clusterId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Basic ${adminCredentials}`
            }
        });

        if (response.status === 204 || response.ok) {
            // Reload clusters to reflect changes
            loadClusters();
        } else if (response.status === 403) {
            const error = await response.json();
            alert(error.detail || 'Cannot delete Segments Manager clusters');
        } else if (response.status === 404) {
            alert('Cluster not found');
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to delete cluster');
        }
    } catch (error) {
        alert(`Error deleting cluster: ${error.message}`);
    }
}
