<template>
  <app-page title="Мои бронирования">
    <div class="bookings-container">
      
      <!-- Загрузка -->
      <div v-if="loading" class="loading">
        <app-loader></app-loader>
      </div>

      <!-- Пустой список -->
      <div v-else-if="bookings.length === 0" class="empty">
        <div class="empty-card">
          <h3>📭 У вас пока нет бронирований</h3>
          <p>Забронируйте стол прямо сейчас!</p>
          <router-link to="/" class="btn primary">🎾 Забронировать стол</router-link>
        </div>
      </div>

      <!-- Список броней -->
      <div v-else class="bookings-list">
        <div v-for="booking in bookings" :key="booking.id" class="booking-card">
          <div class="card-header">
            <div class="booking-info">
              <h3>🏓 Стол №{{ booking.table_number }}</h3>
              <p class="booking-date">{{ formatDate(booking.date) }}</p>
            </div>
            <span :class="['badge', 'status', booking.status]">
              {{ getStatusText(booking.status) }}
            </span>
          </div>
          
          <div class="card-body">
            <div class="info-row">
              <strong>⏰ Время:</strong> {{ formatHour(booking.hour) }}
            </div>
            <div class="info-row">
              <strong>📅 Создано:</strong> {{ formatDateTime(booking.created_at) }}
            </div>
            <div v-if="booking.status === 'confirmed'" class="info-row success">
              <strong>✓ Статус:</strong> Подтверждено администратором
            </div>
            <div v-if="booking.status === 'pending'" class="info-row warning">
              <strong>⏳ Статус:</strong> Ожидает подтверждения
            </div>
          </div>
          
          <div class="card-actions">
            <button 
              v-if="canCancel(booking)" 
              class="btn danger" 
              @click="cancelBooking(booking)"
            >
              🗑️ Отменить бронь
            </button>
            <span v-else-if="booking.status === 'confirmed'" class="hint success">
              ✓ Подтверждено — ждём встречи!
            </span>
            <span v-else-if="booking.status === 'pending'" class="hint warning">
              ⏳ Ожидает подтверждения администратора
            </span>
            <span v-else class="hint">
              🔒 Прошедшее событие
            </span>
          </div>
        </div>
      </div>
    </div>
  </app-page>
</template>

<script>
import axios from '@/utils/axios'
import AppPage from '@/components/ui/AppPage'
import AppLoader from '@/components/ui/AppLoader'

export default {
  components: { AppPage, AppLoader },
  data() {
    return {
      loading: true,
      bookings: []
    }
  },
  async mounted() {
    await this.loadBookings()
  },
  methods: {
    async loadBookings() {
      this.loading = true
      try {
        const { data } = await axios.get('/bookings/my_bookings/')
        this.bookings = Array.isArray(data) ? data : (data.results || [])
      } catch (e) {
        console.error('Error loading bookings:', e)
        this.bookings = []
      } finally {
        this.loading = false
      }
    },
    
    formatDate(dateStr) {
      if (!dateStr) return 'Не указано'
      const date = new Date(dateStr)
      return date.toLocaleDateString('ru-RU', { 
        weekday: 'long',
        day: 'numeric', 
        month: 'long', 
        year: 'numeric' 
      })
    },
    
    formatHour(hour) {
      return `${hour.toString().padStart(2, '0')}:00 - ${(hour + 1).toString().padStart(2, '0')}:00`
    },
    
    formatDateTime(dateStr) {
      if (!dateStr) return 'Не указано'
      const date = new Date(dateStr)
      return date.toLocaleString('ru-RU', { 
        day: 'numeric', 
        month: 'short', 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    },
    
    getStatusText(status) {
      const map = { 
        pending: 'Ожидает', 
        confirmed: 'Подтверждено', 
        cancelled: 'Отменено' 
      }
      return map[status] || status
    },
    
    canCancel(booking) {
      if (!['pending', 'confirmed'].includes(booking.status)) {
        return false
      }

      const now = new Date()
      const bookingStart = new Date(`${booking.date}T${booking.hour.toString().padStart(2, '0')}:00`)
      const diffHours = (bookingStart - now) / (1000 * 60 * 60)
      return diffHours >= 2
    },
    
    async cancelBooking(booking) {
      if (!confirm('Отменить это бронирование?')) return
      try {
        await axios.delete(`/bookings/${booking.id}/`)
        await this.loadBookings()
        alert('✅ Бронь отменена')
      } catch (e) {
        const error = e.response?.data?.detail || 'Ошибка при отмене'
        alert('❌ ' + error)
      }
    }
  }
}
</script>

<style scoped>
.bookings-container {
  max-width: 900px;
  margin: 0 auto;
}

.loading {
  text-align: center;
  padding: 3rem;
  background: white;
  border: 2px solid #03a147;
  border-radius: 12px;
}

.empty {
  text-align: center;
  padding: 2rem;
}

.empty-card {
  background: white;
  border: 2px solid #03a147;
  border-radius: 12px;
  padding: 3rem 2rem;
  box-shadow: 0 4px 12px rgba(3, 161, 71, 0.15);
}

.empty-card h3 {
  margin: 0 0 1rem 0;
  color: #03a147;
  font-size: 1.5rem;
}

.empty-card p {
  color: #666;
  margin-bottom: 1.5rem;
}

.bookings-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.booking-card {
  background: white;
  border: 2px solid #03a147;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(3, 161, 71, 0.15);
  transition: all 0.2s;
}

.booking-card:hover {
  box-shadow: 0 6px 20px rgba(3, 161, 71, 0.25);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #03a147;
}

.booking-info h3 {
  margin: 0 0 0.5rem 0;
  color: #03a147;
  font-size: 1.2rem;
}

.booking-date {
  margin: 0;
  color: #666;
  font-size: 0.95rem;
}

.badge {
  padding: 0.4rem 0.8rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  border: 2px solid;
}

.badge.status.pending {
  background: #fff3cd;
  color: #856404;
  border-color: #ffc107;
}

.badge.status.confirmed {
  background: #d4edda;
  color: #155724;
  border-color: #28a745;
}

.badge.status.cancelled {
  background: #f8d7da;
  color: #721c24;
  border-color: #dc3545;
}

.card-body {
  margin-bottom: 1rem;
}

.info-row {
  margin: 0.5rem 0;
  font-size: 0.9rem;
  color: #555;
}

.info-row strong {
  color: #03a147;
  min-width: 100px;
  display: inline-block;
}

.info-row.success {
  color: #155724;
  background: #e8f5e9;
  padding: 0.5rem;
  border-radius: 6px;
  border-left: 3px solid #03a147;
}

.info-row.warning {
  color: #856404;
  background: #fff3cd;
  padding: 0.5rem;
  border-radius: 6px;
  border-left: 3px solid #ffc107;
}

.card-actions {
  padding-top: 1rem;
  border-top: 2px solid #03a147;
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.hint {
  font-size: 0.85rem;
  color: #666;
  font-style: italic;
}

.hint.success {
  color: #155724;
}

.hint.warning {
  color: #856404;
}

.btn {
  padding: 0.6rem 1.2rem;
  border: 2px solid #03a147;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
  display: inline-block;
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

@media (max-width: 768px) {
  .bookings-list {
    grid-template-columns: 1fr;
  }
  
  .booking-card {
    padding: 1rem;
  }
  
  .card-header {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .card-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>
