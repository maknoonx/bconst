// Gallery images array
const galleryImages = [
    'https://ext.same-assets.com/2977916181/4234824831.png',
    'https://ext.same-assets.com/2977916181/1160599726.png',
    'https://ext.same-assets.com/2977916181/351238446.png',
    'https://ext.same-assets.com/2977916181/2266948137.jpeg',
    'https://ext.same-assets.com/2977916181/476409975.jpeg',
    'https://ext.same-assets.com/2977916181/1656347559.png',
    'https://ext.same-assets.com/2977916181/3823570733.png',
    'https://ext.same-assets.com/2977916181/3045019044.png'
];

let currentImageIndex = 0;

// Change main image
function changeMainImage(direction) {
    currentImageIndex += direction;
    
    if (currentImageIndex < 0) {
        currentImageIndex = galleryImages.length - 1;
    } else if (currentImageIndex >= galleryImages.length) {
        currentImageIndex = 0;
    }
    
    updateMainImage();
}

// Select image by index
function selectImage(index) {
    currentImageIndex = index;
    updateMainImage();
}

// Update main image display
function updateMainImage() {
    const mainImage = document.getElementById('mainImage');
    const currentImageNumber = document.getElementById('currentImageNumber');
    const thumbnails = document.querySelectorAll('.thumbnail-item');
    
    // Update main image
    mainImage.src = galleryImages[currentImageIndex];
    
    // Update counter
    currentImageNumber.textContent = currentImageIndex + 1;
    
    // Update active thumbnail
    thumbnails.forEach((thumb, index) => {
        if (index === currentImageIndex) {
            thumb.classList.add('active');
        } else {
            thumb.classList.remove('active');
        }
    });
}

// Initialize gallery on page load
document.addEventListener('DOMContentLoaded', function() {
    const totalImages = document.getElementById('totalImages');
    if (totalImages) {
        totalImages.textContent = galleryImages.length;
    }
    
    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowLeft') {
            changeMainImage(1);
        } else if (e.key === 'ArrowRight') {
            changeMainImage(-1);
        }
    });
    
    // Auto-play gallery (optional)
    // setInterval(() => {
    //     changeMainImage(1);
    // }, 5000);
});

// Share functionality
document.querySelectorAll('.share-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const platform = this.classList[1]; // whatsapp, twitter, facebook, linkedin
        const url = window.location.href;
        const title = document.querySelector('.project-title').textContent;
        
        let shareUrl = '';
        
        switch(platform) {
            case 'whatsapp':
                shareUrl = `https://api.whatsapp.com/send?text=${encodeURIComponent(title + ' - ' + url)}`;
                break;
            case 'twitter':
                shareUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`;
                break;
            case 'facebook':
                shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
                break;
            case 'linkedin':
                shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`;
                break;
        }
        
        if (shareUrl) {
            window.open(shareUrl, '_blank', 'width=600,height=400');
        }
    });
});

// Smooth scroll for internal links
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

// Animate elements on scroll
function animateOnScroll() {
    const elements = document.querySelectorAll('.feature-box, .related-card, .thumbnail-item');
    
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

// Mobile menu toggle (if not already in main script)
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

if (hamburger) {
    hamburger.addEventListener('click', function() {
        navMenu.classList.toggle('active');
        this.classList.toggle('active');
    });
}

// Close menu when clicking on a link
document.querySelectorAll('.nav-menu a').forEach(link => {
    link.addEventListener('click', function() {
        if (window.innerWidth <= 768) {
            navMenu.classList.remove('active');
            hamburger.classList.remove('active');
        }
    });
});

// WhatsApp button
function openWhatsApp() {
    window.open('https://api.whatsapp.com/send/?phone=966593394747&text&app_absent=0', '_blank');
}

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

// Image lazy loading
document.querySelectorAll('img').forEach(img => {
    img.addEventListener('load', function() {
        this.style.opacity = '1';
    });
    
    if (!img.complete) {
        img.style.opacity = '0';
        img.style.transition = 'opacity 0.3s ease';
    }
});



