// ================================================
// VERITY SYSTEMS - SEO ENHANCEMENTS
// Structured data, meta tags, and social cards
// ================================================

(function() {
    'use strict';

    const VeritySEO = {
        // Default meta data
        defaults: {
            siteName: 'Verity Systems',
            title: 'Verity — AI Fact-Checking That Shows Its Work',
            description: 'AI-powered fact-checking platform with 20+ models and 40+ trusted sources. Verify claims instantly with our 21-point verification system.',
            image: 'https://veritysystems.app/assets/images/og-image.png',
            url: 'https://veritysystems.app',
            twitterHandle: '@veritysystems',
            locale: 'en_US'
        },

        // Initialize SEO
        init() {
            this.addStructuredData();
            this.addOpenGraphTags();
            this.addTwitterCards();
            this.addCanonicalUrl();
        },

        // Add JSON-LD structured data
        addStructuredData() {
            const page = window.location.pathname;
            
            // Organization data (all pages)
            this.addJsonLd({
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": "Verity Systems",
                "url": "https://veritysystems.app",
                "logo": "https://veritysystems.app/assets/images/logo.png",
                "sameAs": [
                    "https://twitter.com/veritysystems",
                    "https://github.com/veritysystems"
                ],
                "contactPoint": {
                    "@type": "ContactPoint",
                    "contactType": "customer support",
                    "email": "support@veritysystems.app"
                }
            });

            // Software application data
            this.addJsonLd({
                "@context": "https://schema.org",
                "@type": "SoftwareApplication",
                "name": "Verity",
                "applicationCategory": "UtilitiesApplication",
                "operatingSystem": "Web, Chrome Extension, iOS, Android",
                "offers": {
                    "@type": "Offer",
                    "price": "0",
                    "priceCurrency": "USD"
                },
                "description": "AI-powered fact-checking platform that verifies claims using 20+ AI models and 40+ trusted sources.",
                "aggregateRating": {
                    "@type": "AggregateRating",
                    "ratingValue": "4.8",
                    "ratingCount": "1247"
                }
            });

            // Page-specific data
            if (page.includes('pricing')) {
                this.addPricingStructuredData();
            } else if (page.includes('api-docs')) {
                this.addApiDocsStructuredData();
            } else if (page === '/' || page.includes('index')) {
                this.addHomeStructuredData();
            }
        },

        // Home page structured data
        addHomeStructuredData() {
            this.addJsonLd({
                "@context": "https://schema.org",
                "@type": "WebSite",
                "name": "Verity Systems",
                "url": "https://veritysystems.app",
                "potentialAction": {
                    "@type": "SearchAction",
                    "target": "https://veritysystems.app/verify.html?claim={search_term_string}",
                    "query-input": "required name=search_term_string"
                }
            });

            // FAQ data for home page
            this.addJsonLd({
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": "What is Verity?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Verity is an AI-powered fact-checking platform that uses 20+ AI models and 40+ trusted sources to verify claims instantly."
                        }
                    },
                    {
                        "@type": "Question",
                        "name": "How does the 21-point verification system work?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Our 21-point system runs 21 independent checks across 7 pillars — source, time, evidence, consensus, logic, method, and bias — and produces a clear summary and confidence score."
                        }
                    },
                    {
                        "@type": "Question",
                        "name": "Is there a free tier?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Yes! Verity offers a free tier with 300 verifications per month. No credit card required."
                        }
                    }
                ]
            });
        },

        // Pricing page structured data
        addPricingStructuredData() {
            this.addJsonLd({
                "@context": "https://schema.org",
                "@type": "Product",
                "name": "Verity Verification Platform",
                "description": "AI-powered fact-checking and claim verification platform",
                "brand": {
                    "@type": "Brand",
                    "name": "Verity Systems"
                },
                "offers": [
                    {
                        "@type": "Offer",
                        "name": "Free",
                        "price": "0",
                        "priceCurrency": "USD",
                        "description": "300 verifications/month"
                    },
                    {
                        "@type": "Offer",
                        "name": "Starter",
                        "price": "9",
                        "priceCurrency": "USD",
                        "billingDuration": "P1M",
                        "description": "1,200 verifications/month"
                    },
                    {
                        "@type": "Offer",
                        "name": "Pro",
                        "price": "29",
                        "priceCurrency": "USD",
                        "billingDuration": "P1M",
                        "description": "5,000 verifications/month"
                    },
                    {
                        "@type": "Offer",
                        "name": "Business",
                        "price": "99",
                        "priceCurrency": "USD",
                        "billingDuration": "P1M",
                        "description": "25,000 verifications/month"
                    }
                ]
            });
        },

        // API docs structured data
        addApiDocsStructuredData() {
            this.addJsonLd({
                "@context": "https://schema.org",
                "@type": "TechArticle",
                "headline": "Verity API Documentation",
                "description": "Complete API reference for integrating Verity fact-checking into your applications",
                "author": {
                    "@type": "Organization",
                    "name": "Verity Systems"
                },
                "datePublished": "2026-01-01",
                "dateModified": "2026-01-12"
            });
        },

        // Add JSON-LD script
        addJsonLd(data) {
            const script = document.createElement('script');
            script.type = 'application/ld+json';
            script.textContent = JSON.stringify(data);
            document.head.appendChild(script);
        },

        // Add Open Graph tags
        addOpenGraphTags() {
            const meta = this.getPageMeta();
            
            this.setMetaTag('property', 'og:site_name', this.defaults.siteName);
            this.setMetaTag('property', 'og:type', 'website');
            this.setMetaTag('property', 'og:title', meta.title);
            this.setMetaTag('property', 'og:description', meta.description);
            this.setMetaTag('property', 'og:image', meta.image);
            this.setMetaTag('property', 'og:url', meta.url);
            this.setMetaTag('property', 'og:locale', this.defaults.locale);
        },

        // Add Twitter Card tags
        addTwitterCards() {
            const meta = this.getPageMeta();
            
            this.setMetaTag('name', 'twitter:card', 'summary_large_image');
            this.setMetaTag('name', 'twitter:site', this.defaults.twitterHandle);
            this.setMetaTag('name', 'twitter:title', meta.title);
            this.setMetaTag('name', 'twitter:description', meta.description);
            this.setMetaTag('name', 'twitter:image', meta.image);
        },

        // Add canonical URL
        addCanonicalUrl() {
            const url = window.location.origin + window.location.pathname;
            
            let canonical = document.querySelector('link[rel="canonical"]');
            if (!canonical) {
                canonical = document.createElement('link');
                canonical.rel = 'canonical';
                document.head.appendChild(canonical);
            }
            canonical.href = url;
        },

        // Get page-specific meta
        getPageMeta() {
            const page = window.location.pathname;
            const pageMeta = {
                '/verify.html': {
                    title: 'Verify Claims | Verity',
                    description: 'Instantly verify any claim with our AI-powered 21-point verification system. Cross-reference 40+ trusted sources.'
                },
                '/pricing.html': {
                    title: 'Pricing | Verity',
                    description: 'Simple, transparent pricing. Start free with 300 verifications/month. Scale as you grow.'
                },
                '/api-docs.html': {
                    title: 'API Documentation | Verity',
                    description: 'Integrate fact-checking into your apps with our RESTful API. Full documentation and examples.'
                },
                '/tools.html': {
                    title: 'Verification Tools | Verity',
                    description: 'Explore our suite of fact-checking tools: batch verification, source checker, misinformation map, and more.'
                },
                '/auth.html': {
                    title: 'Sign In | Verity',
                    description: 'Sign in to your Verity account to access your dashboard and verification history.'
                }
            };

            const currentMeta = pageMeta[page] || {};
            
            return {
                title: currentMeta.title || document.title || this.defaults.title,
                description: currentMeta.description || document.querySelector('meta[name="description"]')?.content || this.defaults.description,
                image: this.defaults.image,
                url: window.location.href
            };
        },

        // Set meta tag
        setMetaTag(attribute, name, content) {
            let tag = document.querySelector(`meta[${attribute}="${name}"]`);
            if (!tag) {
                tag = document.createElement('meta');
                tag.setAttribute(attribute, name);
                document.head.appendChild(tag);
            }
            tag.setAttribute('content', content);
        }
    };

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => VeritySEO.init());
    } else {
        VeritySEO.init();
    }

    // Export
    window.VeritySEO = VeritySEO;

})();
