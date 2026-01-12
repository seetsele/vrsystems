// ================================================
// VERITY SYSTEMS - SEARCH & HISTORY
// Full-text search, filtering, and export
// ================================================

(function() {
    'use strict';

    const VerityHistory = {
        // History storage key
        STORAGE_KEY: 'verity_verification_history',
        MAX_ITEMS: 500,

        // Get all history items
        getAll() {
            try {
                return JSON.parse(localStorage.getItem(this.STORAGE_KEY) || '[]');
            } catch (e) {
                return [];
            }
        },

        // Add a verification to history
        add(verification) {
            const history = this.getAll();
            
            const item = {
                id: this.generateId(),
                claim: verification.claim,
                verdict: verification.verdict,
                confidence: verification.confidence,
                score: verification.score,
                sources: verification.sources || [],
                providers: verification.providers || [],
                timestamp: new Date().toISOString(),
                tags: verification.tags || [],
                favorite: false,
                notes: ''
            };
            
            history.unshift(item);
            
            // Limit history size
            if (history.length > this.MAX_ITEMS) {
                history.pop();
            }
            
            this.save(history);
            return item;
        },

        // Generate unique ID
        generateId() {
            return 'v_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        },

        // Save history
        save(history) {
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(history));
        },

        // Search history with filters
        search(options = {}) {
            let results = this.getAll();
            
            // Text search
            if (options.query) {
                const query = options.query.toLowerCase();
                results = results.filter(item => 
                    item.claim.toLowerCase().includes(query) ||
                    (item.notes && item.notes.toLowerCase().includes(query)) ||
                    (item.tags && item.tags.some(t => t.toLowerCase().includes(query)))
                );
            }
            
            // Date filter
            if (options.startDate) {
                const start = new Date(options.startDate).getTime();
                results = results.filter(item => new Date(item.timestamp).getTime() >= start);
            }
            
            if (options.endDate) {
                const end = new Date(options.endDate).getTime() + 86400000; // Include end date
                results = results.filter(item => new Date(item.timestamp).getTime() <= end);
            }
            
            // Verdict filter
            if (options.verdict) {
                results = results.filter(item => item.verdict === options.verdict);
            }
            
            // Confidence filter
            if (options.minConfidence) {
                results = results.filter(item => item.confidence >= options.minConfidence);
            }
            
            if (options.maxConfidence) {
                results = results.filter(item => item.confidence <= options.maxConfidence);
            }
            
            // Tags filter
            if (options.tags && options.tags.length > 0) {
                results = results.filter(item => 
                    item.tags && options.tags.some(t => item.tags.includes(t))
                );
            }
            
            // Favorites only
            if (options.favoritesOnly) {
                results = results.filter(item => item.favorite);
            }
            
            // Sort
            if (options.sortBy) {
                const sortOrder = options.sortOrder === 'asc' ? 1 : -1;
                results.sort((a, b) => {
                    switch (options.sortBy) {
                        case 'date':
                            return sortOrder * (new Date(b.timestamp) - new Date(a.timestamp));
                        case 'confidence':
                            return sortOrder * (b.confidence - a.confidence);
                        case 'claim':
                            return sortOrder * a.claim.localeCompare(b.claim);
                        default:
                            return 0;
                    }
                });
            }
            
            return results;
        },

        // Get a single item by ID
        getById(id) {
            return this.getAll().find(item => item.id === id);
        },

        // Update an item
        update(id, updates) {
            const history = this.getAll();
            const index = history.findIndex(item => item.id === id);
            
            if (index === -1) return null;
            
            history[index] = { ...history[index], ...updates };
            this.save(history);
            
            return history[index];
        },

        // Toggle favorite
        toggleFavorite(id) {
            const item = this.getById(id);
            if (!item) return null;
            
            return this.update(id, { favorite: !item.favorite });
        },

        // Add tag
        addTag(id, tag) {
            const item = this.getById(id);
            if (!item) return null;
            
            const tags = item.tags || [];
            if (!tags.includes(tag)) {
                tags.push(tag);
                return this.update(id, { tags });
            }
            return item;
        },

        // Remove tag
        removeTag(id, tag) {
            const item = this.getById(id);
            if (!item) return null;
            
            const tags = (item.tags || []).filter(t => t !== tag);
            return this.update(id, { tags });
        },

        // Delete item
        delete(id) {
            const history = this.getAll().filter(item => item.id !== id);
            this.save(history);
        },

        // Bulk delete
        bulkDelete(ids) {
            const history = this.getAll().filter(item => !ids.includes(item.id));
            this.save(history);
        },

        // Clear all history
        clearAll() {
            this.save([]);
        },

        // Get all unique tags
        getAllTags() {
            const history = this.getAll();
            const tags = new Set();
            
            history.forEach(item => {
                if (item.tags) {
                    item.tags.forEach(t => tags.add(t));
                }
            });
            
            return Array.from(tags).sort();
        },

        // Get statistics
        getStats() {
            const history = this.getAll();
            
            const stats = {
                total: history.length,
                true: 0,
                false: 0,
                partial: 0,
                unverified: 0,
                avgConfidence: 0,
                favorites: 0,
                thisWeek: 0,
                thisMonth: 0
            };
            
            const now = Date.now();
            const weekAgo = now - 7 * 24 * 60 * 60 * 1000;
            const monthAgo = now - 30 * 24 * 60 * 60 * 1000;
            let totalConfidence = 0;
            
            history.forEach(item => {
                // Verdict counts
                const verdict = item.verdict?.toLowerCase() || 'unverified';
                if (stats[verdict] !== undefined) {
                    stats[verdict]++;
                }
                
                // Confidence
                if (item.confidence) {
                    totalConfidence += item.confidence;
                }
                
                // Favorites
                if (item.favorite) {
                    stats.favorites++;
                }
                
                // Time-based
                const itemTime = new Date(item.timestamp).getTime();
                if (itemTime >= weekAgo) stats.thisWeek++;
                if (itemTime >= monthAgo) stats.thisMonth++;
            });
            
            stats.avgConfidence = history.length > 0 ? Math.round(totalConfidence / history.length) : 0;
            
            return stats;
        },

        // Export to CSV
        exportCSV(items = null) {
            const data = items || this.getAll();
            
            const headers = ['ID', 'Claim', 'Verdict', 'Confidence', 'Score', 'Tags', 'Favorite', 'Notes', 'Timestamp'];
            const rows = data.map(item => [
                item.id,
                `"${(item.claim || '').replace(/"/g, '""')}"`,
                item.verdict,
                item.confidence,
                item.score,
                `"${(item.tags || []).join(', ')}"`,
                item.favorite ? 'Yes' : 'No',
                `"${(item.notes || '').replace(/"/g, '""')}"`,
                item.timestamp
            ]);
            
            const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
            this.download(csv, 'verity-history.csv', 'text/csv');
        },

        // Export to JSON
        exportJSON(items = null) {
            const data = items || this.getAll();
            const json = JSON.stringify(data, null, 2);
            this.download(json, 'verity-history.json', 'application/json');
        },

        // Export to PDF (basic)
        async exportPDF(items = null) {
            const data = items || this.getAll();
            
            // Create a printable HTML document
            const html = `
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Verity Verification History</title>
                    <style>
                        body { font-family: system-ui, sans-serif; padding: 2rem; }
                        h1 { color: #f59e0b; }
                        table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
                        th, td { padding: 0.75rem; border: 1px solid #ddd; text-align: left; }
                        th { background: #f5f5f5; }
                        .true { color: #10b981; }
                        .false { color: #ef4444; }
                        .partial { color: #f59e0b; }
                    </style>
                </head>
                <body>
                    <h1>Verity Verification History</h1>
                    <p>Exported: ${new Date().toLocaleString()}</p>
                    <p>Total Items: ${data.length}</p>
                    <table>
                        <tr>
                            <th>Claim</th>
                            <th>Verdict</th>
                            <th>Confidence</th>
                            <th>Date</th>
                        </tr>
                        ${data.map(item => `
                            <tr>
                                <td>${item.claim || '-'}</td>
                                <td class="${item.verdict?.toLowerCase()}">${item.verdict || '-'}</td>
                                <td>${item.confidence || '-'}%</td>
                                <td>${new Date(item.timestamp).toLocaleString()}</td>
                            </tr>
                        `).join('')}
                    </table>
                </body>
                </html>
            `;
            
            // Open print dialog
            const win = window.open('', '_blank');
            win.document.write(html);
            win.document.close();
            win.print();
        },

        // Download helper
        download(content, filename, type) {
            const blob = new Blob([content], { type });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        },

        // Re-verify an item
        async reverify(id) {
            const item = this.getById(id);
            if (!item) return null;
            
            // Dispatch event for reverification
            const event = new CustomEvent('reverify:request', { detail: { claim: item.claim } });
            document.dispatchEvent(event);
            
            return item;
        }
    };

    // ================================================
    // SEARCH UI COMPONENT
    // ================================================
    const SearchUI = {
        container: null,

        // Create search interface
        create(targetSelector) {
            const target = document.querySelector(targetSelector);
            if (!target) return;
            
            this.container = document.createElement('div');
            this.container.className = 'verity-search-ui';
            this.container.innerHTML = `
                <div class="search-header">
                    <div class="search-input-wrap">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
                        </svg>
                        <input type="text" id="history-search" placeholder="Search claims, notes, tags..." />
                        <button id="search-clear" style="display: none;">×</button>
                    </div>
                    <div class="search-filters">
                        <select id="filter-verdict">
                            <option value="">All Verdicts</option>
                            <option value="true">True</option>
                            <option value="false">False</option>
                            <option value="partial">Partial</option>
                        </select>
                        <select id="filter-date">
                            <option value="">All Time</option>
                            <option value="today">Today</option>
                            <option value="week">This Week</option>
                            <option value="month">This Month</option>
                        </select>
                        <button id="filter-favorites" class="filter-btn">★ Favorites</button>
                        <button id="export-btn" class="filter-btn">Export ▼</button>
                    </div>
                </div>
                <div class="search-results-info"></div>
                <div class="search-results"></div>
                <div class="search-pagination"></div>
            `;
            
            target.insertBefore(this.container, target.firstChild);
            this.attachStyles();
            this.attachListeners();
            this.refresh();
        },

        // Attach event listeners
        attachListeners() {
            const searchInput = this.container.querySelector('#history-search');
            const verdictSelect = this.container.querySelector('#filter-verdict');
            const dateSelect = this.container.querySelector('#filter-date');
            const favoritesBtn = this.container.querySelector('#filter-favorites');
            const exportBtn = this.container.querySelector('#export-btn');
            const clearBtn = this.container.querySelector('#search-clear');
            
            // Debounced search
            let timeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(timeout);
                clearBtn.style.display = e.target.value ? 'block' : 'none';
                timeout = setTimeout(() => this.refresh(), 300);
            });
            
            clearBtn.addEventListener('click', () => {
                searchInput.value = '';
                clearBtn.style.display = 'none';
                this.refresh();
            });
            
            verdictSelect.addEventListener('change', () => this.refresh());
            dateSelect.addEventListener('change', () => this.refresh());
            
            favoritesBtn.addEventListener('click', () => {
                favoritesBtn.classList.toggle('active');
                this.refresh();
            });
            
            exportBtn.addEventListener('click', () => this.showExportMenu());
        },

        // Get current filter options
        getFilters() {
            const options = {
                query: this.container.querySelector('#history-search').value,
                verdict: this.container.querySelector('#filter-verdict').value,
                favoritesOnly: this.container.querySelector('#filter-favorites').classList.contains('active')
            };
            
            const dateFilter = this.container.querySelector('#filter-date').value;
            if (dateFilter) {
                const now = new Date();
                switch (dateFilter) {
                    case 'today':
                        options.startDate = new Date(now.setHours(0, 0, 0, 0));
                        break;
                    case 'week':
                        options.startDate = new Date(now.setDate(now.getDate() - 7));
                        break;
                    case 'month':
                        options.startDate = new Date(now.setMonth(now.getMonth() - 1));
                        break;
                }
            }
            
            return options;
        },

        // Refresh results
        refresh() {
            const filters = this.getFilters();
            const results = VerityHistory.search(filters);
            this.renderResults(results);
        },

        // Render results
        renderResults(results) {
            const container = this.container.querySelector('.search-results');
            const infoContainer = this.container.querySelector('.search-results-info');
            
            infoContainer.innerHTML = `<span>${results.length} verification${results.length !== 1 ? 's' : ''} found</span>`;
            
            if (results.length === 0) {
                container.innerHTML = `
                    <div class="no-results">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#525252" stroke-width="1.5">
                            <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
                        </svg>
                        <p>No verifications found</p>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = results.slice(0, 20).map(item => `
                <div class="history-item" data-id="${item.id}">
                    <div class="item-icon ${item.verdict?.toLowerCase() || 'unknown'}">
                        ${this.getVerdictIcon(item.verdict)}
                    </div>
                    <div class="item-content">
                        <div class="item-claim">${this.highlightMatch(item.claim)}</div>
                        <div class="item-meta">
                            <span class="confidence">${item.confidence || 0}% confidence</span>
                            <span class="separator">•</span>
                            <span class="time">${this.formatTime(item.timestamp)}</span>
                            ${item.tags?.length ? `<span class="separator">•</span><span class="tags">${item.tags.join(', ')}</span>` : ''}
                        </div>
                    </div>
                    <div class="item-actions">
                        <button class="action-btn favorite ${item.favorite ? 'active' : ''}" title="Favorite">★</button>
                        <button class="action-btn reverify" title="Re-verify">↻</button>
                        <button class="action-btn delete" title="Delete">×</button>
                    </div>
                </div>
            `).join('');
            
            // Attach item listeners
            container.querySelectorAll('.history-item').forEach(el => {
                const id = el.dataset.id;
                
                el.querySelector('.favorite').addEventListener('click', (e) => {
                    e.stopPropagation();
                    VerityHistory.toggleFavorite(id);
                    e.target.classList.toggle('active');
                });
                
                el.querySelector('.reverify').addEventListener('click', (e) => {
                    e.stopPropagation();
                    VerityHistory.reverify(id);
                });
                
                el.querySelector('.delete').addEventListener('click', (e) => {
                    e.stopPropagation();
                    if (confirm('Delete this verification?')) {
                        VerityHistory.delete(id);
                        this.refresh();
                    }
                });
            });
        },

        // Get verdict icon
        getVerdictIcon(verdict) {
            switch (verdict?.toLowerCase()) {
                case 'true':
                    return '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>';
                case 'false':
                    return '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';
                case 'partial':
                    return '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>';
                default:
                    return '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>';
            }
        },

        // Highlight search match
        highlightMatch(text) {
            const query = this.container.querySelector('#history-search').value;
            if (!query) return text;
            
            const regex = new RegExp(`(${query})`, 'gi');
            return text.replace(regex, '<mark>$1</mark>');
        },

        // Format time
        formatTime(timestamp) {
            const date = new Date(timestamp);
            const now = new Date();
            const diff = now - date;
            
            if (diff < 60000) return 'Just now';
            if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
            if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
            if (diff < 604800000) return `${Math.floor(diff / 86400000)}d ago`;
            
            return date.toLocaleDateString();
        },

        // Show export menu
        showExportMenu() {
            const btn = this.container.querySelector('#export-btn');
            const rect = btn.getBoundingClientRect();
            
            const menu = document.createElement('div');
            menu.className = 'export-menu';
            menu.style.cssText = `
                position: fixed;
                top: ${rect.bottom + 5}px;
                right: ${window.innerWidth - rect.right}px;
                background: #18181b;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 0.5rem 0;
                z-index: 10000;
                min-width: 150px;
            `;
            menu.innerHTML = `
                <button class="export-option" data-format="csv">Export CSV</button>
                <button class="export-option" data-format="json">Export JSON</button>
                <button class="export-option" data-format="pdf">Export PDF</button>
            `;
            
            document.body.appendChild(menu);
            
            menu.querySelectorAll('.export-option').forEach(opt => {
                opt.addEventListener('click', () => {
                    const format = opt.dataset.format;
                    const results = VerityHistory.search(this.getFilters());
                    
                    switch (format) {
                        case 'csv': VerityHistory.exportCSV(results); break;
                        case 'json': VerityHistory.exportJSON(results); break;
                        case 'pdf': VerityHistory.exportPDF(results); break;
                    }
                    
                    menu.remove();
                });
            });
            
            // Close on click outside
            setTimeout(() => {
                document.addEventListener('click', function close(e) {
                    if (!menu.contains(e.target)) {
                        menu.remove();
                        document.removeEventListener('click', close);
                    }
                });
            }, 0);
        },

        // Attach styles
        attachStyles() {
            if (document.getElementById('verity-search-styles')) return;
            
            const styles = document.createElement('style');
            styles.id = 'verity-search-styles';
            styles.textContent = `
                .verity-search-ui {
                    margin-bottom: 1.5rem;
                }
                .search-header {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 1rem;
                    margin-bottom: 1rem;
                }
                .search-input-wrap {
                    flex: 1;
                    min-width: 280px;
                    position: relative;
                    display: flex;
                    align-items: center;
                    background: var(--elevated, #18181b);
                    border: 1px solid var(--border, rgba(255,255,255,0.1));
                    border-radius: 10px;
                    padding: 0 1rem;
                }
                .search-input-wrap svg {
                    color: var(--dim, #525252);
                }
                .search-input-wrap input {
                    flex: 1;
                    background: none;
                    border: none;
                    color: var(--text, #fafafa);
                    padding: 0.75rem;
                    font-size: 0.9rem;
                    outline: none;
                }
                .search-input-wrap input::placeholder {
                    color: var(--dim, #525252);
                }
                #search-clear {
                    background: none;
                    border: none;
                    color: var(--muted, #a3a3a3);
                    font-size: 1.2rem;
                    cursor: pointer;
                    padding: 0.25rem 0.5rem;
                }
                .search-filters {
                    display: flex;
                    gap: 0.5rem;
                    flex-wrap: wrap;
                }
                .search-filters select,
                .filter-btn {
                    background: var(--elevated, #18181b);
                    border: 1px solid var(--border, rgba(255,255,255,0.1));
                    border-radius: 8px;
                    color: var(--text, #fafafa);
                    padding: 0.6rem 1rem;
                    font-size: 0.85rem;
                    cursor: pointer;
                }
                .filter-btn.active {
                    background: var(--amber, #f59e0b);
                    color: #000;
                    border-color: var(--amber, #f59e0b);
                }
                .search-results-info {
                    color: var(--muted, #a3a3a3);
                    font-size: 0.85rem;
                    margin-bottom: 1rem;
                }
                .no-results {
                    text-align: center;
                    padding: 3rem;
                    color: var(--dim, #525252);
                }
                .no-results p {
                    margin-top: 1rem;
                }
                .history-item {
                    display: flex;
                    align-items: center;
                    gap: 1rem;
                    padding: 1rem;
                    background: var(--card, #111113);
                    border: 1px solid var(--border, rgba(255,255,255,0.06));
                    border-radius: 12px;
                    margin-bottom: 0.5rem;
                    transition: all 0.2s;
                }
                .history-item:hover {
                    border-color: rgba(245, 158, 11, 0.3);
                }
                .item-icon {
                    width: 36px;
                    height: 36px;
                    border-radius: 10px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .item-icon.true { background: rgba(16, 185, 129, 0.12); color: #10b981; }
                .item-icon.false { background: rgba(239, 68, 68, 0.12); color: #ef4444; }
                .item-icon.partial { background: rgba(234, 179, 8, 0.12); color: #eab308; }
                .item-icon.unknown { background: rgba(100, 100, 100, 0.12); color: #666; }
                .item-content {
                    flex: 1;
                    min-width: 0;
                }
                .item-claim {
                    font-size: 0.9rem;
                    font-weight: 500;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    margin-bottom: 0.25rem;
                }
                .item-claim mark {
                    background: rgba(245, 158, 11, 0.3);
                    color: inherit;
                    padding: 0 0.2rem;
                    border-radius: 2px;
                }
                .item-meta {
                    font-size: 0.75rem;
                    color: var(--dim, #525252);
                }
                .item-meta .separator {
                    margin: 0 0.5rem;
                }
                .item-actions {
                    display: flex;
                    gap: 0.25rem;
                }
                .action-btn {
                    background: none;
                    border: 1px solid transparent;
                    color: var(--muted, #a3a3a3);
                    width: 32px;
                    height: 32px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 1rem;
                    transition: all 0.2s;
                }
                .action-btn:hover {
                    background: var(--elevated, #18181b);
                    border-color: var(--border, rgba(255,255,255,0.1));
                }
                .action-btn.favorite.active {
                    color: var(--amber, #f59e0b);
                }
                .action-btn.delete:hover {
                    color: var(--red, #ef4444);
                }
                .export-option {
                    display: block;
                    width: 100%;
                    padding: 0.6rem 1rem;
                    background: none;
                    border: none;
                    color: var(--text, #fafafa);
                    text-align: left;
                    cursor: pointer;
                    font-size: 0.85rem;
                }
                .export-option:hover {
                    background: var(--elevated, #18181b);
                }
            `;
            document.head.appendChild(styles);
        }
    };

    // Export to global scope
    window.VerityHistory = VerityHistory;
    window.VeritySearchUI = SearchUI;

})();
