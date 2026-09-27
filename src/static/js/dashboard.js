// Statistics Dashboard JavaScript

// Get logger instance
const dashboardLogger = window.loggers ? window.loggers.dashboard : console;

let dashboardCharts = {};
let currentView = 'dashboard';
let currentLayout = 'grid';

// Toggle dashboard visibility
function toggleDashboard() {
    const dashboard = document.getElementById('statisticsDashboard');
    const clustersSection = document.querySelector('.clusters-section');
    
    if (!dashboard || !clustersSection) return;
    
    if (dashboard.style.display === 'none' || !dashboard.style.display) {
        dashboard.style.display = 'block';
        clustersSection.style.display = 'none';
        loadStatistics();
    } else {
        dashboard.style.display = 'none';
        clustersSection.style.display = 'block';
        // Destroy charts when hiding
        Object.values(dashboardCharts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        dashboardCharts = {};
    }
}

// Load and display statistics
async function loadStatistics() {
    const API_BASE_URL = '/api';
    const startTime = performance.now();

    try {
        dashboardLogger.info('Loading statistics...');
        const response = await fetch(`${API_BASE_URL}/statistics`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const stats = await response.json();
        const duration = performance.now() - startTime;
        dashboardLogger.info(`Statistics loaded in ${duration.toFixed(2)}ms`);
        
        // Update overview cards
        document.getElementById('statTotalClusters').textContent = stats.overview.total_clusters;
        document.getElementById('statTotalSites').textContent = stats.overview.total_sites;
        document.getElementById('statTotalSegments').textContent = stats.overview.total_segments;
        document.getElementById('statAvgSegments').textContent = stats.overview.average_segments_per_cluster;
        
        // Render charts
        renderClustersPerSiteChart(stats.clusters_per_site);
        renderSourceDistributionChart(stats.source_distribution);
        renderDomainDistributionChart(stats.domain_distribution);
        renderSegmentsPerSiteChart(stats.segments_per_site);

    } catch (error) {
        dashboardLogger.error('Failed to load statistics:', error);
        if (typeof showToast === 'function') {
            showToast('Failed to load statistics', 'error');
        }
    }
}

// Render clusters per site chart
function renderClustersPerSiteChart(data) {
    const ctx = document.getElementById('clustersPerSiteChart');
    if (!ctx) return;
    
    // Destroy existing chart if any
    if (dashboardCharts.clustersPerSite) {
        dashboardCharts.clustersPerSite.destroy();
    }
    
    const labels = Object.keys(data);
    const values = Object.values(data);
    
    dashboardCharts.clustersPerSite = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Clusters',
                data: values,
                backgroundColor: 'rgba(238, 0, 0, 0.7)',
                borderColor: 'rgba(238, 0, 0, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// Render source distribution chart
function renderSourceDistributionChart(data) {
    const ctx = document.getElementById('sourceDistributionChart');
    if (!ctx) return;
    
    if (dashboardCharts.sourceDistribution) {
        dashboardCharts.sourceDistribution.destroy();
    }
    
    dashboardCharts.sourceDistribution = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(data).map(k => k === 'segments-manager' ? 'Segments Manager' : 'Manual'),
            datasets: [{
                data: Object.values(data),
                backgroundColor: [
                    'rgba(62, 134, 53, 0.7)',
                    'rgba(43, 154, 243, 0.7)'
                ],
                borderColor: [
                    'rgba(62, 134, 53, 1)',
                    'rgba(43, 154, 243, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Render domain distribution chart
function renderDomainDistributionChart(data) {
    const ctx = document.getElementById('domainDistributionChart');
    if (!ctx) return;
    
    if (dashboardCharts.domainDistribution) {
        dashboardCharts.domainDistribution.destroy();
    }
    
    const labels = Object.keys(data);
    const values = Object.values(data);
    
    dashboardCharts.domainDistribution = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    'rgba(238, 0, 0, 0.85)',
                    'rgba(30, 30, 30, 0.85)',
                    'rgba(240, 171, 0, 0.85)',
                    'rgba(153, 0, 0, 0.85)',
                    'rgba(150, 150, 150, 0.85)'
                ],
                borderColor: 'rgba(255, 255, 255, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Render segments per site chart
function renderSegmentsPerSiteChart(data) {
    const ctx = document.getElementById('segmentsPerSiteChart');
    if (!ctx) return;
    
    if (dashboardCharts.segmentsPerSite) {
        dashboardCharts.segmentsPerSite.destroy();
    }
    
    const labels = Object.keys(data);
    const values = Object.values(data);
    
    dashboardCharts.segmentsPerSite = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Segments',
                data: values,
                backgroundColor: 'rgba(43, 154, 243, 0.7)',
                borderColor: 'rgba(43, 154, 243, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}


// ========== New Dashboard UI Functions ==========

// View switching
function switchView(view) {
    currentView = view;

    // Update navigation items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    const activeNav = document.querySelector(`[data-view="${view}"]`);
    if (activeNav) {
        activeNav.classList.add('active');
    }

    // Hide all views
    document.querySelectorAll('.content-view').forEach(view => {
        view.classList.remove('active');
    });

    // Show selected view
    const viewMap = {
        'dashboard': 'dashboardView',
        'sites': 'sitesView',
        'clusters': 'clustersView',
        'analytics': 'analyticsView'
    };

    const viewId = viewMap[view];
    const viewElement = document.getElementById(viewId);
    if (viewElement) {
        viewElement.classList.add('active');
    }

    // Load view-specific data
    switch(view) {
        case 'dashboard':
            updateDashboard();
            break;
        case 'sites':
            renderSitesView();
            break;
        case 'clusters':
            renderAllClustersView();
            break;
        case 'analytics':
            loadStatistics();
            break;
    }
}

// Sidebar toggle for mobile
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        sidebar.classList.toggle('active');
    }
}

// Layout toggle
function toggleLayout(layout) {
    currentLayout = layout;

    // Update active button
    document.querySelectorAll('.view-toggle-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    const activeBtn = document.querySelector(`[onclick="toggleLayout('${layout}')"]`);
    if (activeBtn) {
        activeBtn.classList.add('active');
    }

    // Re-render current view with new layout
    if (currentView === 'sites') {
        renderSitesView();
    } else if (currentView === 'clusters') {
        renderAllClustersView();
    }
}

// Dashboard statistics update
async function updateDashboard() {
    try {
        const response = await fetch('/api/sites-combined');
        if (!response.ok) throw new Error('Failed to fetch data');

        const sites = await response.json();

        // Calculate statistics
        const totalClusters = sites.reduce((sum, site) => sum + site.clusterCount, 0);
        const totalSites = sites.length;
        const allSegments = new Set();
        sites.forEach(site => {
            site.clusters.forEach(cluster => {
                cluster.segments.forEach(segment => allSegments.add(segment));
            });
        });

        // Count VLANs (from segments)
        const totalVLANs = allSegments.size;

        // Animate counters
        animateCounter(document.getElementById('totalClusters'), totalClusters);
        animateCounter(document.getElementById('totalSites'), totalSites);
        animateCounter(document.getElementById('totalSegments'), allSegments.size);
        animateCounter(document.getElementById('totalVLANs'), totalVLANs);

        // Update site distribution
        renderSiteDistribution(sites);

        // Update recent activity
        renderRecentActivity(sites);

    } catch (error) {
        console.error('Failed to update dashboard:', error);
    }
}

// Animate counter
function animateCounter(element, target) {
    if (!element) return;

    const duration = 1000;
    const start = 0;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        const current = Math.floor(progress * target);
        element.textContent = current;

        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            element.textContent = target;
        }
    }

    requestAnimationFrame(update);
}

// Render site distribution
function renderSiteDistribution(sites) {
    const container = document.getElementById('siteDistributionContent');
    if (!container) return;

    container.innerHTML = '';

    // Sort sites by cluster count
    const sortedSites = [...sites].sort((a, b) => b.clusterCount - a.clusterCount);
    const maxCount = sortedSites[0]?.clusterCount || 1;

    sortedSites.forEach(site => {
        const percentage = (site.clusterCount / maxCount) * 100;

        const siteDiv = document.createElement('div');
        siteDiv.className = 'distribution-item';
        siteDiv.innerHTML = `
            <div class="distribution-label">
                <span>${site.site}</span>
                <span class="distribution-count">${site.clusterCount}</span>
            </div>
            <div class="distribution-bar">
                <div class="distribution-fill" style="width: ${percentage}%"></div>
            </div>
        `;
        container.appendChild(siteDiv);
    });
}

// Render recent activity
function renderRecentActivity(sites) {
    const container = document.getElementById('recentActivityContent');
    if (!container) return;

    container.innerHTML = '';

    // Get all clusters with timestamps (simulated for now)
    const allClusters = [];
    sites.forEach(site => {
        site.clusters.forEach(cluster => {
            allClusters.push({
                ...cluster,
                timestamp: new Date() // In real app, this would come from actual data
            });
        });
    });

    // Show most recent 5
    allClusters.slice(0, 5).forEach(cluster => {
        const activityDiv = document.createElement('div');
        activityDiv.className = 'activity-item';

        const icon = cluster.source === 'segments-manager' ?
            '<svg class="activity-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>' :
            '<svg class="activity-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><polyline points="17 11 19 13 23 9"/></svg>';

        activityDiv.innerHTML = `
            ${icon}
            <div class="activity-details">
                <div class="activity-title">${cluster.clusterName}</div>
                <div class="activity-meta">${cluster.site} • ${formatTimeAgo(cluster.timestamp)}</div>
            </div>
        `;
        container.appendChild(activityDiv);
    });
}

// Render sites view
function renderSitesView() {
    const container = document.getElementById('sitesViewContent');
    if (!container) return;

    fetch('/api/sites-combined')
        .then(response => response.json())
        .then(sites => {
            container.innerHTML = '';

            sites.forEach(site => {
                const siteCard = document.createElement('div');
                siteCard.className = 'site-card';
                siteCard.innerHTML = `
                    <div class="site-card-header">
                        <h3>${site.site}</h3>
                        <span class="badge">${site.clusterCount} clusters</span>
                    </div>
                    <div class="site-card-body">
                        <div class="site-stat">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg>
                            <span>${site.clusterCount} Clusters</span>
                        </div>
                    </div>
                `;
                container.appendChild(siteCard);
            });
        })
        .catch(error => {
            console.error('Failed to load sites:', error);
            container.innerHTML = '<p class="error-message">Failed to load sites</p>';
        });
}

// Render all clusters view
function renderAllClustersView() {
    const container = document.getElementById('clustersViewContent');
    if (!container) return;

    fetch('/api/sites-combined')
        .then(response => response.json())
        .then(sites => {
            container.innerHTML = '';

            const containerClass = currentLayout === 'grid' ? 'clusters-grid' : 'clusters-list';
            const gridContainer = document.createElement('div');
            gridContainer.className = containerClass;

            sites.forEach(site => {
                site.clusters.forEach(cluster => {
                    const card = createClusterCard(cluster);
                    if (currentLayout === 'list') {
                        card.classList.add('list-item');
                    }
                    gridContainer.appendChild(card);
                });
            });

            container.appendChild(gridContainer);
        })
        .catch(error => {
            console.error('Failed to load clusters:', error);
            container.innerHTML = '<p class="error-message">Failed to load clusters</p>';
        });
}

// Utility: Format time ago
function formatTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);

    const intervals = {
        year: 31536000,
        month: 2592000,
        week: 604800,
        day: 86400,
        hour: 3600,
        minute: 60
    };

    for (const [unit, secondsInUnit] of Object.entries(intervals)) {
        const interval = Math.floor(seconds / secondsInUnit);
        if (interval >= 1) {
            return `${interval} ${unit}${interval > 1 ? 's' : ''} ago`;
        }
    }

    return 'just now';
}

// Utility: Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Filter functionality for dashboard
function filterDashboardData() {
    const searchTerm = document.getElementById('searchInput')?.value.toLowerCase();
    if (!searchTerm) {
        // Reset filters
        if (currentView === 'sites') renderSitesView();
        else if (currentView === 'clusters') renderAllClustersView();
        return;
    }

    // Apply filters based on current view
    // This would be integrated with the existing filterClusters() function
    if (typeof filterClusters === 'function') {
        filterClusters();
    }
}

// Refresh data function
function refreshData() {
    if (currentView === 'dashboard') {
        updateDashboard();
    } else if (currentView === 'sites') {
        renderSitesView();
    } else if (currentView === 'clusters') {
        renderAllClustersView();
    } else if (currentView === 'analytics') {
        loadStatistics();
    }

    // Also reload sync status
    if (typeof loadSyncStatus === 'function') {
        loadSyncStatus();
    }
}

// Clear search function
function clearSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.value = '';
        filterDashboardData();
    }

    const clearBtn = document.getElementById('clearSearchBtn');
    if (clearBtn) {
        clearBtn.style.display = 'none';
    }
}

// Initialize new dashboard on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // Check if new dashboard exists
        if (document.getElementById('dashboardView')) {
            updateDashboard();

            // Setup search input listener
            const searchInput = document.getElementById('searchInput');
            const clearBtn = document.getElementById('clearSearchBtn');
            if (searchInput && clearBtn) {
                searchInput.addEventListener('input', (e) => {
                    clearBtn.style.display = e.target.value ? 'block' : 'none';
                });
            }
        }
    });
} else {
    // DOM already loaded
    if (document.getElementById('dashboardView')) {
        updateDashboard();

        // Setup search input listener
        const searchInput = document.getElementById('searchInput');
        const clearBtn = document.getElementById('clearSearchBtn');
        if (searchInput && clearBtn) {
            searchInput.addEventListener('input', (e) => {
                clearBtn.style.display = e.target.value ? 'block' : 'none';
            });
        }
    }
}
