/* =============================================
   Base JavaScript - HealthSphere AI
   ============================================= */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Auto-hide loading overlay
    setTimeout(() => {
        const loading = document.getElementById('app-loading');
        if (loading) {
            loading.style.display = 'none';
        }
    }, 500);

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Form validation helper
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea[data-auto-resize]');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });

    // Dashboard metrics animations
    const counters = document.querySelectorAll('.metric-value[data-animate]');
    const animateCounter = (counter) => {
        const target = parseInt(counter.textContent);
        const increment = target / 50;
        let current = 0;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                counter.textContent = target;
                clearInterval(timer);
            } else {
                counter.textContent = Math.floor(current);
            }
        }, 20);
    };

    // Animate counters when they come into view
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        });

        counters.forEach(counter => observer.observe(counter));
    } else {
        // Fallback for older browsers
        counters.forEach(animateCounter);
    }

    // Health score color updates
    const healthScores = document.querySelectorAll('.health-score');
    healthScores.forEach(score => {
        const value = parseInt(score.textContent);
        if (value >= 85) {
            score.classList.add('score-excellent');
        } else if (value >= 70) {
            score.classList.add('score-good');
        } else if (value >= 50) {
            score.classList.add('score-fair');
        } else {
            score.classList.add('score-poor');
        }
    });

    // Notification auto-dismiss
    const alerts = document.querySelectorAll('.alert[data-auto-dismiss]');
    alerts.forEach(alert => {
        const timeout = parseInt(alert.dataset.autoDismiss) || 5000;
        setTimeout(() => {
            if (alert.classList.contains('show')) {
                alert.classList.remove('show');
                setTimeout(() => alert.remove(), 300);
            }
        }, timeout);
    });

    // Search functionality
    const searchInputs = document.querySelectorAll('input[data-search-target]');
    searchInputs.forEach(input => {
        const target = input.dataset.searchTarget;
        const items = document.querySelectorAll(target);
        
        input.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(query)) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });

    console.log('HealthSphere AI - Base JavaScript loaded successfully');
});

// Health score calculation utilities
window.HealthSphere = {
    calculateHealthScore: function(metrics) {
        if (!metrics || metrics.length === 0) return 75;
        
        let totalScore = 0;
        let count = 0;
        
        metrics.forEach(metric => {
            let score = 50; // Base score
            
            switch(metric.type) {
                case 'weight':
                    // Simple weight score (this would be more complex in real app)
                    score = Math.min(100, Math.max(0, 100 - Math.abs(metric.value - 70)));
                    break;
                case 'blood_pressure':
                    // Blood pressure score
                    if (metric.value < 120) score = 100;
                    else if (metric.value < 140) score = 80;
                    else if (metric.value < 160) score = 60;
                    else score = 40;
                    break;
                case 'heart_rate':
                    // Heart rate score
                    if (metric.value >= 60 && metric.value <= 80) score = 100;
                    else if (metric.value >= 50 && metric.value <= 100) score = 80;
                    else score = 60;
                    break;
                default:
                    score = 75;
            }
            
            totalScore += score;
            count++;
        });
        
        return count > 0 ? Math.round(totalScore / count) : 75;
    },
    
    formatHealthMetric: function(value, type) {
        switch(type) {
            case 'weight':
                return value + ' kg';
            case 'blood_pressure':
                return value + ' mmHg';
            case 'heart_rate':
                return value + ' bpm';
            case 'temperature':
                return value + '°C';
            default:
                return value;
        }
    },
    
    getHealthScoreClass: function(score) {
        if (score >= 85) return 'score-excellent';
        if (score >= 70) return 'score-good';
        if (score >= 50) return 'score-fair';
        return 'score-poor';
    }
};