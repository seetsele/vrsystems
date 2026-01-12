// ================================================
// VERITY SYSTEMS - DASHBOARD CHARTS
// Verification trends, stats, and visualizations
// ================================================

(function() {
    'use strict';

    const DashboardCharts = {
        // Chart colors
        colors: {
            amber: '#f59e0b',
            green: '#10b981',
            red: '#ef4444',
            cyan: '#22d3ee',
            violet: '#8b5cf6',
            muted: '#525252',
            border: 'rgba(255, 255, 255, 0.1)'
        },

        // Initialize all charts
        init() {
            this.createTrendChart();
            this.createVerdictChart();
            this.createAccuracyGauge();
            this.setupLiveUpdates();
        },

        // Get verification data (from localStorage or API)
        getData() {
            const history = JSON.parse(localStorage.getItem('verity_verification_history') || '[]');
            return history;
        },

        // Group data by time period
        groupByPeriod(data, period = 'day') {
            const groups = {};
            const now = new Date();
            
            data.forEach(item => {
                const date = new Date(item.timestamp);
                let key;
                
                switch (period) {
                    case 'hour':
                        key = date.toISOString().slice(0, 13);
                        break;
                    case 'day':
                        key = date.toISOString().slice(0, 10);
                        break;
                    case 'week':
                        const weekStart = new Date(date);
                        weekStart.setDate(date.getDate() - date.getDay());
                        key = weekStart.toISOString().slice(0, 10);
                        break;
                    case 'month':
                        key = date.toISOString().slice(0, 7);
                        break;
                }
                
                if (!groups[key]) {
                    groups[key] = { total: 0, true: 0, false: 0, partial: 0 };
                }
                
                groups[key].total++;
                const verdict = item.verdict?.toLowerCase();
                if (groups[key][verdict] !== undefined) {
                    groups[key][verdict]++;
                }
            });
            
            return groups;
        },

        // Create trend line chart
        createTrendChart() {
            const container = document.getElementById('trend-chart');
            if (!container) return;
            
            const data = this.getData();
            const groups = this.groupByPeriod(data, 'day');
            
            // Get last 14 days
            const labels = [];
            const values = [];
            const today = new Date();
            
            for (let i = 13; i >= 0; i--) {
                const date = new Date(today);
                date.setDate(date.getDate() - i);
                const key = date.toISOString().slice(0, 10);
                labels.push(date.toLocaleDateString('en-US', { weekday: 'short', day: 'numeric' }));
                values.push(groups[key]?.total || 0);
            }
            
            // Create SVG chart
            const width = container.clientWidth || 400;
            const height = 200;
            const padding = { top: 20, right: 20, bottom: 40, left: 50 };
            const chartWidth = width - padding.left - padding.right;
            const chartHeight = height - padding.top - padding.bottom;
            
            const maxValue = Math.max(...values, 1);
            const points = values.map((v, i) => ({
                x: padding.left + (i / (values.length - 1)) * chartWidth,
                y: padding.top + chartHeight - (v / maxValue) * chartHeight
            }));
            
            // Create path
            const pathD = points.map((p, i) => 
                `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`
            ).join(' ');
            
            // Create gradient area
            const areaD = pathD + 
                ` L ${padding.left + chartWidth} ${padding.top + chartHeight}` +
                ` L ${padding.left} ${padding.top + chartHeight} Z`;
            
            container.innerHTML = `
                <svg width="100%" height="${height}" viewBox="0 0 ${width} ${height}">
                    <defs>
                        <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="${this.colors.amber}" stop-opacity="0.3"/>
                            <stop offset="100%" stop-color="${this.colors.amber}" stop-opacity="0"/>
                        </linearGradient>
                    </defs>
                    
                    <!-- Grid lines -->
                    ${[0, 25, 50, 75, 100].map(pct => {
                        const y = padding.top + (1 - pct / 100) * chartHeight;
                        return `<line x1="${padding.left}" y1="${y}" x2="${padding.left + chartWidth}" y2="${y}" 
                                      stroke="${this.colors.border}" stroke-dasharray="4"/>`;
                    }).join('')}
                    
                    <!-- Area fill -->
                    <path d="${areaD}" fill="url(#areaGradient)"/>
                    
                    <!-- Line -->
                    <path d="${pathD}" fill="none" stroke="${this.colors.amber}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                    
                    <!-- Data points -->
                    ${points.map((p, i) => `
                        <circle cx="${p.x}" cy="${p.y}" r="4" fill="${this.colors.amber}" stroke="#111113" stroke-width="2">
                            <title>${labels[i]}: ${values[i]} verifications</title>
                        </circle>
                    `).join('')}
                    
                    <!-- Y-axis labels -->
                    <text x="${padding.left - 10}" y="${padding.top}" fill="${this.colors.muted}" font-size="11" text-anchor="end" dominant-baseline="middle">${maxValue}</text>
                    <text x="${padding.left - 10}" y="${padding.top + chartHeight}" fill="${this.colors.muted}" font-size="11" text-anchor="end" dominant-baseline="middle">0</text>
                    
                    <!-- X-axis labels -->
                    ${[0, 6, 13].map(i => `
                        <text x="${points[i].x}" y="${height - 10}" fill="${this.colors.muted}" font-size="11" text-anchor="middle">${labels[i]}</text>
                    `).join('')}
                </svg>
            `;
        },

        // Create verdict donut chart
        createVerdictChart() {
            const container = document.getElementById('verdict-chart');
            if (!container) return;
            
            const data = this.getData();
            const verdicts = { true: 0, false: 0, partial: 0 };
            
            data.forEach(item => {
                const v = item.verdict?.toLowerCase();
                if (verdicts[v] !== undefined) verdicts[v]++;
            });
            
            const total = Object.values(verdicts).reduce((a, b) => a + b, 0) || 1;
            const size = 160;
            const strokeWidth = 25;
            const radius = (size - strokeWidth) / 2;
            const circumference = 2 * Math.PI * radius;
            const center = size / 2;
            
            let offset = 0;
            const segments = [
                { key: 'true', color: this.colors.green, value: verdicts.true },
                { key: 'partial', color: this.colors.amber, value: verdicts.partial },
                { key: 'false', color: this.colors.red, value: verdicts.false }
            ].filter(s => s.value > 0);
            
            const paths = segments.map(seg => {
                const percentage = seg.value / total;
                const dashLength = percentage * circumference;
                const dashOffset = -offset;
                offset += dashLength;
                
                return `<circle cx="${center}" cy="${center}" r="${radius}" 
                                fill="none" 
                                stroke="${seg.color}" 
                                stroke-width="${strokeWidth}"
                                stroke-dasharray="${dashLength} ${circumference}"
                                stroke-dashoffset="${dashOffset}"
                                transform="rotate(-90 ${center} ${center})"/>`;
            });
            
            container.innerHTML = `
                <div style="display: flex; align-items: center; gap: 2rem;">
                    <svg width="${size}" height="${size}">
                        <circle cx="${center}" cy="${center}" r="${radius}" fill="none" stroke="${this.colors.border}" stroke-width="${strokeWidth}"/>
                        ${paths.join('')}
                        <text x="${center}" y="${center - 8}" fill="#fafafa" font-size="24" font-weight="600" text-anchor="middle">${total}</text>
                        <text x="${center}" y="${center + 12}" fill="${this.colors.muted}" font-size="12" text-anchor="middle">Total</text>
                    </svg>
                    <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <div style="width: 12px; height: 12px; background: ${this.colors.green}; border-radius: 3px;"></div>
                            <span style="color: ${this.colors.muted}; font-size: 0.85rem;">True: ${verdicts.true} (${Math.round(verdicts.true / total * 100)}%)</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <div style="width: 12px; height: 12px; background: ${this.colors.amber}; border-radius: 3px;"></div>
                            <span style="color: ${this.colors.muted}; font-size: 0.85rem;">Partial: ${verdicts.partial} (${Math.round(verdicts.partial / total * 100)}%)</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <div style="width: 12px; height: 12px; background: ${this.colors.red}; border-radius: 3px;"></div>
                            <span style="color: ${this.colors.muted}; font-size: 0.85rem;">False: ${verdicts.false} (${Math.round(verdicts.false / total * 100)}%)</span>
                        </div>
                    </div>
                </div>
            `;
        },

        // Create accuracy gauge
        createAccuracyGauge() {
            const container = document.getElementById('accuracy-gauge');
            if (!container) return;
            
            const data = this.getData();
            let totalConfidence = 0;
            let count = 0;
            
            data.forEach(item => {
                if (item.confidence) {
                    totalConfidence += item.confidence;
                    count++;
                }
            });
            
            const accuracy = count > 0 ? Math.round(totalConfidence / count) : 0;
            const size = 120;
            const strokeWidth = 12;
            const radius = (size - strokeWidth) / 2;
            const circumference = 2 * Math.PI * radius;
            const dashOffset = circumference * (1 - accuracy / 100);
            const center = size / 2;
            
            // Determine color based on accuracy
            const color = accuracy >= 80 ? this.colors.green : accuracy >= 60 ? this.colors.amber : this.colors.red;
            
            container.innerHTML = `
                <svg width="${size}" height="${size}">
                    <circle cx="${center}" cy="${center}" r="${radius}" 
                            fill="none" stroke="${this.colors.border}" stroke-width="${strokeWidth}"/>
                    <circle cx="${center}" cy="${center}" r="${radius}" 
                            fill="none" 
                            stroke="${color}" 
                            stroke-width="${strokeWidth}"
                            stroke-dasharray="${circumference}"
                            stroke-dashoffset="${dashOffset}"
                            stroke-linecap="round"
                            transform="rotate(-90 ${center} ${center})"
                            style="transition: stroke-dashoffset 1s ease;"/>
                    <text x="${center}" y="${center - 5}" fill="#fafafa" font-size="24" font-weight="600" text-anchor="middle">${accuracy}%</text>
                    <text x="${center}" y="${center + 15}" fill="${this.colors.muted}" font-size="10" text-anchor="middle">Avg Confidence</text>
                </svg>
            `;
        },

        // Setup live updates
        setupLiveUpdates() {
            // Listen for new verifications
            document.addEventListener('verification:complete', () => {
                setTimeout(() => {
                    this.createTrendChart();
                    this.createVerdictChart();
                    this.createAccuracyGauge();
                }, 500);
            });
            
            // Refresh every 30 seconds
            setInterval(() => {
                this.createTrendChart();
            }, 30000);
        },

        // Create chart card container
        createChartCard(title, chartId, width = 'auto') {
            return `
                <div class="chart-card" style="
                    background: var(--card, #111113);
                    border: 1px solid var(--border, rgba(255,255,255,0.06));
                    border-radius: 16px;
                    padding: 1.5rem;
                    ${width !== 'auto' ? `width: ${width};` : ''}
                ">
                    <h3 style="
                        font-size: 0.9rem;
                        font-weight: 600;
                        color: var(--text, #fafafa);
                        margin-bottom: 1rem;
                        display: flex;
                        align-items: center;
                        gap: 0.5rem;
                    ">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="${this.colors.amber}" stroke-width="2">
                            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                        </svg>
                        ${title}
                    </h3>
                    <div id="${chartId}"></div>
                </div>
            `;
        },

        // Add charts section to dashboard
        addToDashboard() {
            const main = document.querySelector('.main');
            if (!main) return;
            
            // Find verify-card to insert after
            const verifyCard = main.querySelector('.verify-card');
            if (!verifyCard) return;
            
            // Create charts section
            const chartsSection = document.createElement('div');
            chartsSection.className = 'charts-section';
            chartsSection.style.cssText = `
                display: grid;
                grid-template-columns: 2fr 1fr;
                gap: 1.5rem;
                margin-bottom: 2rem;
            `;
            
            chartsSection.innerHTML = `
                ${this.createChartCard('Verification Trend (14 days)', 'trend-chart')}
                <div style="display: flex; flex-direction: column; gap: 1rem;">
                    ${this.createChartCard('Verdict Distribution', 'verdict-chart')}
                    ${this.createChartCard('Accuracy Score', 'accuracy-gauge')}
                </div>
            `;
            
            // Insert after verify card
            verifyCard.parentNode.insertBefore(chartsSection, verifyCard.nextSibling);
            
            // Initialize charts
            this.init();
        }
    };

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            if (window.location.pathname.includes('dashboard')) {
                DashboardCharts.addToDashboard();
            }
        });
    } else {
        if (window.location.pathname.includes('dashboard')) {
            DashboardCharts.addToDashboard();
        }
    }

    // Export
    window.VerityDashboardCharts = DashboardCharts;

})();
