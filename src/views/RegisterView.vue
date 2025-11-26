<template>
  <div class="register-container">
    <div class="container">
      <div class="row justify-content-center align-items-center min-vh-100 py-5">
        <div class="col-md-6 col-lg-5">
          <div class="card shadow-lg border-0">
            <div class="card-body p-5">
              <div class="text-center mb-4">
                <i class="bi bi-person-plus text-primary" style="font-size: 3rem;"></i>
                <h2 class="mt-3 mb-1 fw-bold">Create Account</h2>
                <p class="text-muted">Join VPMS today</p>
              </div>

              <form @submit.prevent="handleRegister" novalidate>
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
                  <label for="email" class="form-label">
                    <i class="bi bi-envelope me-1"></i>Email
                  </label>
                  <input
                    type="email"
                    class="form-control"
                    :class="{ 'is-invalid': errors.email }"
                    id="email"
                    v-model="form.email"
                    required
                    autocomplete="email"
                  />
                  <div class="invalid-feedback" v-if="errors.email">
                    {{ errors.email }}
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
                    autocomplete="new-password"
                    minlength="6"
                  />
                  <div class="invalid-feedback" v-if="errors.password">
                    {{ errors.password }}
                  </div>
                  <small class="form-text text-muted">Minimum 6 characters</small>
                </div>

                <div class="mb-3">
                  <label for="confirmPassword" class="form-label">
                    <i class="bi bi-lock-fill me-1"></i>Confirm Password
                  </label>
                  <input
                    type="password"
                    class="form-control"
                    :class="{ 'is-invalid': errors.confirmPassword }"
                    id="confirmPassword"
                    v-model="form.confirmPassword"
                    required
                    autocomplete="new-password"
                  />
                  <div class="invalid-feedback" v-if="errors.confirmPassword">
                    {{ errors.confirmPassword }}
                  </div>
                </div>

                <div class="alert alert-danger" v-if="errorMessage" role="alert">
                  <i class="bi bi-exclamation-triangle me-2"></i>{{ errorMessage }}
                </div>

                <div class="alert alert-success" v-if="successMessage" role="alert">
                  <i class="bi bi-check-circle me-2"></i>{{ successMessage }}
                </div>

                <button 
                  type="submit" 
                  class="btn btn-primary w-100 mb-3"
                  :disabled="loading"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-person-plus me-2"></i>
                  {{ loading ? 'Registering...' : 'Register' }}
                </button>
              </form>

              <div class="text-center">
                <p class="mb-0">
                  Already have an account? 
                  <router-link to="/login" class="text-primary text-decoration-none">
                    Login here
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

const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const errors = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const validateForm = () => {
  errors.username = ''
  errors.email = ''
  errors.password = ''
  errors.confirmPassword = ''
  let isValid = true

  if (!form.username.trim()) {
    errors.username = 'Username is required'
    isValid = false
  } else if (form.username.length < 3) {
    errors.username = 'Username must be at least 3 characters'
    isValid = false
  }

  if (!form.email.trim()) {
    errors.email = 'Email is required'
    isValid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.email = 'Please enter a valid email address'
    isValid = false
  }

  if (!form.password) {
    errors.password = 'Password is required'
    isValid = false
  } else if (form.password.length < 6) {
    errors.password = 'Password must be at least 6 characters'
    isValid = false
  }

  if (!form.confirmPassword) {
    errors.confirmPassword = 'Please confirm your password'
    isValid = false
  } else if (form.password !== form.confirmPassword) {
    errors.confirmPassword = 'Passwords do not match'
    isValid = false
  }

  return isValid
}

const handleRegister = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  
  if (!validateForm()) {
    return
  }

  loading.value = true

  try {
    const result = await authStore.register({
      username: form.username,
      email: form.email,
      password: form.password
    })

    if (result.success) {
      successMessage.value = 'Registration successful! Redirecting to login...'
      setTimeout(() => {
        router.push('/login')
      }, 2000)
    } else {
      errorMessage.value = result.message || 'Registration failed. Please try again.'
    }
  } catch (error: any) {
    errorMessage.value = 'An error occurred. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.card {
  border-radius: 15px;
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

