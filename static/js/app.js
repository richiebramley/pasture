// AgriTech Newsfeed JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-refresh functionality
    let autoRefreshInterval;
    
    function startAutoRefresh() {
        autoRefreshInterval = setInterval(function() {
            refreshStats();
        }, 300000); // Refresh every 5 minutes
    }
    
    function stopAutoRefresh() {
        if (autoRefreshInterval) {
            clearInterval(autoRefreshInterval);
        }
    }
    
    // Refresh statistics
    function refreshStats() {
        fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                updateStatsDisplay(data);
            })
            .catch(error => {
                console.error('Error refreshing stats:', error);
            });
    }
    
    // Update statistics display
    function updateStatsDisplay(stats) {
        const statElements = document.querySelectorAll('[data-stat]');
        statElements.forEach(element => {
            const statType = element.getAttribute('data-stat');
            if (stats[statType] !== undefined) {
                element.textContent = stats[statType];
            }
        });
    }
    
    // Search functionality
    const searchForm = document.querySelector('form[action*="search"]');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = this.querySelector('input[name="q"]');
            if (!searchInput.value.trim()) {
                e.preventDefault();
                searchInput.focus();
            }
        });
    }
    
    // Category filter functionality
    const categoryButtons = document.querySelectorAll('.btn-group .btn');
    categoryButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Remove active class from all buttons
            categoryButtons.forEach(btn => btn.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');
        });
    });
    
    // Article card interactions
    const articleCards = document.querySelectorAll('.card');
    articleCards.forEach(card => {
        // Add click handler for card body (excluding links)
        card.addEventListener('click', function(e) {
            if (!e.target.closest('a') && !e.target.closest('button')) {
                const link = this.querySelector('.card-title a');
                if (link) {
                    window.open(link.href, '_blank');
                }
            }
        });
        
        // Add hover effect
        card.addEventListener('mouseenter', function() {
            this.style.cursor = 'pointer';
        });
    });
    
    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search focus
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[name="q"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape key to close modals
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            });
        }
    });
    
    // Notification system
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
    
    // Export functionality
    window.exportArticles = function(format = 'json') {
        const articles = Array.from(document.querySelectorAll('.card')).map(card => {
            const title = card.querySelector('.card-title a')?.textContent || '';
            const description = card.querySelector('.card-text')?.textContent || '';
            const url = card.querySelector('.card-title a')?.href || '';
            const source = card.querySelector('small')?.textContent || '';
            const date = card.querySelector('small.text-muted')?.textContent || '';
            
            return { title, description, url, source, date };
        });
        
        if (format === 'json') {
            const dataStr = JSON.stringify(articles, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'agritech-articles.json';
            link.click();
        } else if (format === 'csv') {
            const csvContent = 'data:text/csv;charset=utf-8,' + 
                'Title,Description,URL,Source,Date\n' +
                articles.map(article => 
                    `"${article.title}","${article.description}","${article.url}","${article.source}","${article.date}"`
                ).join('\n');
            
            const link = document.createElement('a');
            link.href = encodeURI(csvContent);
            link.download = 'agritech-articles.csv';
            link.click();
        }
    };
    
    // Start auto-refresh if on main page
    if (window.location.pathname === '/' || window.location.pathname === '') {
        startAutoRefresh();
    }
}); 