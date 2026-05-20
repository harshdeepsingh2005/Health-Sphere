/*
===============================================
HealthSphere AI - Main JavaScript
===============================================
Minimal JavaScript for basic interactivity.
College-level healthcare platform.
===============================================
*/

// Global sidebar state
let sidebarOverlay = null;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initSidebar();
    initAlerts();
    initFormValidation();
    initTables();
    initModals();
    initTooltips();
    initUserDropdown();
    initHealthRing();
});

/* =============================================
   Sidebar Toggle (Mobile)
   ============================================= */
function initSidebar() {
    const sidebar = document.querySelector('.sidebar');
    
    // Create overlay for mobile
    sidebarOverlay = document.createElement('div');
    sidebarOverlay.className = 'sidebar-overlay';
    document.body.appendChild(sidebarOverlay);
    
    // Close sidebar when clicking overlay
    sidebarOverlay.addEventListener('click', function() {
        closeSidebar();
    });
    
    // Close sidebar when pressing Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeSidebar();
        }
    });
    
    // Mark active nav link
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// Global toggle function for sidebar
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.classList.toggle('open');
        if (sidebarOverlay) {
            sidebarOverlay.classList.toggle('active');
        }
        document.body.classList.toggle('sidebar-open');
    }
}

// Close sidebar function
function closeSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.classList.remove('open');
        if (sidebarOverlay) {
            sidebarOverlay.classList.remove('active');
        }
        document.body.classList.remove('sidebar-open');
    }
}

/* =============================================
   Alert Dismissal
   ============================================= */
function initAlerts() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(function(alert) {
        const closeBtn = alert.querySelector('.alert-close');
        
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                alert.style.opacity = '0';
                setTimeout(function() {
                    alert.remove();
                }, 300);
            });
        }
        
        // Auto-dismiss success alerts after 5 seconds
        if (alert.classList.contains('alert-success')) {
            setTimeout(function() {
                alert.style.opacity = '0';
                setTimeout(function() {
                    alert.remove();
                }, 300);
            }, 5000);
        }
    });
}

/* =============================================
   Form Validation
   ============================================= */
function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            const requiredFields = form.querySelectorAll('[required]');
            
            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    isValid = false;
                    showFieldError(field, 'This field is required');
                } else {
                    clearFieldError(field);
                }
            });
            
            // Email validation
            const emailFields = form.querySelectorAll('input[type="email"]');
            emailFields.forEach(function(field) {
                if (field.value && !isValidEmail(field.value)) {
                    isValid = false;
                    showFieldError(field, 'Please enter a valid email address');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    });
}

function showFieldError(field, message) {
    clearFieldError(field);
    field.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/* =============================================
   Table Sorting (Basic)
   ============================================= */
function initTables() {
    const sortableHeaders = document.querySelectorAll('.data-table th[data-sort]');
    
    sortableHeaders.forEach(function(header) {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            const table = header.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const columnIndex = Array.from(header.parentNode.children).indexOf(header);
            const isAscending = header.classList.contains('sort-asc');
            
            // Remove sort classes from all headers
            sortableHeaders.forEach(function(h) {
                h.classList.remove('sort-asc', 'sort-desc');
            });
            
            // Sort rows
            rows.sort(function(a, b) {
                const aValue = a.children[columnIndex].textContent.trim();
                const bValue = b.children[columnIndex].textContent.trim();
                
                if (isAscending) {
                    return bValue.localeCompare(aValue);
                } else {
                    return aValue.localeCompare(bValue);
                }
            });
            
            // Update sort indicator
            header.classList.add(isAscending ? 'sort-desc' : 'sort-asc');
            
            // Re-append sorted rows
            rows.forEach(function(row) {
                tbody.appendChild(row);
            });
        });
    });
}

/* =============================================
   Modal Handling
   ============================================= */
function initModals() {
    // Open modal
    document.querySelectorAll('[data-modal-target]').forEach(function(trigger) {
        trigger.addEventListener('click', function() {
            const modalId = this.getAttribute('data-modal-target');
            const modal = document.getElementById(modalId);
            if (modal) {
                openModal(modal);
            }
        });
    });
    
    // Close modal with close button
    document.querySelectorAll('.modal-close').forEach(function(closeBtn) {
        closeBtn.addEventListener('click', function() {
            const modal = this.closest('.modal');
            closeModal(modal);
        });
    });
    
    // Close modal when clicking outside
    document.querySelectorAll('.modal').forEach(function(modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal(modal);
            }
        });
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.open');
            if (openModal) {
                closeModal(openModal);
            }
        }
    });
}

function openModal(modal) {
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
}

function closeModal(modal) {
    modal.classList.remove('open');
    document.body.style.overflow = '';
}

/* =============================================
   Tooltips
   ============================================= */
function initTooltips() {
    const tooltipTriggers = document.querySelectorAll('[data-tooltip]');
    
    tooltipTriggers.forEach(function(trigger) {
        trigger.addEventListener('mouseenter', function() {
            const tooltipText = this.getAttribute('data-tooltip');
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = tooltipText;
            
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.top = (rect.top - tooltip.offsetHeight - 8) + 'px';
            tooltip.style.left = (rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2)) + 'px';
            
            this._tooltip = tooltip;
        });
        
        trigger.addEventListener('mouseleave', function() {
            if (this._tooltip) {
                this._tooltip.remove();
                this._tooltip = null;
            }
        });
    });
}

/* =============================================
   Utility Functions
   ============================================= */

// Format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Format time
function formatTime(dateString) {
    const options = { hour: 'numeric', minute: '2-digit', hour12: true };
    return new Date(dateString).toLocaleTimeString('en-US', options);
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// Show loading spinner
function showLoading(element) {
    element.classList.add('loading');
    element.disabled = true;
}

// Hide loading spinner
function hideLoading(element) {
    element.classList.remove('loading');
    element.disabled = false;
}

// Copy text to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showNotification('Copied to clipboard!', 'success');
    }).catch(function() {
        showNotification('Failed to copy', 'error');
    });
}

// Show notification
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(function() {
        notification.classList.add('show');
    }, 10);
    
    // Remove after 3 seconds
    setTimeout(function() {
        notification.classList.remove('show');
        setTimeout(function() {
            notification.remove();
        }, 300);
    }, 3000);
}

/* =============================================
   AJAX Helper (for future use)
   ============================================= */
async function fetchData(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

// Get CSRF token from cookie
function getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    
    return cookieValue;
}

/* =============================================
   Dashboard Charts (Placeholder)
   ============================================= */
function initCharts() {
    // This would be implemented with Chart.js or similar
    // For now, we use CSS-based visualizations
    console.log('Charts initialized (placeholder)');
}

/* =============================================
   File Upload Preview
   ============================================= */
function initFileUpload() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            const file = this.files[0];
            const preview = this.parentNode.querySelector('.file-preview');
            
            if (file && preview) {
                preview.textContent = file.name;
                preview.style.display = 'block';
            }
        });
    });
}

/* =============================================
   Search Functionality
   ============================================= */
function initSearch() {
    const searchInputs = document.querySelectorAll('.search-input');
    
    searchInputs.forEach(function(input) {
        input.addEventListener('input', debounce(function() {
            const searchTerm = this.value.toLowerCase();
            const targetId = this.getAttribute('data-search-target');
            const target = document.getElementById(targetId);
            
            if (target) {
                const items = target.querySelectorAll('.searchable');
                items.forEach(function(item) {
                    const text = item.textContent.toLowerCase();
                    item.style.display = text.includes(searchTerm) ? '' : 'none';
                });
            }
        }, 300));
    });
}

/* =============================================
   Confirmation Dialogs
   ============================================= */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Add confirmation to delete buttons
document.querySelectorAll('[data-confirm]').forEach(function(element) {
    element.addEventListener('click', function(e) {
        const message = this.getAttribute('data-confirm');
        if (!confirm(message)) {
            e.preventDefault();
        }
    });
});

/* =============================================
   Print Functionality
   ============================================= */
function printSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        const printWindow = window.open('', '_blank');
        printWindow.document.write('<html><head><title>Print</title>');
        printWindow.document.write('<link rel="stylesheet" href="/static/css/styles.css">');
        printWindow.document.write('</head><body>');
        printWindow.document.write(section.innerHTML);
        printWindow.document.write('</body></html>');
        printWindow.document.close();
        printWindow.print();
    }
}

/* =============================================
   Export to CSV (Basic)
   ============================================= */
function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(function(row) {
        const cols = row.querySelectorAll('td, th');
        const rowData = [];
        cols.forEach(function(col) {
            rowData.push('"' + col.textContent.replace(/"/g, '""') + '"');
        });
        csv.push(rowData.join(','));
    });
    
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename || 'export.csv';
    link.click();
}

/* =============================================
   User Dropdown Menu
   ============================================= */
function initUserDropdown() {
    const userDropdown = document.getElementById('userDropdown');
    if (!userDropdown) return;
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!userDropdown.contains(e.target)) {
            userDropdown.classList.remove('active');
        }
    });
}

// Global toggle function for user dropdown
function toggleUserDropdown() {
    const userDropdown = document.getElementById('userDropdown');
    if (userDropdown) {
        userDropdown.classList.toggle('active');
    }
}

/* =============================================
   Health Ring Animation
   ============================================= */
function initHealthRing() {
    const healthRings = document.querySelectorAll('.health-ring');
    
    healthRings.forEach(function(ring) {
        const score = parseInt(ring.getAttribute('data-score')) || 78;
        const circumference = 2 * Math.PI * 52; // r=52
        const offset = circumference - (score / 100) * circumference;
        
        const progressCircle = ring.querySelector('.ring-progress');
        if (progressCircle) {
            progressCircle.style.strokeDasharray = circumference;
            // Animate after a short delay
            setTimeout(function() {
                progressCircle.style.strokeDashoffset = offset;
            }, 300);
        }
    });
}

/* =============================================
   Scroll Animations
   ============================================= */
function initScrollAnimations() {
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.card, .stat-card, .bento-stat').forEach(function(el) {
        observer.observe(el);
    });
}

