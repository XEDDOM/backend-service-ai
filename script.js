const API_BASE_URL = 'http://localhost:8000';

const form = document.getElementById('contactForm');
const submitBtn = document.getElementById('submitBtn');
const alert = document.getElementById('alert');
const aiResponse = document.getElementById('aiResponse');

const validators = {
    name: (value) => {
        if (value.length < 2) return 'Имя должно содержать минимум 2 символа';
        if (value.length > 50) return 'Имя должно содержать максимум 50 символов';
        return '';
    },
    phone: (value) => {
        const pattern = /^\+?[1-9]\d{10,14}$/;
        if (!pattern.test(value)) return 'Введите корректный номер телефона (например: +79001234567)';
        return '';
    },
    email: (value) => {
        const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!pattern.test(value)) return 'Введите корректный email';
        return '';
    },
    comment: (value) => {
        if (value.length < 10) return 'Комментарий должен содержать минимум 10 символов';
        if (value.length > 1000) return 'Комментарий должен содержать максимум 1000 символов';
        return '';
    }
};

function showError(fieldId, message) {
    const input = document.getElementById(fieldId);
    const errorDiv = document.getElementById(fieldId + 'Error');
    input.classList.add('error');
    errorDiv.textContent = message;
    errorDiv.classList.add('show');
}

function clearError(fieldId) {
    const input = document.getElementById(fieldId);
    const errorDiv = document.getElementById(fieldId + 'Error');
    input.classList.remove('error');
    errorDiv.classList.remove('show');
}

function showAlert(message, type) {
    alert.textContent = message;
    alert.className = `alert alert-${type} show`;
    setTimeout(() => {
        alert.classList.remove('show');
    }, 5000);
}

Object.keys(validators).forEach(fieldId => {
    const input = document.getElementById(fieldId);
    input.addEventListener('blur', () => {
        const error = validators[fieldId](input.value);
        if (error) {
            showError(fieldId, error);
        } else {
            clearError(fieldId);
        }
    });
    input.addEventListener('input', () => {
        clearError(fieldId);
    });
});

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    let hasErrors = false;
    const formData = {
        name: document.getElementById('name').value.trim(),
        phone: document.getElementById('phone').value.trim(),
        email: document.getElementById('email').value.trim(),
        comment: document.getElementById('comment').value.trim()
    };

    Object.keys(validators).forEach(fieldId => {
        const error = validators[fieldId](formData[fieldId]);
        if (error) {
            showError(fieldId, error);
            hasErrors = true;
        }
    });

    if (hasErrors) {
        showAlert('Пожалуйста, исправьте ошибки в форме', 'error');
        return;
    }

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner"></span> Отправка...';

    try {
        const response = await fetch(`${API_BASE_URL}/api/contact`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (response.ok) {
            showAlert('✅ ' + data.message, 'success');
            
            if (data.ai_sentiment || data.ai_generated_reply) {
                const sentimentBadge = document.getElementById('sentimentBadge');
                const sentimentClass = `sentiment-${data.ai_sentiment || 'neutral'}`;
                const sentimentText = {
                    'positive': '😊 Позитивный',
                    'negative': '😔 Негативный',
                    'neutral': '😐 Нейтральный'
                }[data.ai_sentiment] || '😐 Нейтральный';
                
                sentimentBadge.className = `sentiment-badge ${sentimentClass}`;
                sentimentBadge.textContent = sentimentText;
                
                document.getElementById('aiReply').textContent = data.ai_generated_reply;
                aiResponse.classList.add('show');
            }

            form.reset();
            
            setTimeout(() => {
                aiResponse.classList.remove('show');
            }, 10000);
        } else {
            const errorMsg = data.detail || 'Произошла ошибка при отправке';
            showAlert('❌ ' + errorMsg, 'error');
            
            if (response.status === 429) {
                showAlert('️ Слишком много запросов. Пожалуйста, подождите немного.', 'error');
            }
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('❌ Ошибка соединения с сервером. Проверьте, запущен ли backend.', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Отправить сообщение';
    }
});

window.addEventListener('load', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        if (response.ok) {
            console.log('✅ API is available');
        }
    } catch (error) {
        console.warn('⚠️ API is not available. Make sure backend is running on', API_BASE_URL);
        showAlert('⚠️ Backend сервер недоступен. Запустите backend на порту 8000.', 'info');
    }
});
