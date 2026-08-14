import axios from 'axios'

const TOKEN_KEY = 'jwt-token'
const REFRESH_TOKEN_KEY = 'jwt-refresh-token'

const instance = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true
})


function isTokenExpired(token, reserveSeconds = 10) {
  if (!token) return true

  try {
    const parts = token.split('.')

    if (parts.length !== 3) {
      return true
    }

    const normalized = parts[1]
      .replace(/-/g, '+')
      .replace(/_/g, '/')

    const padded = normalized.padEnd(
      normalized.length + (4 - normalized.length % 4) % 4,
      '='
    )

    const payload = JSON.parse(atob(padded))

    if (!payload.exp) {
      return true
    }

    return Date.now() >= (payload.exp - reserveSeconds) * 1000
  } catch (e) {
    return true
  }
}


const getCsrfToken = () => {
  const name = 'csrftoken='
  const decodedCookie = decodeURIComponent(document.cookie)
  const cookies = decodedCookie.split(';')

  for (let cookie of cookies) {
    cookie = cookie.trim()

    if (cookie.indexOf(name) === 0) {
      return cookie.substring(name.length)
    }
  }

  return null
}


let refreshPromise = null


async function refreshAccessToken() {
  if (refreshPromise) {
    return refreshPromise
  }

  const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)

  if (!refreshToken) {
    throw new Error('Refresh token is missing')
  }

  refreshPromise = axios
    .post(
      '/api/token/refresh/',
      {
        refresh: refreshToken
      },
      {
        headers: {
          'Content-Type': 'application/json'
        }
      }
    )
    .then(response => {
      const newAccess = response.data?.access

      if (!newAccess) {
        throw new Error('Refresh response contains no access token')
      }

      localStorage.setItem(TOKEN_KEY, newAccess)

      // Сейчас ROTATE_REFRESH_TOKENS=False,
      // но оставляем поддержку на будущее.
      if (response.data?.refresh) {
        localStorage.setItem(
          REFRESH_TOKEN_KEY,
          response.data.refresh
        )
      }

      return newAccess
    })
    .finally(() => {
      refreshPromise = null
    })

  return refreshPromise
}


function clearSession() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem('username')
}


function redirectToLogin() {
  if (window.location.pathname !== '/auth') {
    window.location.href = '/auth?message=session_expired'
  }
}


instance.interceptors.request.use(
  async config => {
    let accessToken = localStorage.getItem(TOKEN_KEY)
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)

    // Для обычного API-запроса заранее обновляем access,
    // если он уже истёк или истечёт через несколько секунд.
    if (
      accessToken &&
      isTokenExpired(accessToken) &&
      refreshToken
    ) {
      try {
        accessToken = await refreshAccessToken()
      } catch (error) {
        clearSession()
        redirectToLogin()
        return Promise.reject(error)
      }
    }

    if (accessToken && !isTokenExpired(accessToken, 0)) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }

    const csrfToken = getCsrfToken()

    if (
      csrfToken &&
      ['post', 'put', 'patch', 'delete'].includes(
        config.method?.toLowerCase()
      )
    ) {
      config.headers['X-CSRFToken'] = csrfToken
    }

    return config
  },
  error => Promise.reject(error)
)


instance.interceptors.response.use(
  response => response,

  async error => {
    const originalRequest = error.config

    // Страховочный вариант:
    // если access был отвергнут сервером раньше,
    // чем frontend успел его обновить.
    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('/token/')
    ) {
      originalRequest._retry = true

      try {
        const newAccess = await refreshAccessToken()

        originalRequest.headers =
          originalRequest.headers || {}

        originalRequest.headers.Authorization =
          `Bearer ${newAccess}`

        return instance(originalRequest)
      } catch (refreshError) {
        clearSession()
        redirectToLogin()

        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)


export default instance
