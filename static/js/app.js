// backend/static/js/app.js

// ====== КОНФИГУРАЦИЯ ======
const API_URL = '/api';

// Хранение токенов
let accessToken = localStorage.getItem('access_token');
let refreshToken = localStorage.getItem('refresh_token');

// ====== НАВИГАЦИЯ ======

function showPage(pageId) {
    document.querySelectorAll('.page-section').forEach(section => {
        section.classList.remove('active');
    });

    document.getElementById(pageId).classList.add('active');

    document.querySelectorAll('.nav-links a').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.page === pageId) {
            link.classList.add('active');
        }
    });

    document.getElementById('navLinks').classList.remove('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function toggleMobileMenu() {
    document.getElementById('navLinks').classList.toggle('active');
}

// ====== МОДАЛЬНЫЕ ОКНА ======

function showModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}

// ====== АВТОРИЗАЦИЯ ======

async function register(event) {
    event.preventDefault();

    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const fullName = document.getElementById('registerFullName').value;
    const phone = document.getElementById('registerPhone').value;

    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email,
                password,
                full_name: fullName,
                phone
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Ошибка регистрации');
        }

        alert('✅ Регистрация успешна! Теперь войдите.');
        closeModal('registerModal');
        showModal('loginModal');
        document.getElementById('registerForm').reset();
    } catch (error) {
        alert(`❌ ${error.message}`);
    }
}

async function login(event) {
    event.preventDefault();

    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                username: email,
                password: password,
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Ошибка входа');
        }

        accessToken = data.access_token;
        refreshToken = data.refresh_token;
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);

        alert('✅ Вход успешен!');
        updateUIAfterLogin();
        closeModal('loginModal');
        document.getElementById('loginForm').reset();
    } catch (error) {
        alert(`❌ ${error.message}`);
    }
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    accessToken = null;
    refreshToken = null;
    updateUIAfterLogout();
    alert('Вы вышли из аккаунта');
}

function updateUIAfterLogin() {
    document.getElementById('authButtons').style.display = 'none';
    document.getElementById('logoutBtn').style.display = 'block';
}

function updateUIAfterLogout() {
    document.getElementById('authButtons').style.display = 'flex';
    document.getElementById('logoutBtn').style.display = 'none';
}

function checkAuth() {
    if (accessToken) {
        updateUIAfterLogin();
    } else {
        updateUIAfterLogout();
    }
}

// ====== API ЗАПРОСЫ ======

async function getServices() {
    try {
        const response = await fetch(`${API_URL}/services`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error('Ошибка получения услуг');
        }

        return data.items;
    } catch (error) {
        console.error('Error:', error);
        return [];
    }
}

async function getPortfolio(category = null) {
    try {
        let url = `${API_URL}/portfolio`;
        if (category) {
            url += `?category=${category}`;
        }

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error('Ошибка получения портфолио');
        }

        return data.items;
    } catch (error) {
        console.error('Error:', error);
        return [];
    }
}

async function getContactInfo() {
    try {
        const response = await fetch(`${API_URL}/contact`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error('Ошибка получения контактов');
        }

        return data;
    } catch (error) {
        console.error('Error:', error);
        return null;
    }
}

async function createBooking(bookingData) {
    try {
        const response = await fetch(`${API_URL}/bookings`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`,
            },
            body: JSON.stringify(bookingData),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Ошибка создания бронирования');
        }

        return data;
    } catch (error) {
        throw error;
    }
}

// ====== ЗАГРУЗКА ДАННЫХ ======

async function loadServices() {
    const services = await getServices();
    const servicesGrid = document.getElementById('servicesGrid');

    if (servicesGrid && services.length > 0) {
        servicesGrid.innerHTML = services.map(service => `
            <div class="service-card">
                <div class="service-icon">✨</div>
                <h3>${service.name}</h3>
                <p>${service.description || ''}</p>
                <p class="service-price">от ${service.price} ₽</p>
            </div>
        `).join('');
    }
}

async function loadPortfolio() {
    const items = await getPortfolio();
    const portfolioGrid = document.getElementById('portfolioGrid');

    if (portfolioGrid && items.length > 0) {
        portfolioGrid.innerHTML = items.map(item => `
            <div class="portfolio-item" data-category="${item.category}">
                <img src="${item.image_url}" alt="${item.title}">
                <div class="portfolio-overlay">
                    <h3>${item.title}</h3>
                    <p>${item.description || ''}</p>
                </div>
            </div>
        `).join('');
    }
}

async function loadContactInfo() {
    const contact = await getContactInfo();

    if (contact) {
        if (contact.address) {
            document.getElementById('contactAddress').textContent = contact.address;
        }
        if (contact.phone) {
            document.getElementById('contactPhone').textContent = contact.phone;
        }
        if (contact.email) {
            document.getElementById('contactEmail').textContent = contact.email;
        }
        if (contact.latitude && contact.longitude) {
            document.getElementById('mapFrame').src =
                `https://yandex.ru/map-widget/v1/?ll=${contact.longitude}%2C${contact.latitude}&z=15`;
        }
    }
}

// ====== ФИЛЬТР ПОРТФОЛИО ======

function filterPortfolio(category) {
    const items = document.querySelectorAll('.portfolio-item');
    const buttons = document.querySelectorAll('.filter-btn');

    buttons.forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');

    items.forEach(item => {
        if (category === 'all' || item.dataset.category === category) {
            item.style.display = 'block';
            item.classList.add('fade-in');
        } else {
            item.style.display = 'none';
        }
    });
}

// ====== ФОРМА БРОНИРОВАНИЯ ======

async function handleBookingForm(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    const bookingData = {
        client_name: formData.get('name'),
        client_phone: formData.get('phone'),
        client_email: formData.get('email'),
        client_comment: formData.get('message') || '',
        service_id: parseInt(formData.get('service')),
        booking_date: new Date(formData.get('date')).toISOString(),
        master_id: null
    };

    try {
        await createBooking(bookingData);
        document.getElementById('successMessage').classList.add('show');
        form.reset();

        setTimeout(() => {
            document.getElementById('successMessage').classList.remove('show');
        }, 5000);
    } catch (error) {
        alert(`❌ ${error.message}`);
    }
}

// ====== НАВИГАЦИЯ SCROLL ======

window.addEventListener('scroll', () => {
    const navbar = document.getElementById('navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// ====== ФОРМАТИРОВАНИЕ ТЕЛЕФОНА ======

document.addEventListener('DOMContentLoaded', () => {
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 0) {
                if (value[0] === '7' || value[0] === '8') {
                    value = value.substring(1);
                }
                let formatted = '+7';
                if (value.length > 0) formatted += ' (' + value.substring(0, 3);
                if (value.length > 3) formatted += ') ' + value.substring(3, 6);
                if (value.length > 6) formatted += '-' + value.substring(6, 8);
                if (value.length > 8) formatted += '-' + value.substring(8, 10);
                e.target.value = formatted;
            }
        });
    }

    // Минимальная дата - сегодня
    const dateInput = document.getElementById('date');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.setAttribute('min', today);
    }

    // Проверка авторизации
    checkAuth();

    // Загрузка данных
    loadServices();
    loadPortfolio();
    loadContactInfo();

    // Обработчик формы
    const bookingForm = document.getElementById('bookingForm');
    if (bookingForm) {
        bookingForm.addEventListener('submit', handleBookingForm);
    }

    // Обработчики форм авторизации
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', login);
    }

    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', register);
    }
});