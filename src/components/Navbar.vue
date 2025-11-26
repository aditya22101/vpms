<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
    <div class="container-fluid">
      <router-link class="navbar-brand d-flex align-items-center" to="/">
        <i class="bi bi-p-square-fill me-2 fs-4"></i>
        <span class="fw-bold">VPMS</span>
      </router-link>
      
      <button 
        class="navbar-toggler" 
        type="button" 
        data-bs-toggle="collapse" 
        data-bs-target="#navbarNav"
        aria-controls="navbarNav" 
        aria-expanded="false" 
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto">
          <li class="nav-item" v-if="authStore.isAdmin">
            <router-link class="nav-link" to="/admin">
              <i class="bi bi-speedometer2 me-1"></i>Dashboard
            </router-link>
          </li>
          <li class="nav-item" v-if="authStore.isAdmin">
            <router-link class="nav-link" to="/admin/parking-lots">
              <i class="bi bi-building me-1"></i>Parking Lots
            </router-link>
          </li>
          <li class="nav-item" v-if="authStore.isAdmin">
            <router-link class="nav-link" to="/admin/users">
              <i class="bi bi-people me-1"></i>Users
            </router-link>
          </li>
          <li class="nav-item" v-if="!authStore.isAdmin">
            <router-link class="nav-link" to="/user">
              <i class="bi bi-speedometer2 me-1"></i>Dashboard
            </router-link>
          </li>
          <li class="nav-item" v-if="!authStore.isAdmin">
            <router-link class="nav-link" to="/user/book-parking">
              <i class="bi bi-plus-circle me-1"></i>Book Parking
            </router-link>
          </li>
          <li class="nav-item" v-if="!authStore.isAdmin">
            <router-link class="nav-link" to="/user/my-bookings">
              <i class="bi bi-calendar-check me-1"></i>My Bookings
            </router-link>
          </li>
        </ul>
        
        <ul class="navbar-nav">
          <li class="nav-item dropdown">
            <a 
              class="nav-link dropdown-toggle" 
              href="#" 
              id="navbarDropdown" 
              role="button" 
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              <i class="bi bi-person-circle me-1"></i>
              {{ authStore.user?.username || 'User' }}
            </a>
            <ul class="dropdown-menu dropdown-menu-end">
              <li>
                <a class="dropdown-item" href="#" @click.prevent="handleLogout">
                  <i class="bi bi-box-arrow-right me-2"></i>Logout
                </a>
              </li>
            </ul>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

onMounted(() => {
  authStore.loadUser()
})

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.navbar-brand {
  font-size: 1.5rem;
}

.nav-link {
  transition: all 0.3s ease;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 5px;
}

.nav-link.router-link-active {
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 5px;
}
</style>

