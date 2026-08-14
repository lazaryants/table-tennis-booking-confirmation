<!-- /var/www/ttennis/frontend/src/App.vue -->
<template>
  <!-- 🔥 Если layout не задан — используем 'main' по умолчанию -->
  <component :is="currentLayout"></component>
</template>

<script>
import { computed } from "vue"
import { useRoute } from "vue-router"
import MainLayout from "@/layout/MainLayout"
import AuthLayout from "@/layout/AuthLayout"

export default {
  components: { MainLayout, AuthLayout },
  setup() {
    // 🔥 Безопасное получение route с проверкой
    const route = useRoute()
    
    // 🔥 Фоллбэк на 'main', если meta.layout не задан
    const currentLayout = computed(() => {
      const layoutName = route?.meta?.layout || 'main'
      return `${layoutName}-layout`
    })
    
    return {
      currentLayout
    }
  }
}
</script>
