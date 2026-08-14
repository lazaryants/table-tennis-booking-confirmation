<template>
  <app-page title="Админ-панель">
    <div class="admin-container">
      
      <!-- Вкладки -->
      <div class="tabs">
        <button
            v-if="isAdmin"
            :class="{active: tab === 'users'}"
            @click="tab = 'users'"
          >
          👥 Пользователи
        </button>
        <button :class="{active: tab === 'bookings'}" @click="tab = 'bookings'">
          📋 Бронирования
        </button>
      </div>

      <!-- ==================== ПОЛЬЗОВАТЕЛИ ==================== -->
      <div v-if="isAdmin && tab === 'users'">
        <div class="header">
          <h2>Управление пользователями</h2>
          <button class="btn primary" @click="openCreateModal">+ Добавить</button>
        </div>

        <!-- Форма создания -->
        <div v-if="showCreateModal" class="form-card">
          <h3>Новый пользователь</h3>
          <div class="form-grid">
            <div class="form-group">
              <label>Логин *</label>
              <input v-model="createForm.username" type="text" required>
            </div>
            <div class="form-group">
              <label>Email *</label>
              <input v-model="createForm.email" type="email" required>
            </div>
            <div class="form-group">
              <label>Пароль *</label>
              <input v-model="createForm.password" type="password" required minlength="8">
            </div>
            <div class="form-group">
              <label>Имя</label>
              <input v-model="createForm.first_name" type="text">
            </div>
            <div class="form-group">
              <label>Фамилия</label>
              <input v-model="createForm.last_name" type="text">
            </div>
            <div class="form-group">
              <label>Телефон</label>
              <input v-model="createForm.phone" type="tel">
            </div>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn primary" @click="createUser" :disabled="saving">
              {{ saving ? 'Создаём...' : 'Создать' }}
            </button>
            <button type="button" class="btn" @click="closeCreateModal">Отмена</button>
          </div>
          <p v-if="createError" class="error">{{ createError }}</p>
        </div>

        <!-- Список пользователей -->
        <div v-if="usersLoading" class="loading">Загрузка...</div>
        <div v-else class="cards-grid">
          <div v-for="user in users" :key="user.id" class="user-card">
            <div class="card-header">
              <div class="user-info">
                <h3>{{ user.first_name }} {{ user.last_name }}</h3>
                <p class="username">@{{ user.username }}</p>
              </div>
              <div class="badges">
                <span v-if="user.is_staff" class="badge admin">Админ</span>
                <span :class="['badge', user.is_active ? 'active' : 'inactive']">
                  {{ user.is_active ? '✓' : '✗' }}
                </span>
              </div>
            </div>
            
            <div class="card-body">
              <p><strong>Email:</strong> {{ user.email }}</p>
              <p><strong>Телефон:</strong> {{ user.phone || '—' }}</p>
              <p><strong>Броней:</strong> {{ user.bookings_count }}</p>
              <p><strong>Вход:</strong> {{ formatDate(user.last_login) }}</p>
            </div>
            
            <div class="card-actions">
              <button class="btn-icon" @click="openEditModal(user)" title="Редактировать">✏️</button>
              <button class="btn-icon danger" @click="confirmDeleteUser(user)" :disabled="user.id === currentUserId" title="Удалить">🗑️</button>
            </div>
          </div>
        </div>
      </div>

      <!-- ==================== БРОНИРОВАНИЯ ==================== -->
      <div v-if="tab === 'bookings'">
        <div class="header">
          <h2>Все бронирования</h2>
          <div class="filters">
            <select v-model="bookingFilter.status" @change="loadBookings">
              <option value="">Все статусы</option>
              <option value="pending">Ожидают</option>
              <option value="confirmed">Подтверждены</option>
            </select>
            <input type="date" v-model="bookingFilter.date" @change="loadBookings">
            <button class="btn" @click="resetFilters">Сброс</button>
          </div>
        </div>

        <div v-if="bookingsLoading" class="loading">Загрузка...</div>
        <div v-else class="cards-grid">
          <div v-for="booking in bookings" :key="booking.id" class="booking-card">
            <div class="card-header">
              <div class="booking-info">
                <h3>Стол №{{ booking.table_number }}</h3>
                <p>{{ formatDate(booking.date) }} | {{ formatHour(booking.hour) }}</p>
              </div>
              <span :class="['badge', 'status', booking.status]">
                {{ getStatusText(booking.status) }}
              </span>
            </div>
            
            <div class="card-body">
              <p><strong>Пользователь:</strong> {{ getUserName(booking) }}</p>
              <p v-if="isAdmin || isManager"><strong>Телефон:</strong> {{ booking.user_phone || '—' }}</p>
              <p><strong>Создано:</strong> {{ formatDateTime(booking.created_at) }}</p>
            </div>
            
            <div class="card-actions">
              <template v-if="isFuture(booking) && booking.status === 'pending'">
                <button class="btn-icon primary" @click="openConfirmModal(booking)" title="Подтвердить">✓</button>
                <button class="btn-icon danger" @click="openRejectModal(booking)" title="Отклонить">✗</button>
              </template>
              <button class="btn-icon warning" @click="openDeleteBookingModal(booking)" title="Удалить">🗑️</button>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- ==================== МОДАЛКИ ==================== -->
    
    <!-- Создание пользователя -->
    <teleport to="body">
      <div v-if="showCreateModal" class="modal-backdrop" @click="closeCreateModal">
        <div class="modal-content" @click.stop>
          <h3>Новый пользователь</h3>
          <form @submit.prevent="createUser">
            <div class="form-grid">
              <div class="form-group">
                <label>Логин *</label>
                <input v-model="createForm.username" type="text" required>
              </div>
              <div class="form-group">
                <label>Email *</label>
                <input v-model="createForm.email" type="email" required>
              </div>
              <div class="form-group">
                <label>Пароль *</label>
                <input v-model="createForm.password" type="password" required minlength="8">
              </div>
              <div class="form-group">
                <label>Имя</label>
                <input v-model="createForm.first_name" type="text">
              </div>
              <div class="form-group">
                <label>Фамилия</label>
                <input v-model="createForm.last_name" type="text">
              </div>
              <div class="form-group">
                <label>Телефон</label>
                <input v-model="createForm.phone" type="tel">
              </div>
            </div>
            <div class="modal-actions">
              <button type="submit" class="btn primary" :disabled="saving">
                {{ saving ? 'Создаём...' : 'Создать' }}
              </button>
              <button type="button" class="btn" @click="closeCreateModal">Отмена</button>
            </div>
            <p v-if="createError" class="error">{{ createError }}</p>
          </form>
        </div>
      </div>
    </teleport>

    <!-- Редактирование пользователя -->
    <teleport to="body">
      <div v-if="showEditModal" class="modal-backdrop" @click="closeEditModal">
        <div class="modal-content" @click.stop>
          <h3>Редактировать пользователя</h3>
          <form @submit.prevent="saveUser">
            <div class="form-grid">
              <div class="form-group">
                <label>Логин</label>
                <input :value="editForm.username" disabled class="disabled">
              </div>
              <div class="form-group">
                <label>Email *</label>
                <input v-model="editForm.email" type="email" required>
              </div>
              <div class="form-group">
                <label>Имя</label>
                <input v-model="editForm.first_name" type="text">
              </div>
              <div class="form-group">
                <label>Фамилия</label>
                <input v-model="editForm.last_name" type="text">
              </div>
              <div class="form-group">
                <label>Телефон</label>
                <input v-model="editForm.phone" type="tel">
              </div>
              <div class="form-group">
                <label>Новый пароль</label>
                <input v-model="editForm.new_password" type="password" placeholder="Оставьте пустым" minlength="8">
              </div>
              <div class="form-group checkbox">
                <label>
                  <input type="checkbox" v-model="editForm.is_manager">
                  Права менеджера
                </label>
                <small>
                  Управление бронированиями и просмотр контактов клиентов
                </small>
              </div>

              <div class="form-group checkbox">
                <label>
                  <input type="checkbox" v-model="editForm.is_staff">
                  Права администратора
                </label>
              </div>
              <div class="form-group checkbox">
                <label>
                  <input type="checkbox" v-model="editForm.is_active">
                  Активен
                </label>
              </div>
            </div>
            <div class="modal-actions">
              <button type="submit" class="btn primary" :disabled="saving">
                {{ saving ? 'Сохраняем...' : 'Сохранить' }}
              </button>
              <button type="button" class="btn" @click="closeEditModal">Отмена</button>
            </div>
            <p v-if="editError" class="error">{{ editError }}</p>
          </form>
        </div>
      </div>
    </teleport>

    <!-- Удаление пользователя -->
    <teleport to="body">
      <div v-if="showDeleteUserModal" class="modal-backdrop" @click="closeDeleteUserModal">
        <div class="modal-content small" @click.stop>
          <h3>⚠️ Удалить пользователя?</h3>
          <p><strong>{{ selectedUser?.username }}</strong></p>
          <p class="warning">Все бронирования будут удалены!</p>
          <div class="modal-actions">
            <button class="btn danger" @click="deleteUserAction">🗑️ Удалить</button>
            <button class="btn" @click="closeDeleteUserModal">Отмена</button>
          </div>
        </div>
      </div>
    </teleport>

    <!-- Подтверждение брони -->
    <teleport to="body">
      <div v-if="showConfirmModal" class="modal-backdrop" @click="closeConfirmModal">
        <div class="modal-content small" @click.stop>
          <h3>✓ Подтвердить бронь?</h3>
          <p><strong>Пользователь:</strong> {{ getUserName(selectedBooking) }}</p>
          <p><strong>Дата:</strong> {{ formatDate(selectedBooking?.date) }}</p>
          <p><strong>Время:</strong> {{ formatHour(selectedBooking?.hour) }}</p>
          <p><strong>Стол:</strong> №{{ selectedBooking?.table_number }}</p>
          <div class="modal-actions">
            <button class="btn primary" @click="confirmBookingAction">✓ Да</button>
            <button class="btn" @click="closeConfirmModal">Отмена</button>
          </div>
        </div>
      </div>
    </teleport>

    <!-- Отклонение брони -->
    <teleport to="body">
      <div v-if="showRejectModal" class="modal-backdrop" @click="closeRejectModal">
        <div class="modal-content small" @click.stop>
          <h3>✗ Отклонить бронь?</h3>
          <p><strong>Пользователь:</strong> {{ getUserName(selectedBooking) }}</p>
          <p><strong>Дата:</strong> {{ formatDate(selectedBooking?.date) }}</p>
          <p><strong>Время:</strong> {{ formatHour(selectedBooking?.hour) }}</p>
          <p><strong>Стол:</strong> №{{ selectedBooking?.table_number }}</p>
          <p class="warning">Бронь будет удалена</p>
          <div class="modal-actions">
            <button class="btn danger" @click="rejectBookingAction">✗ Да</button>
            <button class="btn" @click="closeRejectModal">Отмена</button>
          </div>
        </div>
      </div>
    </teleport>

    <!-- Удаление брони -->
    <teleport to="body">
      <div v-if="showDeleteBookingModal" class="modal-backdrop" @click="closeDeleteBookingModal">
        <div class="modal-content small" @click.stop>
          <h3>🗑️ Удалить бронь?</h3>
          <p><strong>Пользователь:</strong> {{ getUserName(selectedBooking) }}</p>
          <p><strong>Дата:</strong> {{ formatDate(selectedBooking?.date) }}</p>
          <p><strong>Время:</strong> {{ formatHour(selectedBooking?.hour) }}</p>
          <p><strong>Стол:</strong> №{{ selectedBooking?.table_number }}</p>
          <div class="modal-actions">
            <button class="btn danger" @click="deleteBookingAction">🗑️ Да</button>
            <button class="btn" @click="closeDeleteBookingModal">Отмена</button>
          </div>
        </div>
      </div>
    </teleport>

  </app-page>
</template>

<script>
import axios from '@/utils/axios'
import AppPage from '@/components/ui/AppPage'
import { useStore } from 'vuex'
import { computed } from 'vue'

export default {
  name: 'AdminPanel',
  components: { AppPage },
  setup() {
    const store = useStore()
    const currentUserId = computed(() => store.getters['auth/user']?.id)
    const isAdmin = computed(() => store.getters['auth/isAdmin'])
    const isManager = computed(() => store.getters['auth/isManager'])

    return { currentUserId, isAdmin, isManager }
  },
  data() {
    return {
      tab: 'bookings',
      users: [],
      usersLoading: true,
      bookings: [],
      bookingsLoading: true,
      bookingFilter: { status: '', date: '' },
      
      showCreateModal: false,
      showEditModal: false,
      showDeleteUserModal: false,
      showConfirmModal: false,
      showRejectModal: false,
      showDeleteBookingModal: false,
      
      saving: false,
      createError: null,
      editError: null,
      
      createForm: {
        username: '', email: '', password: '',
        first_name: '', last_name: '', phone: ''
      },
      editForm: {
        id: null, username: '', email: '',
        first_name: '', last_name: '', phone: '',
        is_staff: false, is_active: true, new_password: ''
      },
      
      selectedUser: null,
      selectedBooking: null
    }
  },
  async mounted() {
      if (this.isAdmin) {
        await this.loadData()
      } else {
        await this.loadBookings()
      }
    },
  methods: {
    async loadData() {
      await Promise.all([this.loadUsers(), this.loadBookings()])
    },
    
    async loadUsers() {
      this.usersLoading = true
      try {
        const { data } = await axios.get('/users/')
        this.users = Array.isArray(data) ? data : (data.results || [])
      } catch (e) {
        console.error('Error loading users:', e)
      } finally {
        this.usersLoading = false
      }
    },
    
    async loadBookings() {
      this.bookingsLoading = true
      try {
        const params = {}
        if (this.bookingFilter.status) params.status = this.bookingFilter.status
        if (this.bookingFilter.date) params.date = this.bookingFilter.date
        const { data } = await axios.get('/bookings/', { params })
        this.bookings = Array.isArray(data) ? data : (data.results || [])
      } catch (e) {
        console.error('Error loading bookings:', e)
      } finally {
        this.bookingsLoading = false
      }
    },
    
    resetFilters() {
      this.bookingFilter = { status: '', date: '' }
      this.loadBookings()
    },
    
    isFuture(booking) {
      if (!booking?.date || !booking?.hour) return false
      const now = new Date()
      const bookingDate = new Date(booking.date)
      bookingDate.setHours(booking.hour, 0, 0, 0)
      return bookingDate > now
    },
    
    getUserName(booking) {
      if (!booking) return '—'
      if (booking.user_first_name && booking.user_last_name) {
        return `${booking.user_first_name} ${booking.user_last_name}`
      }
      return booking.user_name || '—'
    },
    
    openCreateModal() {
      this.createForm = { username: '', email: '', password: '', first_name: '', last_name: '', phone: '' }
      this.createError = null
      this.showCreateModal = true
    },
    closeCreateModal() { this.showCreateModal = false },
    
    openEditModal(user) {
      this.editForm = {
        id: user.id, username: user.username, email: user.email,
        first_name: user.first_name || '', last_name: user.last_name || '',
        phone: user.phone || '',
        is_manager: user.is_manager || false,
        is_staff: user.is_staff || false,
        is_active: user.is_active !== undefined ? user.is_active : true,
        new_password: ''
      }
      this.editError = null
      this.showEditModal = true
    },
    closeEditModal() { this.showEditModal = false },
    
    confirmDeleteUser(user) {
      if (user.id === this.currentUserId) {
        alert('Нельзя удалить самого себя')
        return
      }
      this.selectedUser = user
      this.showDeleteUserModal = true
    },
    closeDeleteUserModal() { this.showDeleteUserModal = false },
    
    openConfirmModal(booking) { this.selectedBooking = booking; this.showConfirmModal = true },
    closeConfirmModal() { this.showConfirmModal = false },
    
    openRejectModal(booking) { this.selectedBooking = booking; this.showRejectModal = true },
    closeRejectModal() { this.showRejectModal = false },
    
    openDeleteBookingModal(booking) { this.selectedBooking = booking; this.showDeleteBookingModal = true },
    closeDeleteBookingModal() { this.showDeleteBookingModal = false },
    
    async createUser() {
      if (!this.createForm.username || !this.createForm.email || !this.createForm.password) {
        this.createError = 'Заполните обязательные поля'
        return
      }
      if (this.createForm.password.length < 8) {
        this.createError = 'Пароль должен содержать минимум 8 символов'
        return
      }
      
      this.saving = true
      this.createError = null
      try {
        await axios.post('/users/', this.createForm)
        this.closeCreateModal()
        await this.loadUsers()
        alert('Пользователь создан')
      } catch (e) {
        const errors = e.response?.data
        if (errors?.username) this.createError = 'Такой логин уже занят'
        else if (errors?.email) this.createError = 'Такой email уже зарегистрирован'
        else if (errors?.detail) this.createError = errors.detail
        else this.createError = 'Ошибка при создании'
      } finally {
        this.saving = false
      }
    },
    
    async saveUser() {
      this.saving = true
      this.editError = null
      try {
        const updateData = {
          email: this.editForm.email,
          first_name: this.editForm.first_name,
          last_name: this.editForm.last_name,
          phone: this.editForm.phone,
          is_manager: this.editForm.is_manager,
          is_staff: this.editForm.is_staff,
          is_active: this.editForm.is_active
        }
        if (this.editForm.new_password && this.editForm.new_password.length >= 8) {
          updateData.password = this.editForm.new_password
        }
        await axios.patch(`/users/${this.editForm.id}/`, updateData)
        this.closeEditModal()
        await this.loadUsers()
        alert('Пользователь обновлён')
      } catch (e) {
        const errors = e.response?.data
        if (errors?.email) this.editError = 'Такой email уже занят'
        else if (errors?.detail) this.editError = errors.detail
        else this.editError = 'Ошибка при сохранении'
      } finally {
        this.saving = false
      }
    },
    
    async deleteUserAction() {
      try {
        await axios.delete(`/users/${this.selectedUser.id}/`)
        this.closeDeleteUserModal()
        await this.loadUsers()
        alert('Пользователь удалён')
      } catch (e) {
        alert('Ошибка: ' + (e.response?.data?.detail || 'Неизвестная ошибка'))
      }
    },
    
    async confirmBookingAction() {
      try {
        await axios.post(`/bookings/${this.selectedBooking.id}/confirm/`)
        this.closeConfirmModal()
        await this.loadBookings()
        alert('Бронь подтверждена')
      } catch (e) {
        alert('Ошибка: ' + (e.response?.data?.detail || 'Неизвестная ошибка'))
      }
    },
    
    async rejectBookingAction() {
      try {
        await axios.post(`/bookings/${this.selectedBooking.id}/reject/`)
        this.closeRejectModal()
        await this.loadBookings()
        alert('Бронь отклонена')
      } catch (e) {
        alert('Ошибка: ' + (e.response?.data?.detail || 'Неизвестная ошибка'))
      }
    },
    
    async deleteBookingAction() {
      try {
        await axios.delete(`/bookings/${this.selectedBooking.id}/`)
        this.closeDeleteBookingModal()
        await this.loadBookings()
        alert('Бронь удалена')
      } catch (e) {
        alert('Ошибка: ' + (e.response?.data?.detail || 'Неизвестная ошибка'))
      }
    },
    
    formatDate(dateStr) {
      if (!dateStr) return 'Не указано'
      const d = new Date(dateStr)
      return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
    },
    formatHour(hour) {
      return `${hour.toString().padStart(2, '0')}:00 - ${(hour + 1).toString().padStart(2, '0')}:00`
    },
    formatDateTime(dateStr) {
      if (!dateStr) return 'Не указано'
      const d = new Date(dateStr)
      return d.toLocaleString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
    },
    getStatusText(status) {
      return { pending: 'Ожидает', confirmed: 'Подтверждено', cancelled: 'Отменено' }[status] || status
    }
  }
}
</script>

<style scoped>
.admin-container { max-width: 1200px; margin: 0 auto; padding: 0 1rem; }

.tabs {
  display: flex;
  gap: 1rem;
  margin: 1rem 0 2rem;
  border-bottom: 2px solid #03a147;
}
.tabs button {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  font-size: 1rem;
  font-weight: 600;
  color: #666;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
}
.tabs button.active {
  color: #03a147;
  border-bottom-color: #03a147;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}
.filters {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}
.filters select, .filters input {
  padding: 0.5rem;
  border: 2px solid #03a147;
  border-radius: 6px;
  font-size: 0.95rem;
}

/* 🔥 КАРТОЧКИ с зелёными рамками */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  width: 100%;
}

.user-card, .booking-card {
  background: white;
  border: 2px solid #03a147;
  border-radius: 12px;
  padding: 1rem;
  box-shadow: 0 4px 12px rgba(3, 161, 71, 0.15);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  transition: box-shadow 0.2s;
}

.user-card:hover, .booking-card:hover {
  box-shadow: 0 6px 20px rgba(3, 161, 71, 0.25);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #03a147;
}

.user-info h3, .booking-info h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.1rem;
  color: #03a147;
}

.username {
  color: #666;
  margin: 0;
  font-size: 0.85rem;
}

.badges {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
}

.badge {
  padding: 0.2rem 0.5rem;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid #03a147;
}
.badge.admin { background: #e53935; color: white; border-color: #e53935; }
.badge.active { background: #03a147; color: white; }
.badge.inactive { background: #9e9e9e; color: white; border-color: #9e9e9e; }
.badge.status.pending { background: #ffc107; color: #000; border-color: #ffc107; }
.badge.status.confirmed { background: #03a147; color: white; }
.badge.status.cancelled { background: #dc3545; color: white; border-color: #dc3545; }

.card-body {
  flex: 1;
}
.card-body p {
  margin: 0.5rem 0;
  font-size: 0.9rem;
  color: #555;
}
.card-body p strong {
  color: #03a147;
}

/* 🔥 КНОПКИ-КВАДРАТЫ - ИСПРАВЛЕННОЕ ВЫРАВНИВАНИЕ */
.card-actions {
  display: flex;
  gap: 0.5rem;
  padding-top: 0.75rem;
  border-top: 2px solid #03a147;
  flex-wrap: wrap;
  align-items: center;
}

.btn-icon {
  width: 44px;
  height: 44px;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-size: 1.3rem;
  line-height: 1;
  border: 2px solid #03a147;
  background: white;
  color: #03a147;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.btn-icon:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.btn-icon.primary {
  background: #03a147;
  color: white;
  border-color: #03a147;
}

.btn-icon.warning {
  background: #ffc107;
  color: #000;
  border-color: #ffc107;
}

.btn-icon.danger {
  background: #e53935;
  color: white;
  border-color: #e53935;
}

.btn-icon:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* 🔥 КНОПКИ для модалок (прямоугольные) */
.btn {
  padding: 0.75rem 1.5rem;
  border: 2px solid #03a147;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  background: white;
  color: #03a147;
}

.btn.primary {
  background: #03a147;
  color: white;
}

.btn.danger {
  background: #e53935;
  color: white;
  border-color: #e53935;
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

/* Формы */
.form-card {
  background: white;
  border: 2px solid #03a147;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 12px rgba(3, 161, 71, 0.15);
}
.form-card h3 { margin: 0 0 1rem 0; color: #03a147; }
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}
.form-group label {
  font-weight: 600;
  font-size: 0.9rem;
  color: #03a147;
}
.form-group input {
  padding: 0.6rem;
  border: 2px solid #03a147;
  border-radius: 6px;
  font-size: 1rem;
}
.form-group input:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(3, 161, 71, 0.2);
}
.form-group input.disabled {
  background: #f5f5f5;
  color: #666;
  cursor: not-allowed;
}
.form-group.checkbox {
  flex-direction: row;
  align-items: center;
  gap: 0.5rem;
}
.form-group.checkbox input { width: auto; margin: 0; }
.form-actions, .modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}
.error {
  color: #e53935;
  background: #ffebee;
  padding: 0.75rem;
  border-radius: 8px;
  margin-top: 1rem;
  font-size: 0.9rem;
  border: 2px solid #e53935;
}

/* Модалки */
.modal-backdrop {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}
.modal-content {
  background: white;
  border: 2px solid #03a147;
  border-radius: 12px;
  padding: 1.5rem;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(3, 161, 71, 0.2);
}
.modal-content.small { max-width: 400px; }
.modal-content h3 { margin: 0 0 1rem 0; color: #03a147; }
.warning {
  background: #ffebee;
  color: #c62828;
  padding: 0.75rem;
  border-radius: 8px;
  margin: 0.5rem 0;
  border: 2px solid #e53935;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #666;
}

/* Мобильная адаптация */
@media (max-width: 768px) {
  .header { flex-direction: column; align-items: stretch; }
  .filters { flex-direction: column; }
  .filters select, .filters input { width: 100%; }
  
  .cards-grid { grid-template-columns: 1fr; }
  .user-card, .booking-card { width: 100%; margin-bottom: 1rem; }
  
  .form-grid { grid-template-columns: 1fr; }
  
  .modal-content { padding: 1rem; }
  .modal-actions { flex-direction: column; }
  .modal-actions .btn { width: 100%; }
  
  .card-header { flex-direction: column; gap: 0.5rem; }
  .badges { align-self: flex-start; }
}
</style>
