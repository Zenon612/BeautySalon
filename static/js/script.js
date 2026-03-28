/**
 * Скрипт салона красоты "Лайм"
 * Обрабатывает взаимодействие с пользователем и интеграцию с бэкендом
 */

// API Base URL - используется относительный путь для работы через nginx
const API_BASE_URL = '/api/v1';

// ============================================
// Loading Screen
// ============================================
window.addEventListener('load', () => {
    setTimeout(() => {
        document.getElementById('loader').classList.add('hidden');
    }, 1500);
    
    // Проверка авторизации при загрузке
    checkAuth();
});

// ============================================
// Scroll Progress Bar
// ============================================
window.addEventListener('scroll', () => {
    const scrollProgress = document.getElementById('scrollProgress');
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const scrollPercent = (scrollTop / docHeight) * 100;
    scrollProgress.style.width = scrollPercent + '%';
});

// ============================================
// Particles
// ============================================
function createParticles() {
    const container = document.getElementById('particles');
    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 15 + 's';
        particle.style.animationDuration = (Math.random() * 10 + 10) + 's';
        container.appendChild(particle);
    }
}
createParticles();

// ============================================
// Header Scroll Effect
// ============================================
window.addEventListener('scroll', () => {
    const header = document.getElementById('header');
    const backToTop = document.getElementById('backToTop');

    if (window.scrollY > 100) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }

    if (window.scrollY > 500) {
        backToTop.classList.add('visible');
    } else {
        backToTop.classList.remove('visible');
    }
});

// ============================================
// Back to Top
// ============================================
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ============================================
// Modal Functions
// ============================================
function openModal(type) {
    const modal = document.getElementById(type + 'Modal');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal(type) {
    const modal = document.getElementById(type + 'Modal');
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
}

function switchModal(from, to) {
    closeModal(from);
    setTimeout(() => openModal(to), 300);
}

// Close modal on outside click
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
}

// ============================================
// Authentication Functions
// ============================================

/**
 * Проверка авторизации пользователя
 */
function checkAuth() {
    const token = localStorage.getItem('access_token');
    const userName = localStorage.getItem('user_name');
    
    if (token) {
        showLoggedInState(userName);
    } else {
        showLoggedOutState();
    }
}

/**
 * Отображение состояния авторизованного пользователя
 */
function showLoggedInState(name) {
    document.getElementById('loginBtn').style.display = 'none';
    document.getElementById('registerBtn').style.display = 'none';
    document.getElementById('logoutBtn').style.display = 'block';
    
    if (name) {
        const userNameEl = document.getElementById('userName');
        userNameEl.textContent = name;
        userNameEl.style.display = 'block';
    }
}

/**
 * Отображение состояния неавторизованного пользователя
 */
function showLoggedOutState() {
    document.getElementById('loginBtn').style.display = 'block';
    document.getElementById('registerBtn').style.display = 'block';
    document.getElementById('logoutBtn').style.display = 'none';
    document.getElementById('userName').style.display = 'none';
}

/**
 * Обработка входа пользователя
 */
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        if (response.ok) {
            const data = await response.json();
            
            // Сохранение токенов
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);
            localStorage.setItem('token_type', data.token_type);
            
            // Извлечение имени пользователя из email
            const userName = email.split('@')[0];
            localStorage.setItem('user_name', userName);
            
            alert('Успешный вход!');
            closeModal('login');
            checkAuth();
        } else {
            const error = await response.json();
            alert('Ошибка: ' + (error.detail || 'Неверный email или пароль'));
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('Ошибка подключения к серверу');
    }
}

/**
 * Обработка регистрации пользователя
 */
async function handleRegister(event) {
    event.preventDefault();
    
    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const phone = document.getElementById('registerPhone').value;
    const password = document.getElementById('registerPassword').value;

    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email,
                password,
                full_name: name,
                phone
            }),
        });

        if (response.ok) {
            alert('Регистрация успешна! Теперь вы можете войти.');
            closeModal('register');
            setTimeout(() => openModal('login'), 500);
        } else {
            const error = await response.json();
            alert('Ошибка: ' + (error.detail || 'Не удалось зарегистрироваться'));
        }
    } catch (error) {
        console.error('Register error:', error);
        alert('Ошибка подключения к серверу. Убедитесь, что бэкенд запущен.');
    }
}

/**
 * Обработка выхода пользователя
 */
function handleLogout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('token_type');
    localStorage.removeItem('user_name');
    
    alert('Вы успешно вышли из системы');
    checkAuth();
}

// ============================================
// Mobile Menu Toggle
// ============================================
function toggleMobileMenu() {
    const navLinks = document.querySelector('.nav-links');
    const navButtons = document.querySelector('.nav-buttons');

    if (navLinks.style.display === 'flex') {
        navLinks.style.display = 'none';
        navButtons.style.display = 'none';
    } else {
        navLinks.style.display = 'flex';
        navLinks.style.flexDirection = 'column';
        navLinks.style.position = 'absolute';
        navLinks.style.top = '100%';
        navLinks.style.left = '0';
        navLinks.style.right = '0';
        navLinks.style.background = 'rgba(255, 248, 240, 0.98)';
        navLinks.style.padding = '20px';
        navLinks.style.boxShadow = 'var(--shadow)';

        navButtons.style.display = 'flex';
        navButtons.style.flexDirection = 'column';
        navButtons.style.position = 'absolute';
        navButtons.style.top = '100%';
        navButtons.style.right = '0';
        navButtons.style.background = 'rgba(255, 248, 240, 0.98)';
        navButtons.style.padding = '20px';
        navButtons.style.boxShadow = 'var(--shadow)';
    }
}

// ============================================
// Smooth Scroll for Navigation
// ============================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
            // Close mobile menu if open
            document.querySelector('.nav-links').style.display = '';
            document.querySelector('.nav-buttons').style.display = '';
        }
    });
});

// ============================================
// Animation on Scroll
// ============================================
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate');

            // Add staggered animation for grid items
            if (entry.target.classList.contains('service-card') ||
                entry.target.classList.contains('portfolio-item')) {
                const index = Array.from(entry.target.parentNode.children).indexOf(entry.target);
                entry.target.style.animationDelay = (index * 0.2) + 's';
            }
        }
    });
}, observerOptions);

document.querySelectorAll('.service-card, .portfolio-item').forEach(el => {
    observer.observe(el);
});

// ============================================
// Phone Number Formatting
// ============================================
document.getElementById('registerPhone').addEventListener('input', function(e) {
    let value = e.target.value.replace(/\D/g, '');
    if (value.length > 0) {
        if (value.length > 1) {
            value = '+7 (' + value.substring(1, 4);
        }
        if (value.length > 6) {
            value = value.substring(0, 7) + ') ' + value.substring(7, 10);
        }
        if (value.length > 11) {
            value = value.substring(0, 12) + '-' + value.substring(12, 14);
        }
        if (value.length > 14) {
            value = value.substring(0, 15) + '-' + value.substring(15, 17);
        }
    }
    e.target.value = value;
});

// ============================================
// Service Cards Hover Effect
// ============================================
document.querySelectorAll('.service-card').forEach(card => {
    card.addEventListener('mouseenter', function() {
        this.querySelector('.service-image').style.transform = 'scale(1.1)';
    });

    card.addEventListener('mouseleave', function() {
        this.querySelector('.service-image').style.transform = 'scale(1)';
    });
});
