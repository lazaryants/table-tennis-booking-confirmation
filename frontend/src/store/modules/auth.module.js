import axios from '@/utils/axios'
import router from '@/router'

const TOKEN_KEY = 'jwt-token'
const REFRESH_TOKEN_KEY = 'jwt-refresh-token'

function isTokenExpired(token) {
  if (!token) return true

  try {
    const parts = token.split('.')
    if (parts.length !== 3) return true

    const normalized = parts[1]
      .replace(/-/g, '+')
      .replace(/_/g, '/')

    const padded = normalized.padEnd(
      normalized.length + (4 - normalized.length % 4) % 4,
      '='
    )

    const payload = JSON.parse(atob(padded))

    if (!payload.exp) return true

    return Date.now() >= payload.exp * 1000
  } catch (e) {
    return true
  }
}

export default {
  namespaced: true,

  state() {
    return {
      token: localStorage.getItem(TOKEN_KEY),
      refreshToken: localStorage.getItem(REFRESH_TOKEN_KEY),
      username: localStorage.getItem('username'),
      user: null,
      isAdmin: false
    }
  },

  mutations: {
    SET_TOKEN(state, token) {
      state.token = token

      if (token) {
        localStorage.setItem(TOKEN_KEY, token)
      } else {
        localStorage.removeItem(TOKEN_KEY)
      }
    },

    SET_REFRESH_TOKEN(state, token) {
      state.refreshToken = token

      if (token) {
        localStorage.setItem(REFRESH_TOKEN_KEY, token)
      } else {
        localStorage.removeItem(REFRESH_TOKEN_KEY)
      }
    },

    SET_USERNAME(state, username) {
      state.username = username

      if (username) {
        localStorage.setItem('username', username)
      } else {
        localStorage.removeItem('username')
      }
    },

    SET_USER(state, user) {
      state.user = user
      state.isAdmin =
        user?.is_staff === true ||
        user?.is_superuser === true
    },

    LOGOUT(state) {
      state.token = null
      state.refreshToken = null
      state.username = null
      state.user = null
      state.isAdmin = false

      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(REFRESH_TOKEN_KEY)
      localStorage.removeItem('username')
    }
  },

  actions: {
    async signUp({ commit, dispatch }, payload) {
      try {
        const { data } = await axios.post('/users/', {
          username: payload.username,
          email: payload.email,
          password: payload.password,
          first_name: payload.first_name || '',
          last_name: payload.last_name || '',
          phone: payload.phone || ''
        })

        return {
          success: true,
          data
        }
      } catch (e) {
        const errors = e.response?.data
        let message = 'Ошибка регистрации'

        if (errors?.username) {
          message = 'Такой логин уже занят'
        } else if (errors?.email) {
          message = 'Такой email уже зарегистрирован'
        } else if (errors?.password) {
          message = 'Пароль слишком простой'
        } else if (errors?.detail) {
          message = errors.detail
        }

        return {
          success: false,
          error: message
        }
      }
    },

    async login({ commit, dispatch }, payload) {
      try {
        const { data } = await axios.post('/token/', {
          username: payload.username,
          password: payload.password
        })

        commit('SET_TOKEN', data.access)
        commit('SET_REFRESH_TOKEN', data.refresh)
        commit('SET_USERNAME', payload.username)

        await dispatch('loadProfile')

        return {
          success: true
        }
      } catch (e) {
        return {
          success: false,
          error: 'Неверный логин или пароль'
        }
      }
    },

    async loadProfile({ commit, state }) {
      if (!state.token && !state.refreshToken) {
        return
      }

      try {
        const { data } = await axios.get('/users/me/')

        commit('SET_USER', data)

        return {
          success: true,
          data
        }
      } catch (e) {
        console.error('Error loading profile:', e)

        return {
          success: false
        }
      }
    },

    async updateProfile({ commit, state }, payload) {
      if (!state.token && !state.refreshToken) {
        return
      }

      try {
        const { data } = await axios.patch(
          '/users/update_profile/',
          {
            first_name: payload.first_name,
            last_name: payload.last_name,
            phone: payload.phone,
            email: payload.email
          }
        )

        commit('SET_USER', data)

        return {
          success: true,
          data
        }
      } catch (e) {
        const errors = e.response?.data
        let message = 'Ошибка обновления'

        if (errors?.email) {
          message = 'Такой email уже занят'
        } else if (errors?.detail) {
          message = errors.detail
        }

        return {
          success: false,
          error: message
        }
      }
    },

    logout({ commit }) {
      commit('LOGOUT')
      router.push('/auth')
    }
  },

  getters: {
    isAuthenticated: state =>
      (
        !!state.token &&
        !isTokenExpired(state.token)
      ) ||
      !!state.refreshToken,

    username: state => state.username,
    user: state => state.user,
    token: state => state.token,
    refreshToken: state => state.refreshToken,

    isAdmin: state =>
      state.user?.is_staff === true ||
      state.user?.is_superuser === true,

    isManager: state =>
      state.user?.is_manager === true,

    canManageBookings: state =>
      state.user?.is_staff === true ||
      state.user?.is_superuser === true ||
      state.user?.is_manager === true
  }
}
