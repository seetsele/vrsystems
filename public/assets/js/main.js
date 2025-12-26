// ===========================
// DARK MODE TOGGLE
// ===========================
const themeToggle = document.querySelector('.theme-toggle');
const htmlElement = document.documentElement;

// Check for saved theme preference or default to light mode
const currentTheme = localStorage.getItem('theme') || 'light';
if (currentTheme === 'dark') {
    htmlElement.classList.add('dark-mode');
}

// Toggle dark mode
themeToggle.addEventListener('click', () => {
    htmlElement.classList.toggle('dark-mode');
    const theme = htmlElement.classList.contains('dark-mode') ? 'dark' : 'light';
    localStorage.setItem('theme', theme);
    updateThemeIcon();
});

function updateThemeIcon() {
    const icon = themeToggle.querySelector('i');
    if (htmlElement.classList.contains('dark-mode')) {
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
    } else {
        icon.classList.remove('fa-sun');
        icon.classList.add('fa-moon');
    }
}

updateThemeIcon();

// ===========================
// SMOOTH SCROLLING
// ===========================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ===========================
// NAVBAR SCROLL EFFECT
// ===========================
let lastScrollTop = 0;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    if (scrollTop > 100) {
        navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.1)';
    } else {
        navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.08)';
    }
    
    lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
});

// ===========================
// INTERSECTION OBSERVER FOR ANIMATIONS
// ===========================
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

document.querySelectorAll('.service-card, .feature-item, .testimonial-card, .price-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
    observer.observe(el);
});

// ===========================
// CONTACT FORM HANDLING
// ===========================
const contactForm = document.getElementById('contactForm');

if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const button = contactForm.querySelector('button');
        const originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
        
        const formData = new FormData(contactForm);
        const data = Object.fromEntries(formData);
        
        try {
            // FOR NOW: Log form data (EmailJS integration would go here)
            console.log('Form submitted:', data);
            
            // Simulate sending
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // Show success message
            button.innerHTML = '<i class="fas fa-check"></i> Message Sent!';
            button.style.background = '#10B981';
            
            contactForm.reset();
            
            // Reset button after 3 seconds
            setTimeout(() => {
                button.innerHTML = originalText;
                button.style.background = '';
                button.disabled = false;
            }, 3000);
            
        } catch (error) {
            console.error('Error:', error);
            button.innerHTML = '<i class="fas fa-exclamation-circle"></i> Error Sending';
            button.style.background = '#EF4444';
            
            setTimeout(() => {
                button.innerHTML = originalText;
                button.style.background = '';
                button.disabled = false;
            }, 3000);
        }
    });
}

// ===========================
// DYNAMIC STAT COUNTER
// ===========================
function animateCounter(element, target, duration = 2000) {
    let current = 0;
    const increment = target / (duration / 16);
    
    const interval = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target;
            clearInterval(interval);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 16);
}

// Trigger counters when stats section is visible
const statsSection = document.querySelector('.stats');
if (statsSection) {
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                document.querySelectorAll('.stat-number').forEach(stat => {
                    const text = stat.textContent;
                    const number = parseInt(text);
                    if (!isNaN(number)) {
                        animateCounter(stat, number);
                    }
                });
                statsObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    statsObserver.observe(statsSection);
}

// ===========================
// KEYBOARD SHORTCUTS
// ===========================
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K to focus search (if added)
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        // Focus search input here when added
    }
    
    // Escape to close any modals
    if (e.key === 'Escape') {
        // Close modals here
    }
});

// ===========================
// FORM VALIDATION
// ===========================
const validateEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
};

if (contactForm) {
    const emailInput = contactForm.querySelector('input[type="email"]');
    if (emailInput) {
        emailInput.addEventListener('blur', () => {
            if (!validateEmail(emailInput.value)) {
                emailInput.style.borderColor = '#EF4444';
            } else {
                emailInput.style.borderColor = '';
            }
        });
    }
}

// ===========================
// ANALYTICS TRACKING (placeholder)
// ===========================
function trackEvent(eventName, eventData) {
    console.log(`Event: ${eventName}`, eventData);
    // Google Analytics or similar would go here
}

document.querySelectorAll('a.cta-button, a.btn-primary').forEach(btn => {
    btn.addEventListener('click', () => {
        trackEvent('cta_click', { button: btn.textContent });
    });
});

// ===========================
// MOBILE MENU TOGGLE
// ===========================
function setupMobileMenu() {
    const navLinks = document.querySelector('.nav-links');
    const navContainer = document.querySelector('.nav-container');
    
    // Only for mobile
    if (window.innerWidth <= 768) {
        const menuButton = document.createElement('button');
        menuButton.className = 'mobile-menu-toggle';
        menuButton.innerHTML = '<i class="fas fa-bars"></i>';
        menuButton.style.cssText = `
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: var(--text-primary);
            display: flex;
        `;
        
        navContainer.insertBefore(menuButton, navLinks);
        
        menuButton.addEventListener('click', () => {
            navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
        });
    }
}

setupMobileMenu();
window.addEventListener('resize', setupMobileMenu);

// ===========================
// PERFORMANCE: Lazy load images
// ===========================
if ('IntersectionObserver' in window) {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

console.log('%cVerity Systems - Truth at Speed', 'color: #0066FF; font-size: 20px; font-weight: bold;');
