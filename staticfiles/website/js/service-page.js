// Gallery functionality
let currentGalleryIndex = 0;
let galleryItems = [];
let galleryDots = [];

// Initialize gallery when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeGallery();
    setupGalleryDots();
    startAutoSlide();
});

// Initialize gallery
function initializeGallery() {
    const galleryTrack = document.querySelector('.gallery-track');
    if (!galleryTrack) return;
    
    galleryItems = document.querySelectorAll('.gallery-item');
    if (galleryItems.length === 0) return;
    
    currentGalleryIndex = 0;
    updateGalleryPosition();
}

// Setup dots for gallery navigation
function setupGalleryDots() {
    const dotsContainer = document.querySelector('.gallery-dots');
    if (!dotsContainer || galleryItems.length === 0) return;
    
    dotsContainer.innerHTML = '';
    
    const visibleItems = getVisibleGalleryItems();
    const totalPages = Math.ceil(galleryItems.length / visibleItems);
    
    for (let i = 0; i < totalPages; i++) {
        const dot = document.createElement('div');
        dot.className = 'gallery-dot';
        if (i === 0) dot.classList.add('active');
        dot.addEventListener('click', () => goToGalleryPage(i));
        dotsContainer.appendChild(dot);
        galleryDots.push(dot);
    }
}

// Move gallery
function moveGallery(direction) {
    if (galleryItems.length === 0) return;
    
    const visibleItems = getVisibleGalleryItems();
    const maxIndex = galleryItems.length - visibleItems;
    
    currentGalleryIndex += direction * visibleItems;
    
    if (currentGalleryIndex < 0) {
        currentGalleryIndex = 0;
    } else if (currentGalleryIndex > maxIndex) {
        currentGalleryIndex = maxIndex;
    }
    
    updateGalleryPosition();
    updateGalleryDots();
}

// Go to specific gallery page
function goToGalleryPage(pageIndex) {
    const visibleItems = getVisibleGalleryItems();
    currentGalleryIndex = pageIndex * visibleItems;
    
    const maxIndex = galleryItems.length - visibleItems;
    if (currentGalleryIndex > maxIndex) {
        currentGalleryIndex = maxIndex;
    }
    
    updateGalleryPosition();
    updateGalleryDots();
}

// Update gallery position
function updateGalleryPosition() {
    const track = document.querySelector('.gallery-track');
    if (!track || galleryItems.length === 0) return;
    
    const itemWidth = galleryItems[0].offsetWidth;
    const gap = 30;
    const offset = currentGalleryIndex * (itemWidth + gap);
    
    track.style.transform = `translateX(${offset}px)`;
}

// Update gallery dots
function updateGalleryDots() {
    if (galleryDots.length === 0) return;
    
    const visibleItems = getVisibleGalleryItems();
    const currentPage = Math.floor(currentGalleryIndex / visibleItems);
    
    galleryDots.forEach((dot, index) => {
        if (index === currentPage) {
            dot.classList.add('active');
        } else {
            dot.classList.remove('active');
        }
    });
}

// Get number of visible gallery items based on screen width
function getVisibleGalleryItems() {
    const width = window.innerWidth;
    if (width <= 480) return 1;
    if (width <= 768) return 1;
    if (width <= 1024) return 2;
    return 3;
}

// Auto slide gallery
let autoSlideInterval;

function startAutoSlide() {
    autoSlideInterval = setInterval(() => {
        const visibleItems = getVisibleGalleryItems();
        const maxIndex = galleryItems.length - visibleItems;
        
        currentGalleryIndex += visibleItems;
        
        if (currentGalleryIndex > maxIndex) {
            currentGalleryIndex = 0;
        }
        
        updateGalleryPosition();
        updateGalleryDots();
    }, 5000); // Auto slide every 5 seconds
}

function stopAutoSlide() {
    if (autoSlideInterval) {
        clearInterval(autoSlideInterval);
    }
}

// Stop auto slide when user interacts with gallery
document.addEventListener('DOMContentLoaded', function() {
    const galleryPrev = document.querySelector('.gallery-prev');
    const galleryNext = document.querySelector('.gallery-next');
    
    if (galleryPrev) {
        galleryPrev.addEventListener('click', () => {
            stopAutoSlide();
            setTimeout(startAutoSlide, 10000); // Restart after 10 seconds
        });
    }
    
    if (galleryNext) {
        galleryNext.addEventListener('click', () => {
            stopAutoSlide();
            setTimeout(startAutoSlide, 10000); // Restart after 10 seconds
        });
    }
});

// Handle window resize
let resizeTimer;
window.addEventListener('resize', function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function() {
        currentGalleryIndex = 0;
        updateGalleryPosition();
        setupGalleryDots();
    }, 250);
});

// Smooth scroll for CTA button
document.addEventListener('DOMContentLoaded', function() {
    const ctaButtons = document.querySelectorAll('.btn-primary, .btn-large');
    
    ctaButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href && href.includes('#contact')) {
                e.preventDefault();
                
                // If we're on the home page, scroll to contact
                if (window.location.pathname === '/' || window.location.pathname === '/home/') {
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
                } else {
                    // If we're on another page, navigate to home with contact hash
                    window.location.href = href;
                }
            }
        });
    });
});

// Animate elements on scroll
function animateOnScroll() {
    const elements = document.querySelectorAll('.feature-item, .process-step, .gallery-item');
    
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
    animateOnScroll();
});

// Touch support for gallery slider
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('DOMContentLoaded', function() {
    const gallerySlider = document.querySelector('.gallery-slider');
    
    if (gallerySlider) {
        gallerySlider.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        });
        
        gallerySlider.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            handleGallerySwipe();
        });
    }
});

function handleGallerySwipe() {
    const swipeThreshold = 50;
    const diff = touchStartX - touchEndX;
    
    if (Math.abs(diff) > swipeThreshold) {
        if (diff > 0) {
            // Swipe left - move forward
            moveGallery(1);
        } else {
            // Swipe right - move backward
            moveGallery(-1);
        }
        stopAutoSlide();
        setTimeout(startAutoSlide, 10000);
    }
}

// Lazy load images
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('.gallery-item img');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.style.opacity = '1';
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => {
        img.style.opacity = '0';
        img.style.transition = 'opacity 0.5s ease';
        imageObserver.observe(img);
        
        img.addEventListener('load', function() {
            this.style.opacity = '1';
        });
    });
});