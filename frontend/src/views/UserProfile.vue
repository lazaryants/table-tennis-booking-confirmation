<template>
  <app-page title="Мой профиль">
    <div class="profile-container">
      
      <div v-if="loading" class="loading">
        <app-loader></app-loader>
      </div>

      <form v-else @submit.prevent="saveProfile" class="profile-form">
        <div class="form-header">
          <h2>👤 Информация о пользователе</h2>
        </div>
        
        <div class="form-grid">
          <div class="form-group">
            <label>Имя</label>
            <input v-model="form.first_name" type="text" placeholder="Ваше имя">
          </div>
          <div class="form-group">
            <label>Фамилия</label>
            <input v-model="form.last_name" type="text" placeholder="Ваша фамилия">
          </div>
          <div class="form-group">
            <label>Email</label>
            <input v-model="form.email" type="email" placeholder="example@mail.ru">
          </div>
          <div class="form-group">
            <label>Телефон</label>
            <input v-model="form.phone" type="tel" placeholder="+7 (999) 123-45-67">
          </div>
          <div class="form-group">
            <label>Логин</label>
            <input :value="username" disabled class="disabled">
            <small>Логин нельзя изменить</small>
          </div>
          <div class="form-group">
            <label>Новый пароль</label>
            <input v-model="form.new_password" type="password" placeholder="Оставьте пустым, чтобы не менять" minlength="8">
            <small>Минимум 8 символов</small>
          </div>
        </div>
        
        <div class="form-actions">
          <button type="submit" class="btn primary" :disabled="saving">
            {{ saving ? 'Сохраняем...' : '💾 Сохранить изменения' }}
          </button>
          <button type="button" class="btn" @click="resetForm">↩️ Отмена</button>
        </div>
        
        <p v-if="message" :class="['message', messageType]">{{ message }}</p>
      </form>

      <div class="logout-section">
        <button class="btn danger" @click="handleLogout">🚪 Выйти из аккаунта</button>
      </div>
    </div>
  </app-page>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import AppPage from '@/components/ui/AppPage'
import AppLoader from '@/components/ui/AppLoader'
import axios from '@/utils/axios'

export default {
  components: { AppPage, AppLoader },
  data() {
    return {
      loading: true,
      saving: false,
      message: null,
      messageType: 'info',
      form: {
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        new_password: ''
      }
    }
  },
  computed: {
    ...mapGetters('auth', ['isAuthenticated', 'username', 'user'])
  },
  async mounted() {
    if (!this.isAuthenticated) {
      this.$router.push('/auth')
      return
    }
    await this.loadProfileData()
  },
  methods: {
    ...mapActions('auth', ['loadProfile', 'updateProfile', 'logout']),
    
    async loadProfileData() {
      this.loading = true
      const result = await this.loadProfile()
      if (result?.success && result.data) {
        this.form = {
          first_name: result.data.first_name || '',
          last_name: result.data.last_name || '',
          email: result.data.email || '',
          phone: result.data.phone || '',
          new_password: ''
        }
      }
      this.loading = false
    },
    
    resetForm() {
      if (this.user) {
        this.form = {
          first_name: this.user.first_name || '',
          last_name: this.user.last_name || '',
          email: this.user.email || '',
          phone: this.user.phone || '',
          new_password: ''
        }
      }
      this.message = null
    },
    
    async saveProfile() {
      this.saving = true
      this.message = null
      try {
        const updateData = {
          first_name: this.form.first_name,
          last_name: this.form.last_name,
          phone: this.form.phone,
          email: this.form.email
        }
        if (this.form.new_password && this.form.new_password.length >= 8) {
          updateData.password = this.form.new_password
        }
        const { data } = await axios.patch('/users/update_profile/', updateData)
        this.message = '✅ Профиль успешно обновлён!'
        this.messageType = 'success'
        this.form.new_password = ''
      } catch (e) {
        const errors = e.response?.data
        let message = '❌ Ошибка при сохранении'
        if (errors?.email) message = '❌ Такой email уже занят'
        else if (errors?.detail) message = '❌ ' + errors.detail
        this.message = message
        this.messageType = 'error'
      } finally {
        this.saving = false
      }
    },
    
    handleLogout() {
      if (confirm('Вы действительно хотите выйти?')) {
        this.logout()
      }
    }
  }
}
</script>

<style scoped>
.profile-container { max-width: 700px; margin: 0 auto; }
.profile-form { background: white; border: 2px solid #03a147; border-radius: 12px; padding: 2rem; box-shadow: 0 4px 12px rgba(3, 161, 71, 0.15); margin-bottom: 2rem; }
.form-header { margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 2px solid #03a147; }
.form-header h2 { margin: 0; color: #03a147; font-size: 1.5rem; }
.form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 1.5rem; }
.form-group { display: flex; flex-direction: column; gap: 0.5rem; }
.form-group label { font-weight: 600; color: #03a147; font-size: 0.9rem; }
.form-group input { padding: 0.75rem; border: 2px solid #03a147; border-radius: 8px; font-size: 1rem; transition: all 0.2s; }
.form-group input:focus { outline: none; box-shadow: 0 0 0 3px rgba(3, 161, 71, 0.2); }
.form-group input.disabled { background: #f5f5f5; color: #666; cursor: not-allowed; }
.form-group small { font-size: 0.8rem; color: #666; font-style: italic; }
.form-actions { display: flex; gap: 1rem; margin-top: 1.5rem; flex-wrap: wrap; }
.message { padding: 1rem; border-radius: 8px; margin-top: 1.5rem; font-weight: 500; border: 2px solid; }
.message.success { background: #e8f5e9; color: #155724; border-color: #03a147; }
.message.error { background: #ffebee; color: #c62828; border-color: #e53935; }
.logout-section { text-align: center; padding: 1.5rem; background: white; border: 2px solid #e53935; border-radius: 12px; box-shadow: 0 4px 12px rgba(229, 57, 53, 0.15); }
.btn { padding: 0.75rem 1.5rem; border: 2px solid #03a147; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: all 0.2s; background: white; color: #03a147; }
.btn.primary { background: #03a147; color: white; }
.btn.danger { background: #e53935; color: white; border-color: #e53935; }
.btn:hover:not(:disabled) { opacity: 0.9; transform: translateY(-1px); }
.btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
.loading { text-align: center; padding: 3rem; background: white; border: 2px solid #03a147; border-radius: 12px; }
@media (max-width: 768px) {
  .profile-form { padding: 1.5rem; }
  .form-grid { grid-template-columns: 1fr; }
  .form-actions { flex-direction: column; }
  .btn { width: 100%; }
  .logout-section { padding: 1rem; }
}
</style>
