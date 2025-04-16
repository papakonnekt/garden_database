// Main JavaScript file for Garden Database

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Filter functionality for list views
    const filterDropdown = document.getElementById('filterDropdown');
    if (filterDropdown) {
        const filterLinks = filterDropdown.querySelectorAll('.dropdown-item');
        filterLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                // Add active class to selected filter
                filterLinks.forEach(l => l.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }
    
    // Search form validation
    const searchForm = document.querySelector('form[action*="search"]');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = this.querySelector('input[name="q"]');
            if (!searchInput.value.trim()) {
                e.preventDefault();
                searchInput.classList.add('is-invalid');
            } else {
                searchInput.classList.remove('is-invalid');
            }
        });
    }
    
    // Image error handling
    document.querySelectorAll('img').forEach(img => {
        img.addEventListener('error', function() {
            // Replace broken images with a placeholder
            this.src = '/static/img/placeholder.png';
            this.alt = 'Image not available';
        });
    });
    
    // Companion planting interactive features
    const companionshipTable = document.getElementById('companionship-table');
    if (companionshipTable) {
        // Add sorting functionality
        const headers = companionshipTable.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.addEventListener('click', function() {
                const sortBy = this.getAttribute('data-sort');
                const sortOrder = this.classList.contains('sort-asc') ? 'desc' : 'asc';
                
                // Update header classes
                headers.forEach(h => {
                    h.classList.remove('sort-asc', 'sort-desc');
                });
                this.classList.add(`sort-${sortOrder}`);
                
                // Sort the table rows
                sortTable(companionshipTable, sortBy, sortOrder);
            });
        });
    }
    
    // Function to sort table rows
    function sortTable(table, sortBy, sortOrder) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        rows.sort((a, b) => {
            const aValue = a.querySelector(`td[data-${sortBy}]`).getAttribute(`data-${sortBy}`);
            const bValue = b.querySelector(`td[data-${sortBy}]`).getAttribute(`data-${sortBy}`);
            
            if (sortOrder === 'asc') {
                return aValue.localeCompare(bValue);
            } else {
                return bValue.localeCompare(aValue);
            }
        });
        
        // Remove existing rows
        rows.forEach(row => row.remove());
        
        // Append sorted rows
        rows.forEach(row => tbody.appendChild(row));
    }
    
    // Plant detail page tabs
    const plantDetailTabs = document.getElementById('plant-detail-tabs');
    if (plantDetailTabs) {
        const tabLinks = plantDetailTabs.querySelectorAll('.nav-link');
        tabLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Update active tab
                tabLinks.forEach(l => l.classList.remove('active'));
                this.classList.add('active');
                
                // Show corresponding tab content
                const tabId = this.getAttribute('href');
                document.querySelectorAll('.tab-pane').forEach(pane => {
                    pane.classList.remove('show', 'active');
                });
                document.querySelector(tabId).classList.add('show', 'active');
            });
        });
    }
});
