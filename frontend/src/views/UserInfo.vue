<template>
  <app-page title="Настройки пользователя">
    <div v-if="loading" class="loading">
      <app-loader></app-loader>
    </div>
    <div v-else class="user-info">
      <div class="info-row">
        <h2>Логин: {{ username || 'Не указан' }}</h2>
      </div>
      <div class="info-row">
        <h2>Имя: {{ firstname || 'Не указано' }}</h2>
      </div>
      <div class="info-row">
        <h2>Фамилия: {{ lastname || 'Не указана' }}</h2>
      </div>
      <div class="info-row">
        <h2>Телефон: {{ phone || 'Не указан' }}</h2>
      </div>
    </div>
  </app-page>
</template>

<script>
import AppPage from "@/components/ui/AppPage";
import AppLoader from "@/components/ui/AppLoader";
import { useStore } from "vuex";
import axios from "@/utils/axios";
import { ref, onMounted } from "vue";

export default {
  setup() {
    const store = useStore();
    const username = ref("");
    const phone = ref("");
    const firstname = ref("");
    const lastname = ref("");
    const loading = ref(true);

    const getUser = async () => {
      try {
        const { data } = await axios.get('/users/', {
          params: {
            username: store.getters["auth/username"],
          },
        });
        const users = Array.isArray(data) ? data : (data.results || []);
        const user = users[0];
        
        if (user) {
          username.value = user.username || '';
          phone.value = user.phone || '';
          firstname.value = user.first_name || '';
          lastname.value = user.last_name || '';
        }
      } catch (error) {
        console.error("Error loading user ", error);
      } finally {
        loading.value = false;
      }
    };

    onMounted(() => {
      getUser();
    });

    return {
      username,
      phone,
      firstname,
      lastname,
      loading,
    };
  },
  components: { AppPage, AppLoader },
};
</script>

<style scoped>
.user-info {
  max-width: 600px;
  margin: 0 auto;
}
.info-row {
  margin-bottom: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.info-row h2 {
  margin: 0;
  font-size: 1.1rem;
  color: #333;
}
.loading {
  text-align: center;
  padding: 40px 0;
}
</style>
