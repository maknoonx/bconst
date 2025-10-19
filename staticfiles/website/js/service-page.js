// Gallery functionality
let currentGalleryIndex = 0;
let galleryItems = [];
let galleryDots = [];
let autoSlideInterval;
let galleryResizeTimer;
let touchStartX = 0;
let touchEndX = 0;

// Initialize gallery when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeGallery();
    setupGalleryDots();
    setupGalleryButtons();
    setupTouchSupport();
    startAutoSlide();
    setupAnimations();
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

// Setup gallery navigation buttons
function setupGalleryButtons() {
    const galleryPrev = document.querySelector('.gallery-prev');
    const galleryNext = document.querySelector('.gallery-next');
    
    if (galleryPrev) {
        galleryPrev.addEventListener('click', () => {
            moveGallery(1);
            stopAutoSlide();
            setTimeout(startAutoSlide, 10000);
        });
    }
    
    if (galleryNext) {
        galleryNext.addEventListener('click', () => {
            moveGallery(-1);
            stopAutoSlide();
            setTimeout(startAutoSlide, 10000);
        });
    }
}

// Setup dots for gallery navigation
function setupGalleryDots() {
    const dotsContainer = document.querySelector('.gallery-dots');
    if (!dotsContainer || galleryItems.length === 0) return;
    
    dotsContainer.innerHTML = '';
    galleryDots = [];
    
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
    
    // Simply move by 1 item at a time
    currentGalleryIndex -= direction;
    
    if (currentGalleryIndex < 0) {
        currentGalleryIndex = 0;
    } else if (currentGalleryIndex > maxIndex) {
        currentGalleryIndex = maxIndex;
    }
    
    console.log('Moving gallery:', {
        direction,
        currentIndex: currentGalleryIndex,
        maxIndex,
        totalItems: galleryItems.length,
        visibleItems
    });
    
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
    
    track.style.transform = `translateX(-${offset}px)`;
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
    if (width <= 768) return 1;
    if (width <= 1024) return 2;
    return 3;
}

// Auto slide gallery
function startAutoSlide() {
    stopAutoSlide();
    autoSlideInterval = setInterval(() => {
        if (galleryItems.length === 0) return;
        
        const visibleItems = getVisibleGalleryItems();
        const maxIndex = galleryItems.length - visibleItems;
        
        currentGalleryIndex++;
        
        if (currentGalleryIndex > maxIndex) {
            currentGalleryIndex = 0;
        }
        
        updateGalleryPosition();
        updateGalleryDots();
    }, 5000);
}

function stopAutoSlide() {
    if (autoSlideInterval) {
        clearInterval(autoSlideInterval);
    }
}

// Touch support for gallery slider
function setupTouchSupport() {
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
}

function handleGallerySwipe() {
    const swipeThreshold = 50;
    const diff = touchStartX - touchEndX;
    
    if (Math.abs(diff) > swipeThreshold) {
        if (diff > 0) {
            moveGallery(1);
        } else {
            moveGallery(-1);
        }
        stopAutoSlide();
        setTimeout(startAutoSlide, 10000);
    }
}

// Handle window resize
window.addEventListener('resize', function() {
    clearTimeout(galleryResizeTimer);
    galleryResizeTimer = setTimeout(function() {
        if (galleryItems.length > 0) {
            const visibleItems = getVisibleGalleryItems();
            const maxIndex = galleryItems.length - visibleItems;
            
            if (currentGalleryIndex > maxIndex) {
                currentGalleryIndex = maxIndex;
            }
            
            updateGalleryPosition();
            setupGalleryDots();
        }
    }, 250);
});

// Setup animations
function setupAnimations() {
    // Smooth scroll for CTA button
    const ctaButtons = document.querySelectorAll('.btn-primary, .btn-large');
    
    ctaButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href && href.includes('#contact')) {
                e.preventDefault();
                
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
                    window.location.href = href;
                }
            }
        });
    });
    
    // Animate elements on scroll
    const elements = document.querySelectorAll('.feature-item, .process-step, .gallery-item');
    
    if (elements.length > 0) {
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
    
    // Lazy load images
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
}