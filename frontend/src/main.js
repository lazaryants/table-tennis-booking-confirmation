import { createApp } from 'vue'

import App from './App.vue'
import router from './router'
import store from './store'

import 'bootstrap/dist/css/bootstrap.css'
import './theme.css'

import axios from '@/utils/axios'


async function bootstrap() {
  /*
   * Если в браузере осталась действующая сессия,
   * заранее загружаем профиль пользователя.
   *
   * Это необходимо, чтобы роли is_staff / is_manager
   * были известны ещё до первого перехода router.
   *
   * Если access token истёк, axios автоматически
   * обновит его через refresh token.
   */
  const hasAccessToken =
    !!localStorage.getItem('jwt-token')

  const hasRefreshToken =
    !!localStorage.getItem('jwt-refresh-token')

  if (hasAccessToken || hasRefreshToken) {
    try {
      await store.dispatch('auth/loadProfile')
    } catch (error) {
      console.error(
        'Не удалось загрузить профиль при запуске приложения:',
        error
      )
    }
  }

  const app = createApp(App)

  app.config.globalProperties.$axios = axios

  app.use(store)
  app.use(router)

  app.mount('#app')
}


bootstrap()
