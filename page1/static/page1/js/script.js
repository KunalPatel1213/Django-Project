// ===============================
// MOBILE MENU TOGGLE FUNCTIONALITY
// ===============================

/**
 * Toggles the mobile navigation menu
 * Adds/removes 'active' class to show/hide menu
 */

        document.addEventListener('DOMContentLoaded', function() {
            const progressBar = document.getElementById('progressBar');
            const timer = document.getElementById('timer');
            const completionMessage = document.getElementById('completionMessage');
            const images = document.querySelectorAll('.image-box img');
            const loaderContainer = document.querySelector('.loader-container');
            const mainContent = document.getElementById('mainContent');

            let currentImageIndex = 0;
            let progress = 0;
            const totalTime = 3000; // 3 seconds
            const intervalTime = 30; // Update every 30ms
            const steps = totalTime / intervalTime;
            const progressIncrement = 100 / steps;

            // Function to switch images
            function switchImage() {
                images[currentImageIndex].classList.remove('active');
                currentImageIndex = (currentImageIndex + 1) % images.length;
                images[currentImageIndex].classList.add('active');
            }
            
            // Start the loader
            const loaderInterval = setInterval(() => {
                progress += progressIncrement;
                
                // Update progress bar
                progressBar.style.width = `${progress}%`;
                
                // Update timer text
                timer.textContent = `Loading... ${Math.min(100, Math.round(progress))}%`;
                
                // Switch image every 20% progress
                if (Math.round(progress) % 20 === 0) {
                    switchImage();
                }
                
                // Check if loading is complete
                if (progress >= 100) {
                    clearInterval(loaderInterval);
                    timer.style.display = 'none';
                    completionMessage.style.display = 'block';
                    
                    // Redirect or show content after completion
                    setTimeout(() => {
                        loaderContainer.style.display = 'none';
                        mainContent.style.display = 'block';
                        document.body.classList.remove('loader-active');
                        mainContent.classList.add('visible'); // Add this for fade-in effect
                    }, 1000);
                }
            }, intervalTime);
        });

// ===============================
// LANGUAGE TOGGLE FUNCTIONALITY
// ===============================

let currentLanguage = 'en';

/**
 * Toggles between English and Hindi languages
 * Updates button text and all translatable content
 */
function toggleLanguage() {
    const languageBtn = document.getElementById('language-btn');
    
    if (currentLanguage === 'en') {
        currentLanguage = 'hi';
        languageBtn.textContent = 'English';
        updateTextContent('hi');
    } else {
        currentLanguage = 'en';
        languageBtn.textContent = 'हिंदी';
        updateTextContent('en');
    }
}

/**
 * Updates all text content based on selected language
 * @param {string} language - The language code ('en' or 'hi')
 */
function updateTextContent(language) {
    // Select all elements with language data attributes
    const elements = document.querySelectorAll('[data-en], [data-hi]');
    
    elements.forEach(element => {
        if (element.hasAttribute(`data-${language}`)) {
            const newText = element.getAttribute(`data-${language}`);
            
            // Handle HTML content for elements with line breaks
            if (newText.includes('<br>')) {
                element.innerHTML = newText;
            } else {
                element.textContent = newText;
            }
        }
    });
}

// ===============================
// CAROUSEL FUNCTIONALITY
// ===============================

document.addEventListener('DOMContentLoaded', function() {
    // Carousel DOM elements
    const carouselTrack = document.querySelector('.carousel-track');
    const slides = document.querySelectorAll('.carousel-slide');
    const stepIndicators = document.querySelectorAll('.step');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const playPauseBtn = document.getElementById('play-pause-btn');
    const playIcon = document.getElementById('play-icon');
    const pauseIcon = document.getElementById('pause-icon');
    
    // Carousel state variables
    let currentSlide = 0;
    let autoPlayInterval;
    let isPlaying = true;
    
    /**
     * Initializes the carousel
     * Sets up initial slide and starts autoplay
     */
    function initCarousel() {
        updateCarousel();
        startAutoPlay();
    }
    
    /**
     * Updates carousel display to show current slide
     * Manages active classes for slides and indicators
     */
    function updateCarousel() {
        // Remove active class from all slides
        slides.forEach(slide => {
            slide.classList.remove('active');
        });
        
        // Add active class to current slide
        slides[currentSlide].classList.add('active');
        
        // Update step indicators
        stepIndicators.forEach((indicator, index) => {
            if (index === currentSlide) {
                indicator.classList.add('active');
            } else {
                indicator.classList.remove('active');
            }
        });
    }
    
    /**
     * Advances to the next slide
     * Wraps around to first slide if at the end
     */
    function nextSlide() {
        currentSlide = (currentSlide + 1) % slides.length;
        updateCarousel();
    }
    
    /**
     * Goes back to the previous slide
     * Wraps around to last slide if at the beginning
     */
    function prevSlide() {
        currentSlide = (currentSlide - 1 + slides.length) % slides.length;
        updateCarousel();
    }
    
    /**
     * Jumps to a specific slide
     * @param {number} index - The slide index to navigate to
     */
    function goToSlide(index) {
        currentSlide = index;
        updateCarousel();
    }
    
    /**
     * Starts automatic slideshow
     * Changes slide every 4 seconds
     */
    function startAutoPlay() {
        // Clear existing interval to prevent duplicates
        if (autoPlayInterval) {
            clearInterval(autoPlayInterval);
        }
        
        // Set new interval for autoplay
        autoPlayInterval = setInterval(() => {
            if (isPlaying) {
                nextSlide();
            }
        }, 4000); // 4 second interval
        
        // Update play/pause button icon
        playIcon.style.display = 'none';
        pauseIcon.style.display = 'block';
        isPlaying = true;
    }
    
    /**
     * Pauses the automatic slideshow
     */
    function pauseAutoPlay() {
        if (autoPlayInterval) {
            clearInterval(autoPlayInterval);
        }
        
        // Update play/pause button icon
        playIcon.style.display = 'block';
        pauseIcon.style.display = 'none';
        isPlaying = false;
    }
    
    /**
     * Toggles between play and pause states
     */
    function togglePlayPause() {
        if (isPlaying) {
            pauseAutoPlay();
        } else {
            startAutoPlay();
        }
    }
    
    // ===============================
    // CAROUSEL EVENT LISTENERS
    // ===============================
    
    // Previous button click handler
    prevBtn.addEventListener('click', function() {
        prevSlide();
        // If paused, keep it paused after manual navigation
        if (!isPlaying) {
            pauseAutoPlay();
        }
    });
    
    // Next button click handler
    nextBtn.addEventListener('click', function() {
        nextSlide();
        // If paused, keep it paused after manual navigation
        if (!isPlaying) {
            pauseAutoPlay();
        }
    });
    
    // Play/pause button click handler
    playPauseBtn.addEventListener('click', togglePlayPause);
    
    // Step indicator click handlers
    stepIndicators.forEach((indicator, index) => {
        indicator.addEventListener('click', function() {
            goToSlide(index);
            // If paused, keep it paused after manual navigation
            if (!isPlaying) {
                pauseAutoPlay();
            }
        });
    });
    
    // Pause on hover for better user experience
    carouselTrack.addEventListener('mouseenter', function() {
        if (isPlaying) {
            pauseAutoPlay();
        }
    });
    
    // Resume autoplay when mouse leaves (if was playing)
    carouselTrack.addEventListener('mouseleave', function() {
        if (!isPlaying) {
            startAutoPlay();
        }
    });
    
    // Initialize the carousel when DOM is fully loaded
    initCarousel();
});

// ===============================
// MODAL DIALOG FUNCTIONALITY
// ===============================

// Get modal and control elements
const modal = document.getElementById("infoModal");
const btn = document.getElementById("knowMoreBtn");
const span = document.getElementsByClassName("close")[0];

/**
 * Opens the modal dialog
 */
btn.onclick = function() {
    modal.style.display = "block";
}

/**
 * Closes the modal dialog when close button is clicked
 */
span.onclick = function() {
    modal.style.display = "none";
}

/**
 * Closes modal when clicking outside modal content
 */
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

/**
 * Closes modal with Escape key for accessibility
 */
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        modal.style.display = "none";
    }
});



// static/js/footer.js
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('.footer-links a').forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      alert("This link is currently in demo mode.");
    });
  });
});