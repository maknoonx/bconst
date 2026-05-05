// Preloader
window.addEventListener('load', function() {
    const preloader = document.getElementById('preloader');
    
    // Minimum loading time of 1 second for better UX
    setTimeout(() => {
        preloader.classList.add('fade-out');
        
        // Remove preloader from DOM after fade out
        setTimeout(() => {
            preloader.style.display = 'none';
        }, 500);
    }, 1000);
});

// Fallback: Hide preloader after 3 seconds even if page isn't fully loaded
setTimeout(() => {
    const preloader = document.getElementById('preloader');
    if (preloader && !preloader.classList.contains('fade-out')) {
        preloader.classList.add('fade-out');
        setTimeout(() => {
            preloader.style.display = 'none';
        }, 500);
    }
}, 3000);