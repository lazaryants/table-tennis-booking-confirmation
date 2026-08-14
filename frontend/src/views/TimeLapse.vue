<template>
  <app-page title="Список столов">
    <form @submit.prevent="chooseDate" style="padding-bottom: 10px;">
      <div style="display:flex; margin: 0 -5px;" class="box">
        <h2 class="item">Выберите дату:</h2>
      </div>
      <div style="display:flex; margin: 0 -5px;" class="box">
        <input type="date" id="date" v-model="date" class="item" :min="today">
        <button class="btn primary item" type="submit">Выбрать</button>
      </div>
    </form>

    <div class="table-container" v-if="date && Array.isArray(bookingsToday)">
      <table class="table table-bordered booking-table">
        <thead>
          <tr>
            <th scope="col" class="time-col">Время</th>
            <th v-for="table in 5" :key="table" scope="col" class="table-col">
              Стол {{ table }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="hour in hours" :key="hour">
            <td class="time-cell">{{ formatHour(hour) }}</td>
            <!-- 🔥 Desktop: hover + click, Mobile: только click -->
            <td 
              v-for="table in 5" 
              :key="table" 
              class="table-cell"
              :class="getCellClass(hour, table)"
              @click="handleCellClick(hour, table)"
              @mouseenter="!isMobile ? showTooltip($event, getBooking(hour, table)) : null"
              @mouseleave="!isMobile ? hideTooltip() : null"
            >
              <span v-if="getBooking(hour, table)" class="booking-name">
                {{ getBooking(hour, table).user_first_name || getBooking(hour, table).user_name }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <div v-else-if="date" class="text-center" style="padding: 20px; color: #666;">
      Загрузка броней...
    </div>

    <!-- 🔥 Tooltip ТОЛЬКО для desktop -->
    <div v-if="tooltip.visible && !isMobile" class="booking-tooltip" :style="tooltip.style">
      <div class="tooltip-header">
        <strong>{{ tooltip.booking?.user_first_name }} {{ tooltip.booking?.user_last_name }}</strong>
        <span :class="['badge', 'status', tooltip.booking?.status]">
          {{ getStatusText(tooltip.booking?.status) }}
        </span>
      </div>
      <div class="tooltip-body">
        <p><strong>Дата:</strong> {{ formatDate(tooltip.booking?.date) }}</p>
        <p><strong>Время:</strong> {{ formatHour(tooltip.booking?.hour) }}</p>
        <p><strong>Стол:</strong> №{{ tooltip.booking?.table_number }}</p>
        <p v-if="isAdmin"><strong>Телефон:</strong> {{ tooltip.booking?.user_phone || 'Не указан' }}</p>
        <p><strong>Создано:</strong> {{ formatDateTime(tooltip.booking?.created_at) }}</p>
      </div>
      <div class="tooltip-hint">
        <small>ℹ️ Нажмите для действий</small>
      </div>
    </div>

    <!-- Модалка: Информация о брони (клик) -->
    <teleport to="body">
      <div v-if="showInfoModal" class="modal-backdrop" @click="closeInfoModal">
        <div class="modal-content" @click.stop>
          <h3>📋 Информация о брони</h3>
          <div class="info-row"><strong>Дата:</strong> {{ formatDate(selectedBooking?.date) }}</div>
          <div class="info-row"><strong>Время:</strong> {{ formatHour(selectedBooking?.hour) }}</div>
          <div class="info-row"><strong>Стол:</strong> №{{ selectedBooking?.table_number }}</div>
          <div class="info-row">
            <strong>Пользователь:</strong> 
            {{ selectedBooking?.user_first_name && selectedBooking?.user_last_name 
                ? `${selectedBooking.user_first_name} ${selectedBooking.user_last_name}` 
                : selectedBooking?.user_name || 'Не указано' }}
          </div>
          <div v-if="isAdmin" class="info-row">
            <strong>Телефон:</strong> {{ selectedBooking?.user_phone || 'Не указан' }}
          </div>
          <div class="info-row">
            <strong>Статус:</strong> 
            <span :class="['badge', 'status', selectedBooking?.status]">
              {{ getStatusText(selectedBooking?.status) }}
            </span>
          </div>
          <div class="info-row"><strong>Создано:</strong> {{ formatDateTime(selectedBooking?.created_at) }}</div>
          <div class="modal-actions">
            <template v-if="isAdmin">
              <button v-if="selectedBooking?.status === 'pending'" class="btn primary" @click="openConfirmModal">✓ Подтвердить</button>
              <button v-if="selectedBooking?.status === 'pending'" class="btn danger" @click="openRejectModal">✗ Отклонить</button>
              <button v-if="selectedBooking?.status === 'confirmed'" class="btn warning" @click="openCancelAdminModal">🗑️ Отменить</button>
            </template>
            <button class="btn" @click="closeInfoModal">Закрыть</button>
          </div>
        </div>
      </div>
    </teleport>

    <!-- Модалки: Подтверждение/Отклонение/Отмена (админ) -->
    <teleport to="body">
      <div v-if="showConfirmModal" class="modal-backdrop" @click="closeConfirmModal">
        <div class="modal-content small" @click.stop>
          <h3>⚠️ Подтвердить бронь?</h3>
          <p><strong>Пользователь:</strong> {{ selectedBooking?.user_first_name }} {{ selectedBooking?.user_last_name }}</p>
          <p><strong>Дата:</strong> {{ formatDate(selectedBooking?.date) }}</p>
          <p><strong>Время:</strong> {{ formatHour(selectedBooking?.hour) }}</p>
          <p><strong>Стол:</strong> №{{ selectedBooking?.table_number }}</p>
          <div class="modal-actions">
            <button class="btn primary" @click="confirmBooking">✓ Да, подтвердить</button>
            <button class="btn" @click="closeConfirmModal">Отмена</button>
          </div>
        </div>
      </div>
    </teleport>

    <teleport to="body">
      <div v-if="showRejectModal" class="modal-backdrop" @click="closeRejectModal">
        <div class="modal-content small" @click.stop>
          <h3>⚠️ Отклонить бронь?</h3>
          <p><strong>Пользователь:</strong> {{ selectedBooking?.user_first_name }} {{ selectedBooking?.user_last_name }}</p>
          <p><strong>Дата:</strong> {{ formatDate(selectedBooking?.date) }}</p>
          <p><strong>Время:</strong> {{ formatHour(selectedBooking?.hour) }}</p>
          <p><strong>Стол:</strong> №{{ selectedBooking?.table_number }}</p>
          <p class="warning">Бронь будет удалена</p>
          <div class="modal-actions">
            <button class="btn danger" @click="rejectBooking">✗ Да, отклонить</button>
            <button class="btn" @click="closeRejectModal">Отмена</button>
          </div>
        </div>
      </div>
    </teleport>

    <teleport to="body">
      <div v-if="showCancelAdminModal" class="modal-backdrop" @click="closeCancelAdminModal">
        <div class="modal-content small" @click.stop>
          <h3>⚠️ Отменить подтверждённую бронь?</h3>
          <p><strong>Пользователь:</strong> {{ selectedBooking?.user_first_name }} {{ selectedBooking?.user_last_name }}</p>
          <p><strong>Дата:</strong> {{ formatDate(selectedBooking?.date) }}</p>
          <p><strong>Время:</strong> {{ formatHour(selectedBooking?.hour) }}</p>
          <p><strong>Стол:</strong> №{{ selectedBooking?.table_number }}</p>
          <p class="warning">Бронь будет удалена</p>
          <div class="modal-actions">
            <button class="btn danger" @click="cancelAdminBooking">🗑️ Да, отменить</button>
            <button class="btn" @click="closeCancelAdminModal">Отмена</button>
          </div>
        </div>
      </div>
    </teleport>

    <!-- Модалка: Создание брони (пользователь) -->
    <teleport to="body">
      <div v-if="showCreationConfirm" class="modal-backdrop" @click="closeCreationConfirm">
        <div class="modal-content small" @click.stop>
          <h3>Подтверждение бронирования</h3>
          <p>Вы хотите забронировать:</p>
          <p><strong>Дата:</strong> {{ formatDate(date) }}</p>
          <p><strong>Время:</strong> {{ formatHour(selectedHour) }}</p>
          <p><strong>Стол №:</strong> {{ selectedTable }}</p>
          <div v-if="isAdmin" class="status-note admin">
            <span class="badge primary">✓ Будет подтверждено сразу</span>
            <p class="hint">Как администратор, вы создаёте подтверждённую бронь</p>
          </div>
          <div v-else class="status-note">
            <span class="badge warning">⏳ Ожидает подтверждения</span>
            <p class="hint">Администратор свяжется с вами для подтверждения</p>
          </div>
          <div class="modal-actions">
            <button class="btn primary" @click="confirmCreate">Да, забронировать</button>
            <button class="btn" @click="closeCreationConfirm">Отмена</button>
          </div>
        </div>
      </div>
    </teleport>

    <!-- Модалка: Удаление своей брони (пользователь) -->
    <teleport to="body">
      <div v-if="showDeleteConfirm" class="modal-backdrop" @click="closeDeleteConfirm">
        <div class="modal-content small" @click.stop>
          <h3>⚠️ Отменить свою бронь?</h3>
          <p><strong>Дата:</strong> {{ formatDate(selectedBooking?.date) }}</p>
          <p><strong>Время:</strong> {{ formatHour(selectedBooking?.hour) }}</p>
          <p><strong>Стол:</strong> №{{ selectedBooking?.table_number }}</p>
          <p class="warning">Бронь будет удалена</p>
          <div class="modal-actions">
            <button class="btn danger" @click="confirmDelete">🗑️ Да, отменить</button>
            <button class="btn" @click="closeDeleteConfirm">Отмена</button>
          </div>
        </div>
      </div>
    </teleport>

    <!-- Модалка: Сообщение об ошибке -->
    <teleport to="body">
      <div v-if="showCreateModal" class="modal-backdrop" @click="closeCreateModal">
        <div class="modal-content small" @click.stop>
          <h3>⚠️ {{ createModalMessage }}</h3>
          <button class="btn" @click="closeCreateModal">Закрыть</button>
        </div>
      </div>
    </teleport>
  </app-page>
</template>

<script>
import AppPage from "@/components/ui/AppPage"
import axios from "@/utils/axios"
import { ref, computed, onMounted, onUnmounted } from "vue"
import { useStore } from "vuex"

export default {
  name: 'TimeLapse',
  components: { AppPage },
  setup() {
    const store = useStore()
    const date = ref(null)
    const bookings = ref([])
    const bookingsToday = ref([])
    const today = computed(() => {
      const d = new Date()
      return d.toISOString().split('T')[0]
    })
    const hours = Array.from({ length: 16 }, (_, i) => i + 8)
    
    const isAdmin = computed(() => {
      const username = store.getters['auth/username']
      const user = store.getters['auth/user']
      return username === 'admin' || user?.is_staff === true || user?.is_manager === true
    })
    
    // 🔥 Определение мобильного устройства
    const isMobile = ref(false)
    
    const checkMobile = () => {
      isMobile.value = window.innerWidth < 768 || 'ontouchstart' in window
    }
    
    onMounted(() => {
      checkMobile()
      window.addEventListener('resize', checkMobile)
    })
    
    onUnmounted(() => {
      window.removeEventListener('resize', checkMobile)
    })
    
    const showInfoModal = ref(false)
    const showConfirmModal = ref(false)
    const showRejectModal = ref(false)
    const showCancelAdminModal = ref(false)
    const showCreationConfirm = ref(false)
    const showDeleteConfirm = ref(false)
    const showCreateModal = ref(false)
    
    const createModalMessage = ref('')
    const selectedBooking = ref(null)
    const selectedHour = ref(null)
    const selectedTable = ref(null)
    
    const tooltip = ref({ visible: false, booking: null, style: { top: '0px', left: '0px' } })
    
    const fetchBookings = async () => {
      try {
        const { data } = await axios.get('/bookings/')
        const results = Array.isArray(data) ? data : (data.results || [])
        bookings.value = results
      } catch (e) {
        console.error('Error fetching bookings:', e)
        bookings.value = []
      }
    }
    
    const fetchBookingsByDate = async (dateValue) => {
      try {
        const { data } = await axios.get('/bookings/', { params: { date: dateValue } })
        const results = Array.isArray(data) ? data : (data.results || [])
        bookingsToday.value = results
      } catch (e) {
        console.error('Error fetching bookings by date:', e)
        bookingsToday.value = []
      }
    }
    
    const chooseDate = async () => {
      if (!date.value) return
      await fetchBookingsByDate(date.value)
    }
    
    const formatHour = (hour) => {
      if (!hour) return ''
      return `${hour.toString().padStart(2, '0')}:00 - ${(hour + 1).toString().padStart(2, '0')}:00`
    }
    
    const formatDate = (dateStr) => {
      if (!dateStr) return 'Не указано'
      const d = new Date(dateStr)
      return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
    }
    
    const formatDateTime = (dateStr) => {
      if (!dateStr) return 'Не указано'
      const d = new Date(dateStr)
      return d.toLocaleString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
    }
    
    const getStatusText = (status) => {
      const map = { pending: 'Ожидает подтверждения', confirmed: 'Подтверждено', cancelled: 'Отменено' }
      return map[status] || status
    }
    
    const getBooking = (hour, table) => {
      if (!Array.isArray(bookingsToday.value)) return null
      return bookingsToday.value.find(b => 
        b && b.hour === hour && b.table_number === table && b.status !== 'cancelled'
      ) || null
    }
    
    const getCellClass = (hour, table) => {
      const booking = getBooking(hour, table)
      if (!booking) return ''
      if (booking.status === 'pending') return 'status-pending'
      if (booking.status === 'confirmed') return 'status-confirmed'
      return ''
    }
    
    const isPastSlot = (hour) => {
      const now = new Date()
      const selectedDate = new Date(date.value)
      selectedDate.setHours(0, 0, 0, 0)
      const todayDate = new Date()
      todayDate.setHours(0, 0, 0, 0)
      if (selectedDate < todayDate) return true
      if (selectedDate.getTime() === todayDate.getTime()) {
        return hour <= now.getHours()
      }
      return false
    }
    
    const canDeleteBooking = (booking) => {
      if (!booking?.date || !booking?.hour) return false
      const bookingStart = new Date(`${booking.date}T${booking.hour.toString().padStart(2, '0')}:00`)
      const now = new Date()
      const diffHours = (bookingStart - now) / (1000 * 60 * 60)
      return diffHours >= 2
    }
    
    const handleCellClick = async (hour, table) => {
      const booking = getBooking(hour, table)
      const currentUser = store.getters['auth/username']
      
      if (booking) {
        if (booking.user_name === currentUser) {
          if (isPastSlot(hour)) {
            createModalMessage.value = 'Нельзя удалить бронь на прошедшее время'
            showCreateModal.value = true
          } else if (!canDeleteBooking(booking)) {
            createModalMessage.value = 'Можно удалить бронь не позже чем за 2 часа до начала'
            showCreateModal.value = true
          } else {
            selectedBooking.value = booking
            showDeleteConfirm.value = true
          }
        } else {
          selectedBooking.value = booking
          showInfoModal.value = true
        }
      } else {
        if (isPastSlot(hour)) {
          createModalMessage.value = 'Нельзя создать бронь на прошедшее время'
          showCreateModal.value = true
        } else {
          selectedHour.value = hour
          selectedTable.value = table
          showCreationConfirm.value = true
        }
      }
    }
    
    const closeInfoModal = () => { showInfoModal.value = false; selectedBooking.value = null }
    const closeConfirmModal = () => { showConfirmModal.value = false }
    const closeRejectModal = () => { showRejectModal.value = false }
    const closeCancelAdminModal = () => { showCancelAdminModal.value = false }
    const closeCreationConfirm = () => { showCreationConfirm.value = false }
    const closeDeleteConfirm = () => { showDeleteConfirm.value = false }
    const closeCreateModal = () => { showCreateModal.value = false }
    
    const openConfirmModal = () => { showConfirmModal.value = true; showInfoModal.value = false }
    const openRejectModal = () => { showRejectModal.value = true; showInfoModal.value = false }
    const openCancelAdminModal = () => { showCancelAdminModal.value = true; showInfoModal.value = false }
    
    const confirmBooking = async () => {
      if (!selectedBooking.value?.id) return
      try {
        await axios.post(`/bookings/${selectedBooking.value.id}/confirm/`)
        await fetchBookings()
        await fetchBookingsByDate(date.value)
        closeConfirmModal()
        alert('Бронь подтверждена')
      } catch (e) {
        console.error('Error confirming booking:', e)
        createModalMessage.value = e.response?.data?.detail || 'Ошибка при подтверждении'
        showCreateModal.value = true
      }
    }
    
    const rejectBooking = async () => {
      if (!selectedBooking.value?.id) return
      try {
        await axios.post(`/bookings/${selectedBooking.value.id}/reject/`)
        await fetchBookings()
        await fetchBookingsByDate(date.value)
        closeRejectModal()
        alert('Бронь отклонена')
      } catch (e) {
        console.error('Error rejecting booking:', e)
        createModalMessage.value = e.response?.data?.detail || 'Ошибка при отклонении'
        showCreateModal.value = true
      }
    }
    
    const cancelAdminBooking = async () => {
      if (!selectedBooking.value?.id) return
      try {
        await axios.delete(`/bookings/${selectedBooking.value.id}/`)
        await fetchBookings()
        await fetchBookingsByDate(date.value)
        closeCancelAdminModal()
        alert('Бронь отменена')
      } catch (e) {
        console.error('Error cancelling booking:', e)
        createModalMessage.value = e.response?.data?.detail || 'Ошибка при отмене'
        showCreateModal.value = true
      }
    }
    
    const confirmCreate = async () => {
      try {
        await axios.post('/bookings/', {
          date: date.value,
          hour: selectedHour.value,
          table_number: selectedTable.value
        })
        await fetchBookings()
        await fetchBookingsByDate(date.value)
        closeCreationConfirm()
      } catch (e) {
        console.error('❌ Ошибка создания брони:', e)
        let errorMsg = 'Ошибка при создании брони'
        if (e.response?.data) {
          const errors = e.response.data
          if (errors.non_field_errors) {
            errorMsg = Array.isArray(errors.non_field_errors) 
              ? errors.non_field_errors.join('; ') 
              : errors.non_field_errors
          } else if (typeof errors === 'object' && !Array.isArray(errors)) {
            errorMsg = Object.entries(errors)
              .map(([field, messages]) => {
                const fieldName = { date: 'Дата', hour: 'Время', table_number: 'Номер стола', user: 'Пользователь' }[field] || field
                return `${fieldName}: ${Array.isArray(messages) ? messages.join(', ') : messages}`
              })
              .join('; ')
          } else if (errors.detail) {
            errorMsg = errors.detail
          } else if (Array.isArray(errors)) {
            errorMsg = errors.join('; ')
          } else {
            errorMsg = JSON.stringify(errors)
          }
        } else if (e.message) {
          errorMsg = e.message
        }
        console.error('📋 Детали ошибки:', e.response?.data, e.response?.status)
        createModalMessage.value = errorMsg
        showCreateModal.value = true
      }
    }
    
    const confirmDelete = async () => {
      if (!selectedBooking.value?.id) return
      try {
        await axios.delete(`/bookings/${selectedBooking.value.id}/`)
        await fetchBookings()
        await fetchBookingsByDate(date.value)
        closeDeleteConfirm()
        alert('Бронь отменена')
      } catch (e) {
        console.error('Error deleting booking:', e)
        createModalMessage.value = e.response?.data?.detail || 'Ошибка при удалении'
        showCreateModal.value = true
      }
    }
    
    const showTooltip = (event, booking) => {
      if (!booking) return
      const offset = 12
      const tooltipWidth = 300
      const tooltipHeight = 200
      let left = event.pageX + offset
      let top = event.pageY + offset
      if (left + tooltipWidth > window.innerWidth) left = event.pageX - tooltipWidth - offset
      if (top + tooltipHeight > window.innerHeight) top = window.innerHeight - tooltipHeight - offset
      tooltip.value = { visible: true, booking, style: { top: `${top}px`, left: `${left}px` } }
    }
    
    const hideTooltip = () => { tooltip.value.visible = false }
    
    onMounted(async () => {
      checkMobile()
      window.addEventListener('resize', checkMobile)
      await fetchBookings()
      if (!date.value) {
        date.value = today.value
        await fetchBookingsByDate(date.value)
      }
    })
    
    onUnmounted(() => {
      window.removeEventListener('resize', checkMobile)
    })
    
    return {
      date, bookingsToday, today, hours, formatHour, formatDate, formatDateTime, getStatusText,
      getBooking, getCellClass, handleCellClick, chooseDate, isAdmin, isMobile,
      showInfoModal, showConfirmModal, showRejectModal, showCancelAdminModal,
      showCreationConfirm, showDeleteConfirm, showCreateModal,
      closeInfoModal, closeConfirmModal, closeRejectModal, closeCancelAdminModal,
      closeCreationConfirm, closeDeleteConfirm, closeCreateModal,
      openConfirmModal, openRejectModal, openCancelAdminModal,
      createModalMessage, selectedBooking, selectedHour, selectedTable,
      confirmCreate, confirmDelete, confirmBooking, rejectBooking, cancelAdminBooking,
      tooltip, showTooltip, hideTooltip
    }
  }
}
</script>

<style scoped>
.table-container { overflow-x: auto; -webkit-overflow-scrolling: touch; margin-top: 10px; }
.booking-table { table-layout: fixed; width: 100%; font-size: 0.85rem; border-collapse: collapse; }
.time-col { width: 110px; min-width: 110px; background: #03a147; color: white; font-weight: 600; text-align: center; vertical-align: middle; padding: 8px 4px; border: 2px solid #03a147; }
.table-col { width: 16%; min-width: 90px; text-align: center; border: 2px solid #03a147; }
.time-cell { height: 36px; min-height: 36px; cursor: default; text-align: center; vertical-align: middle; padding: 2px 4px; border: 2px solid #03a147; background: #f8f9fa; font-weight: 600; color: #03a147; }
.table-cell { height: 36px; min-height: 36px; cursor: pointer; transition: background-color 0.15s; position: relative; overflow: hidden; text-align: center; vertical-align: middle; padding: 2px 4px; border: 2px solid #03a147; }
.table-cell:hover { background-color: rgba(3, 161, 71, 0.15); }
.table-cell.status-pending { background-color: #fff3cd !important; border-left: 3px solid #ffc107; }
.table-cell.status-confirmed { background-color: #d4edda !important; border-left: 3px solid #28a745; }
.table-cell.status-cancelled { background-color: #f8d7da !important; border-left: 3px solid #dc3545; }
.booking-name { display: block; font-size: 0.8rem; font-weight: 500; color: #333; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.2; }
.booking-tooltip { position: fixed; background: white; border: 2px solid #03a147; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.2); padding: 12px 16px; min-width: 260px; max-width: 300px; z-index: 10000; font-size: 0.85rem; pointer-events: none; }
.tooltip-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; padding-bottom: 8px; border-bottom: 2px solid #03a147; }
.tooltip-header strong { font-size: 0.95rem; color: #333; }
.tooltip-body p { margin: 4px 0; color: #555; }
.tooltip-body p strong { color: #03a147; min-width: 65px; display: inline-block; }
.tooltip-hint { margin-top: 8px; padding-top: 8px; border-top: 1px solid #eee; text-align: center; color: #999; font-size: 0.8rem; }
.badge.status { padding: 3px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: 600; }
.badge.status.pending { background: #ffc107; color: #000; }
.badge.status.confirmed { background: #28a745; color: white; }
.badge.status.cancelled { background: #dc3545; color: white; }
.box { display: flex; }
.item { margin: 0 5px; }
.text-center { text-align: center; }
.modal-backdrop { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 9999; display: flex; align-items: center; justify-content: center; padding: 1rem; }
.modal-content { background: white; border: 2px solid #03a147; border-radius: 12px; padding: 1.5rem; max-width: 500px; width: 100%; max-height: 90vh; overflow-y: auto; box-shadow: 0 10px 40px rgba(3, 161, 71, 0.2); }
.modal-content.small { max-width: 400px; }
.modal-content h3 { margin: 0 0 1rem 0; color: #03a147; }
.info-row { margin: 0.5rem 0; font-size: 0.9rem; }
.info-row strong { color: #03a147; min-width: 100px; display: inline-block; }
.status-note { margin: 1rem 0; padding: 0.75rem; border-radius: 8px; }
.status-note.admin { background: #e8f5e9; color: #155724; }
.hint { font-size: 0.8rem; color: #666; margin: 0.25rem 0 0 0; font-style: italic; }
.warning { background: #ffebee; color: #c62828; padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0; font-size: 0.85rem; border: 1px solid #e53935; }
.modal-actions { display: flex; gap: 1rem; margin-top: 1.5rem; flex-wrap: wrap; }
.btn { padding: 0.5rem 1rem; border: 2px solid #03a147; border-radius: 6px; font-size: 0.9rem; font-weight: 500; cursor: pointer; transition: all 0.2s; background: white; color: #03a147; }
.btn.primary { background: #03a147; color: white; }
.btn.warning { background: #ffc107; color: #000; border-color: #ffc107; }
.btn.danger { background: #e53935; color: white; border-color: #e53935; }
@media (max-width: 768px) {
  .booking-table { font-size: 0.75rem; }
  .time-col { width: 85px; min-width: 85px; padding: 6px 2px; }
  .time-cell, .table-cell { height: 32px; min-height: 32px; }
  .booking-name { font-size: 0.75rem; }
  .booking-tooltip { display: none !important; }
  .modal-content { padding: 1rem; }
  .modal-actions { flex-direction: column; }
  .modal-actions .btn { width: 100%; }
}
</style>
