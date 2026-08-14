<template>
  <div class="main-layout">
    <header class="header">
      <div class="header-container">
        <router-link to="/" class="logo">
          <img
            src="/img/table-tennis.svg"
            alt="Table Tennis"
            class="logo-icon"
          >
          <span>Table Tennis</span>
        </router-link>
        
        <!-- 🔥 Бургер кнопка (только мобильные) -->
        <button class="burger-btn" @click="toggleMenu" :class="{active: menuOpen}">
          <span></span>
          <span></span>
          <span></span>
        </button>
        
        <!-- Навигация -->
        <nav class="nav" :class="{open: menuOpen}">
          <router-link to="/" class="nav-link" @click="closeMenu">Главная</router-link>
          <router-link to="/my-bookings" class="nav-link" @click="closeMenu">Мои брони</router-link>
          <router-link to="/profile" class="nav-link" @click="closeMenu">Профиль</router-link>
          <router-link v-if="canManageBookings" to="/panel" class="nav-link admin-link" @click="closeMenu">
            👨‍💼 Управление
          </router-link>
          
          <div class="user-menu-mobile">
            <span class="username">{{ username }}</span>
            <button @click="handleLogout" class="btn-logout">Выйти</button>
          </div>
        </nav>
        
        <!-- Десктопное меню -->
        <div class="user-menu-desktop">
          <span class="username">{{ username }}</span>
          <button @click="handleLogout" class="btn-logout">Выйти</button>
        </div>
      </div>
    </header>
    
    <main class="content">
      <router-view></router-view>
    </main>
    
    <footer class="footer">
      <p>© 2026 Table Tennis. Бронирование столов для настольного тенниса</p>
    </footer>
    
    <!-- Затемнение фона при открытом меню -->
    <div v-if="menuOpen" class="menu-overlay" @click="closeMenu"></div>
  </div>
</template>

<script>
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { computed, ref } from 'vue'

export default {
  setup() {
    const store = useStore()
    const router = useRouter()
    const menuOpen = ref(false)
    
    const username = computed(() => store.getters['auth/username'])
    const canManageBookings = computed(() => store.getters['auth/canManageBookings'])
    
    const toggleMenu = () => {
      menuOpen.value = !menuOpen.value
      document.body.style.overflow = menuOpen.value ? 'hidden' : ''
    }
    
    const closeMenu = () => {
      menuOpen.value = false
      document.body.style.overflow = ''
    }
    
    const handleLogout = () => {
      if (confirm('Вы действительно хотите выйти?')) {
        closeMenu()
        store.commit('auth/LOGOUT')
        router.push('/auth')
      }
    }
    
    return { username, canManageBookings, menuOpen, toggleMenu, closeMenu, handleLogout }
  }
}
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: #03a147;
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  text-decoration: none;
  z-index: 1001;
}

/* 🔥 Бургер кнопка (скрыта на десктопе) */
.burger-btn {
  display: none;
  flex-direction: column;
  gap: 5px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  z-index: 1001;
}

.burger-btn span {
  display: block;
  width: 25px;
  height: 3px;
  background: white;
  border-radius: 2px;
  transition: all 0.3s;
}

.burger-btn.active span:nth-child(1) {
  transform: rotate(45deg) translate(5px, 5px);
}

.burger-btn.active span:nth-child(2) {
  opacity: 0;
}

.burger-btn.active span:nth-child(3) {
  transform: rotate(-45deg) translate(7px, -6px);
}

/* Навигация */
.nav {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: background 0.2s;
  white-space: nowrap;
}

.nav-link:hover {
  background: rgba(255,255,255,0.1);
}

.nav-link.admin-link {
  background: rgba(255,255,255,0.2);
  font-weight: 600;
}

.user-menu-desktop {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.username {
  font-weight: 500;
}

.btn-logout {
  background: rgba(255,255,255,0.2);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
  white-space: nowrap;
}

.btn-logout:hover {
  background: rgba(255,255,255,0.3);
}

/* Мобильное меню */
.user-menu-mobile {
  display: none;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  border-top: 1px solid rgba(255,255,255,0.2);
  margin-top: 1rem;
}

.menu-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 999;
}

.content {
  flex: 1;
  padding: 2rem 1rem;
  background: #f5f5f5;
}

.footer {
  background: #333;
  color: white;
  text-align: center;
  padding: 1rem;
}

/* 🔥 Мобильная адаптация */
@media (max-width: 768px) {
  .burger-btn {
    display: flex;
  }
  
  .user-menu-desktop {
    display: none;
  }
  
  .user-menu-mobile {
    display: flex;
  }
  
  .nav {
    position: fixed;
    top: 0;
    right: -100%;
    width: 280px;
    height: 100vh;
    background: #03a147;
    flex-direction: column;
    align-items: stretch;
    padding: 5rem 1.5rem 1.5rem;
    gap: 0.5rem;
    transition: right 0.3s ease;
    box-shadow: -5px 0 15px rgba(0,0,0,0.2);
  }
  
  .nav.open {
    right: 0;
  }
  
  .nav-link {
    padding: 1rem;
    font-size: 1.1rem;
  }
  
  .menu-overlay {
    display: block;
  }
  
  .header-container {
    padding: 0 1rem;
  }
  
  .logo {
    font-size: 1.3rem;
  }
}

/* 🔥 Очень маленькие экраны */
@media (max-width: 400px) {
  .nav {
    width: 100%;
  }
  
  .logo {
    font-size: 1.2rem;
  }
}

.logo {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
}

.logo-icon {
  width: 34px;
  height: 34px;
  flex-shrink: 0;
}

</style>
