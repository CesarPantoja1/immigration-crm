// MigraFácil Landing Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initSmoothScroll();
    initScrollAnimations();
    initMobileMenu();
    initFormValidation();
    initHeaderScroll();
    initStatCounters();
});

/**
 * Smooth scroll for anchor links
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                const headerOffset = 80;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * Scroll-triggered animations using Intersection Observer
 */
function initScrollAnimations() {
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                entry.target.style.opacity = '1';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe sections and cards
    const animatedElements = document.querySelectorAll(
        'section > div > div, .group, .grid > div'
    );
    
    animatedElements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.animationDelay = `${index * 0.1}s`;
        observer.observe(el);
    });
}

/**
 * Mobile menu toggle
 */
function initMobileMenu() {
    // Create mobile menu button if it doesn't exist
    const header = document.querySelector('header');
    const nav = header.querySelector('nav');
    
    // Create hamburger button
    const menuButton = document.createElement('button');
    menuButton.className = 'md:hidden p-2 text-gray-600 hover:text-primary-600 focus:outline-none';
    menuButton.innerHTML = `
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
        </svg>
    `;
    menuButton.setAttribute('aria-label', 'Toggle menu');
    
    // Insert before CTA buttons on mobile
    const ctaDiv = header.querySelector('.flex.items-center.space-x-4');
    ctaDiv.insertBefore(menuButton, ctaDiv.firstChild);
    
    // Create mobile menu
    const mobileMenu = document.createElement('div');
    mobileMenu.className = 'mobile-menu-container hidden fixed inset-0 z-50 md:hidden';
    mobileMenu.innerHTML = `
        <div class="absolute inset-0 bg-black/50" id="menu-overlay"></div>
        <div class="mobile-menu absolute right-0 top-0 h-full w-64 bg-white shadow-xl p-6">
            <button class="absolute top-4 right-4 p-2 text-gray-600 hover:text-primary-600" id="close-menu">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
            <nav class="mt-12 space-y-4">
                <a href="#servicios" class="block py-2 text-gray-700 hover:text-primary-600 font-medium">Servicios</a>
                <a href="#como-funciona" class="block py-2 text-gray-700 hover:text-primary-600 font-medium">¿Cómo funciona?</a>
                <a href="#caracteristicas" class="block py-2 text-gray-700 hover:text-primary-600 font-medium">Características</a>
                <a href="#contacto" class="block py-2 text-gray-700 hover:text-primary-600 font-medium">Contacto</a>
                <hr class="my-4 border-gray-200">
                <a href="/login" class="block py-2 text-primary-600 font-medium">Iniciar Sesión</a>
                <a href="/registro" class="block py-3 px-4 bg-primary-600 text-white text-center font-semibold rounded-full mt-4">
                    Comenzar Ahora
                </a>
            </nav>
        </div>
    `;
    document.body.appendChild(mobileMenu);
    
    // Toggle menu
    menuButton.addEventListener('click', () => {
        mobileMenu.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    });
    
    // Close menu handlers
    const closeMenu = () => {
        mobileMenu.classList.add('hidden');
        document.body.style.overflow = '';
    };
    
    mobileMenu.querySelector('#close-menu').addEventListener('click', closeMenu);
    mobileMenu.querySelector('#menu-overlay').addEventListener('click', closeMenu);
    mobileMenu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', closeMenu);
    });
}

/**
 * Form validation and submission
 */
function initFormValidation() {
    const contactForm = document.querySelector('form');
    
    if (contactForm) {
        contactForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            
            // Basic validation
            const inputs = this.querySelectorAll('input, textarea');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.classList.add('border-red-500');
                    input.classList.remove('border-gray-200');
                } else {
                    input.classList.remove('border-red-500');
                    input.classList.add('border-gray-200');
                }
            });
            
            // Email validation
            const emailInput = this.querySelector('input[type="email"]');
            if (emailInput && !isValidEmail(emailInput.value)) {
                isValid = false;
                emailInput.classList.add('border-red-500');
            }
            
            if (!isValid) {
                showNotification('Por favor, completa todos los campos correctamente.', 'error');
                return;
            }
            
            // Show loading state
            submitBtn.disabled = true;
            submitBtn.innerHTML = `
                <span class="inline-flex items-center">
                    <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Enviando...
                </span>
            `;
            
            // Simulate form submission (replace with actual API call)
            try {
                await new Promise(resolve => setTimeout(resolve, 1500));
                
                showNotification('¡Mensaje enviado con éxito! Te contactaremos pronto.', 'success');
                this.reset();
            } catch (error) {
                showNotification('Hubo un error al enviar el mensaje. Intenta de nuevo.', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }
    
    // Hero email form
    const heroForm = document.querySelector('section input[type="email"]');
    if (heroForm) {
        const heroButton = heroForm.parentElement.querySelector('button');
        heroButton.addEventListener('click', function(e) {
            e.preventDefault();
            const email = heroForm.value;
            
            if (!email || !isValidEmail(email)) {
                showNotification('Por favor, ingresa un correo electrónico válido.', 'error');
                heroForm.classList.add('border-red-500');
                return;
            }
            
            heroForm.classList.remove('border-red-500');
            // Redirect to registration with email
            window.location.href = `/registro?email=${encodeURIComponent(email)}`;
        });
    }
}

/**
 * Email validation helper
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Show notification toast
 */
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existing = document.querySelector('.notification-toast');
    if (existing) existing.remove();
    
    const notification = document.createElement('div');
    notification.className = `notification-toast fixed bottom-4 right-4 px-6 py-4 rounded-xl shadow-xl z-50 flex items-center space-x-3 transform translate-y-0 transition-all duration-300`;
    
    const colors = {
        success: 'bg-green-500 text-white',
        error: 'bg-red-500 text-white',
        info: 'bg-primary-500 text-white'
    };
    
    const icons = {
        success: `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>`,
        error: `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>`,
        info: `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`
    };
    
    notification.classList.add(...colors[type].split(' '));
    notification.innerHTML = `
        ${icons[type]}
        <span class="font-medium">${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.transform = 'translateY(100px)';
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

/**
 * Header scroll effect
 */
function initHeaderScroll() {
    const header = document.querySelector('header');
    let lastScroll = 0;
    
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > 50) {
            header.classList.add('shadow-md');
            header.style.backgroundColor = 'rgba(255, 255, 255, 0.98)';
        } else {
            header.classList.remove('shadow-md');
            header.style.backgroundColor = '';
        }
        
        // Hide/show header on scroll
        if (currentScroll > lastScroll && currentScroll > 200) {
            header.style.transform = 'translateY(-100%)';
        } else {
            header.style.transform = 'translateY(0)';
        }
        
        header.style.transition = 'transform 0.3s ease, background-color 0.3s ease, box-shadow 0.3s ease';
        lastScroll = currentScroll;
    });
}

/**
 * Animated stat counters
 */
function initStatCounters() {
    const stats = document.querySelectorAll('.text-4xl.font-bold, .text-5xl.font-bold');
    
    const observerOptions = {
        threshold: 0.5
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateValue(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    stats.forEach(stat => observer.observe(stat));
}

/**
 * Animate numeric values
 */
function animateValue(element) {
    const text = element.textContent;
    const match = text.match(/(\d+)/);
    
    if (match) {
        const endValue = parseInt(match[1]);
        const suffix = text.replace(match[0], '');
        const duration = 2000;
        const startTime = performance.now();
        
        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const currentValue = Math.round(endValue * easeOutQuart);
            
            element.textContent = currentValue + suffix;
            
            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }
        
        requestAnimationFrame(update);
    }
}
