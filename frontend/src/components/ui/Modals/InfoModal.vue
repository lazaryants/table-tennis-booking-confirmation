<template>
  <div class="modal-backdrop1" @click="$emit('close')"></div>
  <div class="modal1">
    <div class="modal-content1" style="text-align: center">
      <h3><strong>Стол уже забронирован</strong></h3>
      <div v-if="booking" style="margin: 20px 0; text-align: left;">
        <p><strong>Пользователь:</strong> {{ booking.user_first_name }} {{ booking.user_last_name }}</p>
        <p><strong>Телефон:</strong> {{ booking.user_phone || 'Не указан' }}</p>
        <p><strong>Дата:</strong> {{ booking.date }}</p>
        <p><strong>Время:</strong> {{ formattedTime }}</p>
        <p><strong>Статус:</strong> 
          <span :class="['badge', booking.status === 'confirmed' ? 'primary' : 'warning']">
            {{ statusText }}
          </span>
        </p>
      </div>
      <button class="btn warning" @click="$emit('close')" style="margin-top: 15px;">Закрыть</button>
    </div>
  </div>
</template>

<script>
export default {
  emits: ['close'],
  props: {
    booking: Object
  },
  computed: {
    formattedTime() {
      if (!this.booking?.hour) return ''
      return `${String(this.booking.hour - 1).padStart(2, '0')}:00 - ${String(this.booking.hour).padStart(2, '0')}:00`
    },
    statusText() {
      const map = {
        pending: 'Ожидает подтверждения',
        confirmed: 'Подтверждено',
        cancelled: 'Отменено'
      }
      return map[this.booking?.status] || this.booking?.status
    }
  }
}
</script>

<style scoped>
.modal-backdrop1 {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 1000;
}
.modal1 {
  position: fixed;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 90%; max-width: 400px;
  background: #fff;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
  z-index: 1001;
}
.badge { padding: 4px 10px; border-radius: 12px; font-size: 0.85rem; }
.badge.primary { background: #03a147; color: #fff; }
.badge.warning { background: #ffc107; color: #000; }
.btn { margin-top: 15px; }
@media (max-width: 500px) { .modal1 { width: 95%; padding: 1.5rem; } }
</style>
