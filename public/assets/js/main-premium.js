/* ===========================
   GSAP & ScrollTrigger Setup
   =========================== */
gsap.registerPlugin(ScrollTrigger);

// Default animation settings
const animConfig = {
    duration: 0.6,
    stagger: 0.05,
    ease: 'power3.out'
};

/* ===========================
   UTILITY FUNCTIONS
   =========================== */
const Verity = {
    // Initialize all animations
    init() {
        this.setupDarkMode();
        this.setupNavigation();
        this.setupHeroAnimations();
        this.setupSectionAnimations();
        this.setupInteractions();
        this.setupFormHandling();
        this.setupCounterAnimations();
    },

    // Dark mode toggle
    setupDarkMode() {
        const themeToggle = document.querySelector('.theme-toggle');
        const htmlElement = document.documentElement;
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        // Initialize based on localStorage or system preference
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            if (savedTheme === 'dark') htmlElement.classList.add('dark-mode');
        } else if (prefersDark) {
            htmlElement.classList.add('dark-mode');
        }

        // Toggle handler
        themeToggle?.addEventListener('click', () => {
            htmlElement.classList.toggle('dark-mode');
            const isDark = htmlElement.classList.contains('dark-mode');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            
            // Animate the icon
            gsap.to(themeToggle, {
                duration: 0.3,
                rotation: 360,
                ease: 'back.out'
            });
        });
    },

    // Navigation smooth scroll and active state
    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                const href = link.getAttribute('href');
                if (href && href.startsWith('#')) {
                    e.preventDefault();
                    const target = document.querySelector(href);
                    if (target) {
                        gsap.to(window, {
                            duration: 0.8,
                            scrollTo: { y: target, offsetY: 100 },
                            ease: 'power3.inOut'
                        });
                    }
                }
            });
        });

        // Update active link on scroll
        window.addEventListener('scroll', () => {
            navLinks.forEach(link => {
                const href = link.getAttribute('href');
                if (href && href.startsWith('#')) {
                    const target = document.querySelector(href);
                    if (target) {
                        const rect = target.getBoundingClientRect();
                        if (rect.top < window.innerHeight * 0.3 && rect.bottom > window.innerHeight * 0.3) {
                            navLinks.forEach(l => l.classList.remove('active'));
                            link.classList.add('active');
                        }
                    }
                }
            });
        });
    },

    // Hero section animations
    setupHeroAnimations() {
        const heroSection = document.querySelector('.hero');
        if (!heroSection) return;

        // Create a timeline for hero entrance
        const heroTimeline = gsap.timeline();

        // Animate text split
        const textSplits = document.querySelectorAll('.hero-title .text-split');
        textSplits.forEach((element, index) => {
            heroTimeline.to(
                element,
                {
                    opacity: 1,
                    y: 0,
                    duration: 0.8,
                    ease: 'cubic-bezier(0.23, 0.32, 0.23, 0.2)'
                },
                index === 0 ? 0.2 : `-=0.3`
            );
        });

        // Animate description
        heroTimeline.to(
            '.hero-description',
            {
                opacity: 1,
                y: 0,
                duration: 0.8,
                ease: 'cubic-bezier(0.23, 0.32, 0.23, 0.2)'
            },
            '-=0.5'
        );

        // Animate buttons
        heroTimeline.to(
            '.hero-buttons',
            {
                opacity: 1,
                y: 0,
                duration: 0.8,
                ease: 'cubic-bezier(0.23, 0.32, 0.23, 0.2)'
            },
            '-=0.5'
        );

        // Animate stats
        heroTimeline.to(
            '.hero-stats',
            {
                opacity: 1,
                y: 0,
                duration: 0.8,
                ease: 'cubic-bezier(0.23, 0.32, 0.23, 0.2)'
            },
            '-=0.5'
        );

        // Animate verification card
        gsap.to('.verification-card', {
            opacity: 1,
            duration: 1,
            ease: 'power2.out'
        });
    },

    // Section animations on scroll
    setupSectionAnimations() {
        // Service cards
        const serviceCards = document.querySelectorAll('.service-card');
        serviceCards.forEach((card, index) => {
            ScrollTrigger.create({
                trigger: card,
                onEnter: () => {
                    gsap.from(card, {
                        opacity: 0,
                        y: 60,
                        duration: 0.8,
                        delay: index * 0.1,
                        ease: 'power3.out'
                    });
                },
                once: true
            });
        });

        // Process steps
        const processSteps = document.querySelectorAll('.process-step');
        processSteps.forEach((step, index) => {
            ScrollTrigger.create({
                trigger: step,
                onEnter: () => {
                    gsap.from(step, {
                        opacity: 0,
                        y: 40,
                        duration: 0.8,
                        delay: index * 0.15,
                        ease: 'power3.out'
                    });
                },
                once: true
            });
        });

        // Feature cards
        const featureCards = document.querySelectorAll('.feature-card');
        featureCards.forEach((card, index) => {
            ScrollTrigger.create({
                trigger: card,
                onEnter: () => {
                    gsap.from(card, {
                        opacity: 0,
                        y: 40,
                        duration: 0.8,
                        delay: index * 0.08,
                        ease: 'power3.out'
                    });
                },
                once: true
            });
        });

        // Testimonials
        const testimonials = document.querySelectorAll('.testimonial-card');
        testimonials.forEach((card, index) => {
            ScrollTrigger.create({
                trigger: card,
                onEnter: () => {
                    gsap.from(card, {
                        opacity: 0,
                        y: 40,
                        duration: 0.8,
                        delay: index * 0.1,
                        ease: 'power3.out'
                    });
                },
                once: true
            });
        });

        // Price cards
        const priceCards = document.querySelectorAll('.price-card');
        priceCards.forEach((card, index) => {
            ScrollTrigger.create({
                trigger: card,
                onEnter: () => {
                    gsap.from(card, {
                        opacity: 0,
                        y: 60,
                        duration: 0.8,
                        delay: index * 0.12,
                        ease: 'power3.out'
                    });
                },
                once: true
            });
        });

        // Section headers
        const sectionHeaders = document.querySelectorAll('.section-header');
        sectionHeaders.forEach(header => {
            ScrollTrigger.create({
                trigger: header,
                onEnter: () => {
                    const label = header.querySelector('.section-label');
                    const title = header.querySelector('h2');
                    
                    gsap.timeline()
                        .from(label, {
                            opacity: 0,
                            y: 20,
                            duration: 0.6,
                            ease: 'power3.out'
                        }, 0)
                        .from(title, {
                            opacity: 0,
                            y: 30,
                            duration: 0.8,
                            ease: 'power3.out'
                        }, '-=0.3');
                },
                once: true
            });
        });
    },

    // Interactive hover effects
    setupInteractions() {
        // Service cards hover
        document.querySelectorAll('.service-card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                gsap.to(card, {
                    y: -10,
                    duration: 0.4,
                    ease: 'power2.out'
                });
            });
            card.addEventListener('mouseleave', () => {
                gsap.to(card, {
                    y: 0,
                    duration: 0.4,
                    ease: 'power2.out'
                });
            });
        });

        // Feature cards hover
        document.querySelectorAll('.feature-card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                gsap.to(card, {
                    y: -8,
                    duration: 0.3,
                    ease: 'power2.out'
                });
            });
            card.addEventListener('mouseleave', () => {
                gsap.to(card, {
                    y: 0,
                    duration: 0.3,
                    ease: 'power2.out'
                });
            });
        });

        // Buttons hover effect
        document.querySelectorAll('.btn').forEach(button => {
            button.addEventListener('mouseenter', () => {
                gsap.to(button, {
                    scale: 1.05,
                    duration: 0.3,
                    ease: 'back.out'
                });
            });
            button.addEventListener('mouseleave', () => {
                gsap.to(button, {
                    scale: 1,
                    duration: 0.3,
                    ease: 'back.out'
                });
            });
        });

        // Process step icons hover
        document.querySelectorAll('.process-step').forEach(step => {
            const icon = step.querySelector('.step-icon');
            step.addEventListener('mouseenter', () => {
                if (icon) {
                    gsap.to(icon, {
                        scale: 1.15,
                        duration: 0.4,
                        ease: 'elastic.out'
                    });
                }
            });
            step.addEventListener('mouseleave', () => {
                if (icon) {
                    gsap.to(icon, {
                        scale: 1,
                        duration: 0.4,
                        ease: 'elastic.out'
                    });
                }
            });
        });
    },

    // Form handling and validation
    setupFormHandling() {
        const form = document.querySelector('.contact-form');
        if (!form) return;

        // Input focus animations
        form.querySelectorAll('input, textarea').forEach(input => {
            input.addEventListener('focus', function() {
                gsap.to(this, {
                    scale: 1.02,
                    duration: 0.3,
                    ease: 'power2.out'
                });
            });
            input.addEventListener('blur', function() {
                gsap.to(this, {
                    scale: 1,
                    duration: 0.3,
                    ease: 'power2.out'
                });
            });
        });

        // Form submission
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const submitButton = form.querySelector('button[type="submit"]');
            const formData = new FormData(form);

            try {
                // Disable button and show loading state
                submitButton.disabled = true;
                gsap.to(submitButton, {
                    opacity: 0.6,
                    duration: 0.3
                });

                // Simulate API call
                await new Promise(resolve => setTimeout(resolve, 1500));

                // Success animation
                form.style.pointerEvents = 'none';
                gsap.timeline()
                    .to(form, {
                        opacity: 0,
                        y: 20,
                        duration: 0.4
                    })
                    .call(() => {
                        form.innerHTML = `
                            <div style="text-align: center; padding: 2rem;">
                                <p style="font-size: 1.2rem; color: var(--success); font-weight: 600;">
                                    ✓ Message sent successfully!
                                </p>
                                <p style="color: var(--text-secondary); margin-top: 0.5rem;">
                                    We'll get back to you within 24 hours.
                                </p>
                            </div>
                        `;
                    })
                    .to(form, {
                        opacity: 1,
                        y: 0,
                        duration: 0.4
                    });

            } catch (error) {
                console.error('Form submission error:', error);
                submitButton.disabled = false;
                gsap.to(submitButton, {
                    opacity: 1,
                    duration: 0.3
                });
            }
        });
    },

    // Counter animations for statistics
    setupCounterAnimations() {
        const statValues = document.querySelectorAll('.stat-value');
        
        statValues.forEach(element => {
            const finalValue = element.textContent.trim();
            const numberMatch = finalValue.match(/\d+/);
            
            if (numberMatch) {
                const targetNumber = parseInt(numberMatch[0]);
                const suffix = finalValue.replace(/\d+/, '');

                ScrollTrigger.create({
                    trigger: element,
                    onEnter: () => {
                        gsap.fromTo(element, 
                            { textContent: 0 },
                            {
                                textContent: targetNumber,
                                duration: 2.5,
                                snap: { textContent: 1 },
                                ease: 'power1.inOut',
                                onUpdate: function() {
                                    element.textContent = Math.ceil(this.targets()[0].textContent) + suffix;
                                }
                            }
                        );
                    },
                    once: true
                });
            }
        });
    }
};

/* ===========================
   INITIALIZATION
   =========================== */
document.addEventListener('DOMContentLoaded', () => {
    Verity.init();
});

/* ===========================
   GSAP PLUGIN: ScrollToPlugin
   Add smooth scrolling support
   =========================== */
if (!gsap.plugins.scrollTo) {
    gsap.registerPlugin(
        class ScrollToPlugin {
            static register() {
                gsap.registerPlugin(ScrollToPlugin);
            }
        }
    );
}

/* ===========================
   KEYBOARD SHORTCUTS
   =========================== */
document.addEventListener('keydown', (e) => {
    // Ctrl+K or Cmd+K: Open search/command palette
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        console.log('Command palette would open here');
    }
    
    // Escape: Close modals or search
    if (e.key === 'Escape') {
        console.log('Modal would close here');
    }
});

/* ===========================
   PERFORMANCE OPTIMIZATION
   =========================== */

// Throttle scroll events
let ticking = false;
window.addEventListener('scroll', () => {
    if (!ticking) {
        window.requestAnimationFrame(() => {
            ticking = false;
        });
        ticking = true;
    }
});

// Kill animations on device orientation change
window.addEventListener('orientationchange', () => {
    ScrollTrigger.getAll().forEach(trigger => trigger.kill());
});

// Export Verity for debugging
window.Verity = Verity;
