<template>
  <div class="modal-backdrop1" @click="$emit('close')"></div>
  <div class="modal1">
    <div class="modal-content1" style="text-align: center;">
      <h3><strong>{{ message }}</strong></h3>
      <button class="btn warning" @click="$emit('close')" style="margin-top: 15px;">Закрыть</button>
    </div>
  </div>
</template>

<script>
export default {
  emits: ['close'],
  props: {
    message: {
      type: String,
      default: 'Действие невозможно'
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
@media (max-width: 500px) { .modal1 { width: 95%; padding: 1.5rem; } }
</style>
