// Mobile menu toggle
document.querySelector('.hamburger').addEventListener('click', function() {
    const navMenu = document.querySelector('.nav-menu');
    navMenu.classList.toggle('active');
    
    // Animate hamburger
    this.classList.toggle('active');
});

// Close menu when clicking on a link
document.querySelectorAll('.nav-menu a').forEach(link => {
    link.addEventListener('click', function() {
        const navMenu = document.querySelector('.nav-menu');
        const hamburger = document.querySelector('.hamburger');
        
        if (window.innerWidth <= 768) {
            navMenu.classList.remove('active');
            hamburger.classList.remove('active');
        }
    });
});

// Close menu when clicking outside
document.addEventListener('click', function(event) {
    const navMenu = document.querySelector('.nav-menu');
    const hamburger = document.querySelector('.hamburger');
    const navbar = document.querySelector('.navbar');
    
    if (!navbar.contains(event.target) && navMenu.classList.contains('active')) {
        navMenu.classList.remove('active');
        hamburger.classList.remove('active');
    }
});

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const headerOffset = 70;
            const elementPosition = target.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
            
            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// Scroll to contact section function
function scrollToContact() {
    const contactSection = document.querySelector('#contact');
    if (contactSection) {
        const headerOffset = 70;
        const elementPosition = contactSection.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
        
        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    }
}

// Add event listeners to all "تواصل معنا" buttons
document.addEventListener('DOMContentLoaded', function() {
    // Hero section button
    const heroButton = document.querySelector('.hero .btn-primary');
    if (heroButton) {
        heroButton.addEventListener('click', scrollToContact);
    }
    
    // Stats section button
    const statsButton = document.querySelector('.stats .btn-dark');
    if (statsButton) {
        statsButton.addEventListener('click', scrollToContact);
    }
    
    // Dark CTA section button
    const ctaButton = document.querySelector('.dark-cta .btn-primary');
    if (ctaButton) {
        ctaButton.addEventListener('click', scrollToContact);
    }
    
    // About section button
    const aboutButton = document.querySelector('.about .btn-dark');
    if (aboutButton) {
        aboutButton.addEventListener('click', scrollToContact);
    }
    
    // Customer service link in navigation
    const supportLink = document.querySelector('a[href="#support"]');
    if (supportLink) {
        supportLink.addEventListener('click', function(e) {
            e.preventDefault();
            scrollToContact();
        });
    }
});

// Form submission
document.getElementById('contactForm').addEventListener('submit', function(e) {
    e.preventDefault();
    alert('تم إرسال النموذج بنجاح! سنتواصل معك قريباً.');
    this.reset();
});

// WhatsApp button
function openWhatsApp() {
    window.open('https://api.whatsapp.com/send/?phone=966593394747&text&app_absent=0', '_blank');
}

// Partners slider functionality
let currentPartnerIndex = 0;

function scrollPartners(direction) {
    const track = document.querySelector('.partners-track');
    const items = document.querySelectorAll('.partner-item');
    const itemsVisible = getVisiblePartnersCount();
    const maxIndex = items.length - itemsVisible;
    
    currentPartnerIndex += direction;
    
    if (currentPartnerIndex < 0) {
        currentPartnerIndex = 0;
    } else if (currentPartnerIndex > maxIndex) {
        currentPartnerIndex = maxIndex;
    }
    
    const itemWidth = items[0].offsetWidth;
    const gap = 30;
    const offset = currentPartnerIndex * (itemWidth + gap);
    
    track.style.transform = `translateX(${offset}px)`;
}

function getVisiblePartnersCount() {
    const width = window.innerWidth;
    if (width <= 480) return 1;
    if (width <= 768) return 2;
    if (width <= 1024) return 3;
    return 5;
}

// Reset partner slider on window resize
window.addEventListener('resize', function() {
    currentPartnerIndex = 0;
    const track = document.querySelector('.partners-track');
    if (track) {
        track.style.transform = 'translateX(0)';
    }
});

// Service buttons functionality
document.addEventListener('DOMContentLoaded', function() {
    const serviceButtons = document.querySelectorAll('.btn-service');
    serviceButtons.forEach((button, index) => {
        button.addEventListener('click', function() {
            // Define service URLs
            const serviceUrls = [
                '/architectural-services/',  // الخدمات المعمارية
                '/structural-services/',     // الخدمات الإنشائية
                '/design-services/'          // التصاميم
            ];
            
            // Redirect to the appropriate service page
            if (serviceUrls[index]) {
                window.location.href = serviceUrls[index];
            }
        });
    });
    
    // Project cards functionality
    const projectCards = document.querySelectorAll('.project-card');
    projectCards.forEach((card, index) => {
        card.style.cursor = 'pointer';
        card.addEventListener('click', function() {
            // For now, redirect to project 1 (you can create more project pages later)
            window.location.href = `/project/${index + 1}/`;
        });
    });
});

// Navbar background on scroll
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.background = 'rgba(255, 255, 255, 0.95)';
        navbar.style.boxShadow = '0 4px 10px rgba(0, 0, 0, 0.15)';
    } else {
        navbar.style.background = 'rgba(255, 255, 255, 0.6)';
        navbar.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
    }
});

// Animate stats on scroll
function animateStats() {
    const stats = document.querySelectorAll('.stat-number');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                const text = target.textContent;
                const number = parseInt(text.replace(/[^\d]/g, ''));
                const prefix = text.replace(/[\d,]/g, '');
                let current = 0;
                const increment = number / 100;
                
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= number) {
                        current = number;
                        clearInterval(timer);
                    }
                    target.textContent = prefix + Math.floor(current).toLocaleString();
                }, 20);
                
                observer.unobserve(target);
            }
        });
    }, { threshold: 0.5 });
    
    stats.forEach(stat => observer.observe(stat));
}

// Animate elements on scroll
function animateOnScroll() {
    const elements = document.querySelectorAll('.project-card, .service-card, .stat-item, .about-images img, .partner-item');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });
    
    elements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

// Initialize animations when page loads
window.addEventListener('load', function() {
    animateStats();
    animateOnScroll();
});

// Add loading animation for images
document.querySelectorAll('img').forEach(img => {
    img.addEventListener('load', function() {
        this.style.opacity = '1';
    });
    
    if (!img.complete) {
        img.style.opacity = '0';
        img.style.transition = 'opacity 0.3s ease';
    }
});

// Handle window resize
let resizeTimer;
window.addEventListener('resize', function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function() {
        const navMenu = document.querySelector('.nav-menu');
        const hamburger = document.querySelector('.hamburger');
        
        if (window.innerWidth > 768) {
            navMenu.classList.remove('active');
            hamburger.classList.remove('active');
        }
    }, 250);
});