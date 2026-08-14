<template>
  <div class="modal-backdrop1" @click="$emit('close')"></div>
  <div class="modal1">
    <div class="modal-content1" style="text-align: center">
      <h3><strong>Удаление бронирования</strong></h3>
      <p>Вы действительно хотите отменить запись?</p>
      <p v-if="booking">
        <strong>{{ booking.date }} | {{ formattedTime }} | Стол №{{ booking.table_number }}</strong>
      </p>
      <div style="margin-top: 20px;">
        <button class="btn danger" @click="$emit('confirm'); $emit('close')">Да, удалить</button>
        <button class="btn warning" @click="$emit('close')">Отмена</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "@/utils/axios"

export default {
  emits: ['close', 'confirm'],
  props: {
    booking: Object
  },
  computed: {
    formattedTime() {
      if (!this.booking?.hour) return ''
      return `${String(this.booking.hour - 1).padStart(2, '0')}:00 - ${String(this.booking.hour).padStart(2, '0')}:00`
    }
  },
  methods: {
    async deleteBooking() {
      if (!this.booking?.id) return
      try {
        await axios.delete(`/bookings/${this.booking.id}/`)
        this.$emit('confirm')
      } catch (e) {
        console.error('Error deleting booking:', e)
      }
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
.btn { margin: 0 5px; }
@media (max-width: 500px) { .modal1 { width: 95%; padding: 1.5rem; } }
</style>
