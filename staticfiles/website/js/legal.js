// Legal Pages JavaScript

// Smooth scroll for sidebar navigation
document.addEventListener('DOMContentLoaded', function() {
    const sidebarLinks = document.querySelectorAll('.sidebar-nav a');
    const sections = document.querySelectorAll('.legal-section');
    
    // Update active link on scroll
    function updateActiveLink() {
        let current = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (window.pageYOffset >= (sectionTop - 150)) {
                current = section.getAttribute('id');
            }
        });
        
        sidebarLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {
                link.classList.add('active');
            }
        });
    }
    
    // Smooth scroll to section
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const headerOffset = 120;
                const elementPosition = targetSection.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Update active link on scroll
    window.addEventListener('scroll', updateActiveLink);
    
    // Initial call to set active link
    updateActiveLink();
});

// Print page functionality
function printPage() {
    window.print();
}

// Copy link to clipboard
function copyLink() {
    const url = window.location.href;
    navigator.clipboard.writeText(url).then(function() {
        alert('تم نسخ الرابط بنجاح!');
    }, function() {
        alert('فشل نسخ الرابط');
    });
}

// Scroll to top button
const scrollTopBtn = document.createElement('button');
scrollTopBtn.className = 'scroll-top-btn';
scrollTopBtn.innerHTML = '↑';
scrollTopBtn.style.cssText = `
    position: fixed;
    bottom: 100px;
    right: 20px;
    width: 50px;
    height: 50px;
    background: #6699cc;
    color: white;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    display: none;
    z-index: 999;
    font-size: 1.5rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102, 153, 204, 0.3);
`;

document.body.appendChild(scrollTopBtn);

window.addEventListener('scroll', function() {
    if (window.pageYOffset > 300) {
        scrollTopBtn.style.display = 'block';
    } else {
        scrollTopBtn.style.display = 'none';
    }
});

scrollTopBtn.addEventListener('click', function() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
});

scrollTopBtn.addEventListener('mouseenter', function() {
    this.style.background = '#3b82f6';
    this.style.transform = 'scale(1.1)';
});

scrollTopBtn.addEventListener('mouseleave', function() {
    this.style.background = '#6699cc';
    this.style.transform = 'scale(1)';
});

// Highlight text on double click (for easy copying)
document.addEventListener('dblclick', function(e) {
    if (e.target.tagName === 'P' || e.target.tagName === 'LI') {
        const selection = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(e.target);
        selection.removeAllRanges();
        selection.addRange(range);
    }
});

// Add reading progress bar
const progressBar = document.createElement('div');
progressBar.className = 'reading-progress';
progressBar.style.cssText = `
    position: fixed;
    top: 90px;
    left: 0;
    width: 0%;
    height: 4px;
    background: linear-gradient(90deg, #6699cc, #3b82f6);
    z-index: 1001;
    transition: width 0.1s ease;
`;

document.body.appendChild(progressBar);

window.addEventListener('scroll', function() {
    const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrolled = (winScroll / height) * 100;
    progressBar.style.width = scrolled + '%';
});

// Animate sections on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

document.querySelectorAll('.legal-section').forEach(section => {
    section.style.opacity = '0';
    section.style.transform = 'translateY(20px)';
    section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(section);
});

// Add tooltips to important terms
const importantTerms = {
    'الملكية الفكرية': 'حقوق المبدع في حماية أعماله الإبداعية',
    'التحكيم': 'وسيلة بديلة لحل النزاعات خارج المحاكم',
    'القوة القاهرة': 'ظروف استثنائية خارجة عن إرادة الأطراف',
    'الضمان': 'التزام بإصلاح العيوب خلال فترة محددة'
};

// Lazy load images (if any are added in the future)
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver(function(entries, observer) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });

    document.querySelectorAll('img.lazy').forEach(img => {
        imageObserver.observe(img);
    });
}

// Print styles
window.addEventListener('beforeprint', function() {
    document.querySelector('.navbar').style.display = 'none';
    document.querySelector('.footer').style.display = 'none';
    document.querySelector('.whatsapp-btn').style.display = 'none';
    document.querySelector('.legal-sidebar').style.display = 'none';
});

window.addEventListener('afterprint', function() {
    document.querySelector('.navbar').style.display = 'block';
    document.querySelector('.footer').style.display = 'block';
    document.querySelector('.whatsapp-btn').style.display = 'flex';
    document.querySelector('.legal-sidebar').style.display = 'block';
});

// Track reading time
let startTime = Date.now();
let totalReadingTime = 0;

window.addEventListener('beforeunload', function() {
    totalReadingTime = Math.floor((Date.now() - startTime) / 1000);
    console.log('وقت القراءة: ' + totalReadingTime + ' ثانية');
});

// Add copy button to code blocks (if any)
document.querySelectorAll('pre code').forEach(block => {
    const button = document.createElement('button');
    button.className = 'copy-code-btn';
    button.textContent = 'نسخ';
    button.style.cssText = `
        position: absolute;
        top: 10px;
        left: 10px;
        background: #6699cc;
        color: white;
        border: none;
        padding: 5px 15px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 0.9rem;
    `;
    
    const pre = block.parentElement;
    pre.style.position = 'relative';
    pre.appendChild(button);
    
    button.addEventListener('click', function() {
        navigator.clipboard.writeText(block.textContent);
        button.textContent = 'تم النسخ!';
        setTimeout(() => {
            button.textContent = 'نسخ';
        }, 2000);
    });
});

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + P to print
    if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
        e.preventDefault();
        window.print();
    }
    
    // Ctrl/Cmd + F to focus search (if added)
    if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        // Custom search functionality can be added here
    }
});

// Smooth scroll for all anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                const headerOffset = 120;
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        }
    });
});

console.log('Legal pages scripts loaded successfully');