<!-- /var/www/ttennis/frontend/src/components/ui/Modals/CreationConfirm.vue -->
<template>
  <div class="modal-backdrop1" @click="$emit('close')"></div>
  <div class="modal1">
    <div class="modal-content1" style="text-align: center">
      <h3><strong>Подтверждение бронирования</strong></h3>
      <p>Вы хотите забронировать:</p>
      <p><strong>Дата:</strong> {{ formattedDate }}</p>
      <p><strong>Время:</strong> {{ formattedTime }}</p>
      <p><strong>Стол №:</strong> {{ table }}</p>
      
      <!-- 🔥 Разный текст для админа и пользователя -->
      <div v-if="isAdmin" class="status-note admin">
        <span class="badge primary">✓ Будет подтверждено сразу</span>
        <p class="hint">Как администратор, вы создаёте подтверждённую бронь</p>
      </div>
      <div v-else class="status-note">
        <span class="badge warning">⏳ Ожидает подтверждения</span>
        <p class="hint">Администратор свяжется с вами для подтверждения</p>
      </div>
      
      <div style="margin-top: 20px;">
        <button class="btn primary" @click="$emit('confirm'); $emit('close')">Да, забронировать</button>
        <button class="btn warning" @click="$emit('close')">Отмена</button>
      </div>
    </div>
  </div>
</template>

<script>
import { useStore } from 'vuex'

export default {
  emits: ['close', 'confirm'],
  props: {
    date: String,
    hour: Number,
    table: Number
  },
  setup() {
    const store = useStore()
    return {
      isAdmin: store.getters['auth/username'] === 'admin'
    }
  },
  computed: {
    formattedDate() {
      if (!this.date) return ''
      const d = new Date(this.date)
      return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
    },
    formattedTime() {
      return `${String(this.hour - 1).padStart(2, '0')}:00 - ${String(this.hour).padStart(2, '0')}:00`
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
.status-note { margin: 15px 0; }
.status-note.admin { background: #e8f5e9; padding: 10px; border-radius: 8px; }
.hint { font-size: 0.9rem; color: #666; font-style: italic; margin: 8px 0 0 0; }
.badge { padding: 4px 10px; border-radius: 12px; font-size: 0.85rem; }
.badge.warning { background: #ffc107; color: #000; }
.badge.primary { background: #03a147; color: #fff; }
.btn { margin: 0 5px; }
@media (max-width: 500px) { .modal1 { width: 95%; padding: 1.5rem; } }
</style>
