<template>
  <app-page title="Вход / Регистрация">
    <div class="auth-container">
      
      <!-- Табы с фиксированной шириной -->
      <div class="auth-tabs">
        <button 
          :class="{active: mode === 'login'}" 
          @click="mode = 'login'"
          class="tab-btn"
        >
          <span class="tab-icon">🚪</span>
          <span class="tab-text">Вход</span>
        </button>
        <button 
          :class="{active: mode === 'signup'}" 
          @click="mode = 'signup'"
          class="tab-btn"
        >
          <span class="tab-icon">📝</span>
          <span class="tab-text">Регистрация</span>
        </button>
      </div>

      <!-- Форма входа -->
      <form v-if="mode === 'login'" @submit.prevent="handleLogin" class="auth-form">
        <div class="form-header">
          <h2>Вход в систему</h2>
          <p class="subtitle">Добро пожаловать!</p>
        </div>
        
        <div class="form-group">
          <label>Логин</label>
          <input 
            v-model="loginForm.username" 
            type="text" 
            required 
            placeholder="Введите логин"
            autocomplete="username"
          >
        </div>
        
        <div class="form-group">
          <label>Пароль</label>
          <input 
            v-model="loginForm.password" 
            type="password" 
            required 
            placeholder="Введите пароль"
            autocomplete="current-password"
          >
        </div>
        
        <button type="submit" class="btn primary" :disabled="loading">
          {{ loading ? '⏳ Входим...' : '🚪 Войти' }}
        </button>
        
        <p v-if="error" class="error">❌ {{ error }}</p>
      </form>

      <!-- Форма регистрации -->
      <form v-if="mode === 'signup'" @submit.prevent="handleSignUp" class="auth-form">
        <div class="form-header">
          <h2>Регистрация</h2>
          <p class="subtitle">Создайте аккаунт</p>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label>Логин *</label>
            <input 
              v-model="signupForm.username" 
              type="text" 
              required 
              placeholder="Придумайте логин"
              autocomplete="username"
            >
          </div>
          <div class="form-group">
            <label>Email *</label>
            <input 
              v-model="signupForm.email" 
              type="email" 
              required 
              placeholder="example@mail.ru"
              autocomplete="email"
            >
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label>Пароль *</label>
            <input 
              v-model="signupForm.password" 
              type="password" 
              required 
              minlength="8" 
              placeholder="Минимум 8 символов"
              autocomplete="new-password"
            >
          </div>
          <div class="form-group">
            <label>Повтор пароля *</label>
            <input 
              v-model="signupForm.passwordConfirm" 
              type="password" 
              required 
              placeholder="Повторите пароль"
              autocomplete="new-password"
            >
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label>Имя</label>
            <input 
              v-model="signupForm.first_name" 
              type="text" 
              placeholder="Ваше имя"
              autocomplete="given-name"
            >
          </div>
          <div class="form-group">
            <label>Фамилия</label>
            <input 
              v-model="signupForm.last_name" 
              type="text" 
              placeholder="Ваша фамилия"
              autocomplete="family-name"
            >
          </div>
        </div>
        
        <div class="form-group">
          <label>Телефон</label>
          <input 
            v-model="signupForm.phone" 
            type="tel" 
            placeholder="+7 (999) 123-45-67"
            autocomplete="tel"
          >
        </div>
        
        <button type="submit" class="btn primary" :disabled="loading">
          {{ loading ? '⏳ Регистрируем...' : '📝 Зарегистрироваться' }}
        </button>
        
        <p v-if="error" class="error">❌ {{ error }}</p>
        <p class="hint">* — обязательные поля</p>
      </form>

      <!-- Сообщение об успехе -->
      <div v-if="successMessage" class="success-card">
        <div class="success-icon">✅</div>
        <h3>Регистрация успешна!</h3>
        <p>{{ successMessage }}</p>
        <button class="btn" @click="mode = 'login'">Перейти ко входу</button>
      </div>
      
    </div>
  </app-page>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import AppPage from '@/components/ui/AppPage'

export default {
  components: { AppPage },
  data() {
    return {
      mode: 'login',
      loading: false,
      error: null,
      successMessage: null,
      loginForm: {
        username: '',
        password: ''
      },
      signupForm: {
        username: '',
        email: '',
        password: '',
        passwordConfirm: '',
        first_name: '',
        last_name: '',
        phone: ''
      }
    }
  },
  computed: {
    ...mapGetters('auth', ['isAuthenticated'])
  },
  watch: {
    isAuthenticated(val) {
      if (val) this.$router.push('/')
    }
  },
  mounted() {
      if (this.isAuthenticated) {
        this.$router.push('/')
        return
      }

      if (this.$route.query.message === 'session_expired') {
        this.error = 'Сессия истекла. Войдите снова.'
      }
    },
  methods: {
    ...mapActions('auth', ['login', 'signUp']),
    
    async handleLogin() {
      this.loading = true
      this.error = null
      const result = await this.login(this.loginForm)
      this.loading = false
      if (result.success) {
        this.$router.push('/')
      } else {
        this.error = result.error
      }
    },
    
    async handleSignUp() {
      if (this.signupForm.password !== this.signupForm.passwordConfirm) {
        this.error = 'Пароли не совпадают'
        return
      }
      if (this.signupForm.password.length < 8) {
        this.error = 'Пароль должен содержать минимум 8 символов'
        return
      }
      
      this.loading = true
      this.error = null
      const result = await this.signUp(this.signupForm)
      this.loading = false
      
      if (result.success) {
        this.successMessage = 'Теперь войдите в систему'
        this.signupForm = {
          username: '', email: '', password: '', passwordConfirm: '',
          first_name: '', last_name: '', phone: ''
        }
      } else {
        this.error = result.error
      }
    }
  }
}
</script>

<style scoped>
.auth-container {
  max-width: 600px;  /* 🔥 Увеличено с 500px до 600px для десктопа */
  margin: 0 auto;
  padding: 1rem;
}

/* Табы с фиксированной шириной */
.auth-tabs {
  display: flex;
  margin-bottom: 2rem;
  background: white;
  border: 2px solid #03a147;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(3, 161, 71, 0.15);
}

.tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem;
  background: white;
  border: none;
  font-size: 1rem;
  font-weight: 600;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 140px;
}

.tab-btn:hover {
  background: #f0f9f4;
}

.tab-btn.active {
  background: #03a147;
  color: white;
}

.tab-icon {
  font-size: 1.2rem;
}

.tab-text {
  white-space: nowrap;
}

/* Формы одинаковой ширины */
.auth-form {
  background: white;
  border: 2px solid #03a147;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(3, 161, 71, 0.15);
}

.form-header {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #03a147;
}

.form-header h2 {
  margin: 0 0 0.5rem 0;
  color: #03a147;
  font-size: 1.5rem;
}

.subtitle {
  margin: 0;
  color: #666;
  font-size: 0.95rem;
}

/* 🔥 Сетка для полей - исправлено для десктопа */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;  /* 🔥 Уменьшено с 1.5rem до 1rem */
  margin-bottom: 0;  /* 🔥 Убрано, чтобы не добавлять лишние отступы */
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
  min-width: 0;  /* 🔥 Важно для grid - позволяет сжиматься */
}

.form-group label {
  font-weight: 600;
  color: #03a147;
  font-size: 0.9rem;
}

.form-group input {
  padding: 0.75rem;
  border: 2px solid #03a147;
  border-radius: 8px;
  font-size: 0.95rem;  /* 🔥 Чуть меньше для лучшего вмещения */
  transition: all 0.2s;
  width: 100%;  /* 🔥 Явно указываем ширину */
  box-sizing: border-box;  /* 🔥 Важно - включает padding в ширину */
}

.form-group input:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(3, 161, 71, 0.2);
}

.btn {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #03a147;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  background: white;
  color: #03a147;
  margin-top: 0.5rem;
  box-sizing: border-box;  /* 🔥 Важно */
}

.btn.primary {
  background: #03a147;
  color: white;
}

.btn:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.error {
  color: #c62828;
  background: #ffebee;
  padding: 0.75rem;
  border-radius: 8px;
  margin: 1rem 0 0 0;
  border: 2px solid #e53935;
  text-align: center;
}

.hint {
  font-size: 0.85rem;
  color: #666;
  text-align: center;
  margin-top: 1rem;
  font-style: italic;
}

/* Сообщение об успехе */
.success-card {
  background: white;
  border: 2px solid #03a147;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 4px 12px rgba(3, 161, 71, 0.15);
}

.success-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.success-card h3 {
  margin: 0 0 0.5rem 0;
  color: #03a147;
}

.success-card p {
  color: #666;
  margin-bottom: 1.5rem;
}

/* 🔥 Мобильная адаптация */
@media (max-width: 600px) {
  .auth-container {
    padding: 0.5rem;
    max-width: 100%;
  }
  
  .auth-tabs {
    flex-direction: row;
  }
  
  .tab-btn {
    padding: 0.75rem 0.5rem;
    font-size: 0.9rem;
    min-width: auto;
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .tab-icon {
    font-size: 1.1rem;
  }
  
  .tab-text {
    font-size: 0.85rem;
  }
  
  .auth-form {
    padding: 1.5rem;
  }
  
  .form-header h2 {
    font-size: 1.3rem;
  }
  
  /* 🔥 На мобильном одна колонка */
  .form-row {
    grid-template-columns: 1fr;
    gap: 0;
  }
  
  .form-group input {
    font-size: 0.95rem;
    padding: 0.65rem;
  }
  
  .btn {
    font-size: 0.95rem;
    padding: 0.65rem;
  }
  
  .success-card {
    padding: 1.5rem;
  }
  
  .success-icon {
    font-size: 2.5rem;
  }
}

/* 🔥 Очень маленькие экраны */
@media (max-width: 400px) {
  .tab-btn {
    flex-direction: row;
    gap: 0.3rem;
  }
  
  .tab-text {
    font-size: 0.8rem;
  }
  
  .auth-form {
    padding: 1rem;
  }
  
  .form-group input {
    font-size: 0.9rem;
    padding: 0.6rem;
  }
}
</style>
