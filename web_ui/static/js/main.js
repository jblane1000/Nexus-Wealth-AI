/**
 * Nexus Wealth AI - Main JavaScript
 * Global JavaScript functions for the web interface
 */

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Initialize dashboard data refresh if on dashboard
    if (document.getElementById('allocationChart') || document.getElementById('performanceChart')) {
        setupDashboardRefresh();
    }
    
    // Setup form validations
    setupFormValidations();
    
    // Animate elements
    animateElements();
});

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Setup periodic refresh of dashboard data
 */
function setupDashboardRefresh() {
    // Refresh portfolio data every 5 minutes
    setInterval(function() {
        if (!document.hidden) {
            refreshPortfolioData();
        }
    }, 300000); // 5 minutes
    
    // Refresh market data more frequently
    setInterval(function() {
        if (!document.hidden) {
            refreshMarketData();
        }
    }, 60000); // 1 minute
}

/**
 * Refresh portfolio data via AJAX
 */
function refreshPortfolioData() {
    fetch('/api/portfolio')
        .then(response => response.json())
        .then(data => {
            // Update portfolio value
            const portfolioValueElements = document.querySelectorAll('.portfolio-value');
            portfolioValueElements.forEach(el => {
                el.textContent = `$${data.total_value.toFixed(2)}`;
            });
            
            // Update performance indicators
            updatePerformanceIndicators(data.performance);
            
            // Update allocation chart if it exists
            if (window.allocationChart) {
                updateAllocationChart(data.allocation);
            }
            
            // Update assets table if it exists
            updateAssetsTable(data.assets);
        })
        .catch(error => {
            console.error('Error refreshing portfolio data:', error);
        });
}

/**
 * Refresh market data via AJAX
 */
function refreshMarketData() {
    fetch('/api/market_summary')
        .then(response => response.json())
        .then(data => {
            // Update market indices
            updateMarketIndices(data.indices);
            
            // Update crypto prices if displayed
            if (data.crypto) {
                updateCryptoPrices(data.crypto);
            }
        })
        .catch(error => {
            console.error('Error refreshing market data:', error);
        });
}

/**
 * Update performance indicators with new data
 * @param {Object} performance - Performance data object
 */
function updatePerformanceIndicators(performance) {
    const dailyElement = document.getElementById('performance-daily');
    const weeklyElement = document.getElementById('performance-weekly');
    const monthlyElement = document.getElementById('performance-monthly');
    const yearlyElement = document.getElementById('performance-yearly');
    
    if (dailyElement) {
        const dailyChange = performance.daily;
        dailyElement.textContent = `${dailyChange > 0 ? '+' : ''}${dailyChange.toFixed(2)}%`;
        dailyElement.className = dailyChange >= 0 ? 'text-success' : 'text-danger';
        
        const dailyIcon = dailyElement.querySelector('i') || document.createElement('i');
        dailyIcon.className = dailyChange >= 0 ? 'fas fa-arrow-up me-1' : 'fas fa-arrow-down me-1';
        
        if (!dailyElement.contains(dailyIcon)) {
            dailyElement.prepend(dailyIcon);
        }
    }
    
    // Similar updates for weekly, monthly, yearly
    // Implementation omitted for brevity
}

/**
 * Update allocation chart with new data
 * @param {Object} allocation - Asset allocation data
 */
function updateAllocationChart(allocation) {
    const labels = Object.keys(allocation);
    const values = Object.values(allocation);
    
    window.allocationChart.data.labels = labels;
    window.allocationChart.data.datasets[0].data = values;
    window.allocationChart.update();
}

/**
 * Update assets table with new data
 * @param {Array} assets - Portfolio assets data
 */
function updateAssetsTable(assets) {
    const tableBody = document.querySelector('#assets-table tbody');
    if (!tableBody) return;
    
    // Clear existing rows
    tableBody.innerHTML = '';
    
    // Add new rows
    assets.forEach(asset => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${asset.symbol}</td>
            <td>${asset.name}</td>
            <td class="text-end">${asset.quantity}</td>
            <td class="text-end">$${asset.price.toFixed(2)}</td>
            <td class="text-end">$${asset.value.toFixed(2)}</td>
            <td class="text-end">${asset.allocation.toFixed(2)}%</td>
        `;
        
        tableBody.appendChild(row);
    });
}

/**
 * Update market indices with new data
 * @param {Array} indices - Market indices data
 */
function updateMarketIndices(indices) {
    indices.forEach(index => {
        const element = document.getElementById(`index-${index.name.toLowerCase().replace(/[^a-z0-9]/g, '-')}`);
        if (element) {
            const valueElement = element.querySelector('.index-value');
            const changeElement = element.querySelector('.index-change');
            
            if (valueElement) {
                valueElement.textContent = index.value.toFixed(2);
            }
            
            if (changeElement) {
                changeElement.textContent = `${index.change_percent > 0 ? '+' : ''}${index.change_percent.toFixed(2)}%`;
                changeElement.className = index.change_percent >= 0 ? 'index-change text-success' : 'index-change text-danger';
            }
        }
    });
}

/**
 * Update crypto prices with new data
 * @param {Array} cryptos - Cryptocurrency data
 */
function updateCryptoPrices(cryptos) {
    cryptos.forEach(crypto => {
        const element = document.getElementById(`crypto-${crypto.symbol.toLowerCase()}`);
        if (element) {
            const priceElement = element.querySelector('.crypto-price');
            const changeElement = element.querySelector('.crypto-change');
            
            if (priceElement) {
                priceElement.textContent = `$${crypto.price.toFixed(2)}`;
            }
            
            if (changeElement) {
                changeElement.textContent = `${crypto.change_percent > 0 ? '+' : ''}${crypto.change_percent.toFixed(2)}%`;
                changeElement.className = crypto.change_percent >= 0 ? 'crypto-change text-success' : 'crypto-change text-danger';
            }
        }
    });
}

/**
 * Setup form validations
 */
function setupFormValidations() {
    // Deposit form validation
    const depositForm = document.querySelector('form[action="/deposit"]');
    if (depositForm) {
        depositForm.addEventListener('submit', function(event) {
            const amountInput = depositForm.querySelector('#amount');
            const amount = parseFloat(amountInput.value);
            
            if (isNaN(amount) || amount < 100) {
                event.preventDefault();
                alert('Please enter a valid deposit amount of $100 or more.');
            }
        });
    }
    
    // Withdrawal form validation
    const withdrawForm = document.querySelector('form[action="/withdraw"]');
    if (withdrawForm) {
        withdrawForm.addEventListener('submit', function(event) {
            const amountInput = withdrawForm.querySelector('#amount');
            const amount = parseFloat(amountInput.value);
            const availableBalance = parseFloat(amountInput.getAttribute('max') || '0');
            
            if (isNaN(amount) || amount < 10) {
                event.preventDefault();
                alert('Please enter a valid withdrawal amount of $10 or more.');
            } else if (amount > availableBalance) {
                event.preventDefault();
                alert(`Withdrawal amount exceeds available balance of $${availableBalance.toFixed(2)}.`);
            }
        });
    }
}

/**
 * Animate elements on page load
 */
function animateElements() {
    // Fade in stat cards
    const statCards = document.querySelectorAll('.stat-card');
    
    statCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 * index);
    });
    
    // Animate progress bars
    const progressBars = document.querySelectorAll('.progress-bar');
    
    progressBars.forEach(bar => {
        const finalWidth = bar.style.width;
        bar.style.width = '0%';
        
        setTimeout(() => {
            bar.style.transition = 'width 1s ease';
            bar.style.width = finalWidth;
        }, 200);
    });
}

/**
 * Format currency value
 * @param {number} value - The value to format
 * @param {string} currency - Currency code (default: USD)
 * @returns {string} Formatted currency string
 */
function formatCurrency(value, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(value);
}

/**
 * Format date value
 * @param {string} dateString - ISO date string
 * @param {boolean} includeTime - Whether to include time
 * @returns {string} Formatted date string
 */
function formatDate(dateString, includeTime = false) {
    const date = new Date(dateString);
    
    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    };
    
    if (includeTime) {
        options.hour = '2-digit';
        options.minute = '2-digit';
    }
    
    return new Intl.DateTimeFormat('en-US', options).format(date);
}

/**
 * Calculate time difference from now
 * @param {string} dateString - ISO date string
 * @returns {string} Human-readable time difference
 */
function timeFromNow(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    
    const diffMs = now - date;
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);
    
    if (diffDay > 0) {
        return diffDay === 1 ? '1 day ago' : `${diffDay} days ago`;
    } else if (diffHour > 0) {
        return diffHour === 1 ? '1 hour ago' : `${diffHour} hours ago`;
    } else if (diffMin > 0) {
        return diffMin === 1 ? '1 minute ago' : `${diffMin} minutes ago`;
    } else {
        return 'Just now';
    }
}
