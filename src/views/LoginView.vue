<template>
  <div class="login-container">
    <div class="container">
      <div class="row justify-content-center align-items-center min-vh-100">
        <div class="col-md-5 col-lg-4">
          <div class="card shadow-lg border-0">
            <div class="card-body p-5">
              <div class="text-center mb-4">
                <i class="bi bi-p-square-fill text-primary" style="font-size: 3rem;"></i>
                <h2 class="mt-3 mb-1 fw-bold">VPMS</h2>
                <p class="text-muted">Vehicle Parking Management System</p>
              </div>

              <div class="mb-4">
                <ul class="nav nav-pills nav-fill" role="tablist">
                  <li class="nav-item" role="presentation">
                    <button 
                      class="nav-link" 
                      :class="{ active: !isAdminLogin }"
                      @click="isAdminLogin = false"
                      type="button"
                    >
                      <i class="bi bi-person me-2"></i>User Login
                    </button>
                  </li>
                  <li class="nav-item" role="presentation">
                    <button 
                      class="nav-link" 
                      :class="{ active: isAdminLogin }"
                      @click="isAdminLogin = true"
                      type="button"
                    >
                      <i class="bi bi-shield-lock me-2"></i>Admin Login
                    </button>
                  </li>
                </ul>
              </div>

              <form @submit.prevent="handleLogin" novalidate>
                <div class="mb-3">
                  <label for="username" class="form-label">
                    <i class="bi bi-person me-1"></i>Username
                  </label>
                  <input
                    type="text"
                    class="form-control"
                    :class="{ 'is-invalid': errors.username }"
                    id="username"
                    v-model="form.username"
                    required
                    autocomplete="username"
                  />
                  <div class="invalid-feedback" v-if="errors.username">
                    {{ errors.username }}
                  </div>
                </div>

                <div class="mb-3">
                  <label for="password" class="form-label">
                    <i class="bi bi-lock me-1"></i>Password
                  </label>
                  <input
                    type="password"
                    class="form-control"
                    :class="{ 'is-invalid': errors.password }"
                    id="password"
                    v-model="form.password"
                    required
                    autocomplete="current-password"
                  />
                  <div class="invalid-feedback" v-if="errors.password">
                    {{ errors.password }}
                  </div>
                </div>

                <div class="alert alert-danger" v-if="errorMessage" role="alert">
                  <i class="bi bi-exclamation-triangle me-2"></i>{{ errorMessage }}
                </div>

                <button 
                  type="submit" 
                  class="btn btn-primary w-100 mb-3"
                  :disabled="loading"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-box-arrow-in-right me-2"></i>
                  {{ loading ? 'Logging in...' : 'Login' }}
                </button>
              </form>

              <div class="text-center" v-if="!isAdminLogin">
                <p class="mb-0">
                  Don't have an account? 
                  <router-link to="/register" class="text-primary text-decoration-none">
                    Register here
                  </router-link>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isAdminLogin = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const errors = reactive({
  username: '',
  password: ''
})

const form = reactive({
  username: '',
  password: ''
})

const validateForm = () => {
  errors.username = ''
  errors.password = ''
  let isValid = true

  if (!form.username.trim()) {
    errors.username = 'Username is required'
    isValid = false
  }

  if (!form.password) {
    errors.password = 'Password is required'
    isValid = false
  }

  return isValid
}

const handleLogin = async () => {
  errorMessage.value = ''
  
  if (!validateForm()) {
    return
  }

  loading.value = true

  try {
    const result = await authStore.login(
      form.username,
      form.password,
      isAdminLogin.value
    )

    if (result.success) {
      if (isAdminLogin.value) {
        router.push('/admin')
      } else {
        router.push('/user')
      }
    } else {
      errorMessage.value = result.message || 'Login failed. Please try again.'
    }
  } catch (error: any) {
    errorMessage.value = 'An error occurred. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.card {
  border-radius: 15px;
  backdrop-filter: blur(10px);
}

.nav-pills .nav-link {
  color: #495057;
  border-radius: 10px;
}

.nav-pills .nav-link.active {
  background-color: #0d6efd;
  color: white;
}

.form-control:focus {
  border-color: #0d6efd;
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
}

.btn-primary {
  border-radius: 10px;
  padding: 12px;
  font-weight: 600;
}
</style>

