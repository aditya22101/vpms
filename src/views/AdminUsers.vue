<template>
  <div class="container-fluid py-4">
    <div class="row mb-4">
      <div class="col">
        <h2 class="fw-bold">
          <i class="bi bi-people me-2 text-primary"></i>Users Management
        </h2>
        <p class="text-muted">View and manage all registered users</p>
      </div>
    </div>

    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <div class="row mb-3">
          <div class="col-md-6">
            <div class="input-group">
              <span class="input-group-text">
                <i class="bi bi-search"></i>
              </span>
              <input 
                type="text" 
                class="form-control" 
                placeholder="Search users..."
                v-model="searchQuery"
                @input="filterUsers"
              />
            </div>
          </div>
        </div>

        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Email</th>
                <th>Total Bookings</th>
                <th>Active Bookings</th>
                <th>Total Spent</th>
                <th>Registered</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in filteredUsers" :key="user.id">
                <td>{{ user.id }}</td>
                <td>
                  <i class="bi bi-person-circle me-2"></i>
                  {{ user.username }}
                </td>
                <td>{{ user.email }}</td>
                <td>
                  <span class="badge bg-info">{{ user.total_bookings || 0 }}</span>
                </td>
                <td>
                  <span class="badge bg-success">{{ user.active_bookings || 0 }}</span>
                </td>
                <td>₹{{ user.total_spent || 0 }}</td>
                <td>{{ formatDate(user.created_at) }}</td>
              </tr>
            </tbody>
          </table>

          <div v-if="filteredUsers.length === 0" class="text-center py-4 text-muted">
            No users found
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '../services/api'

const loading = ref(true)
const users = ref<any[]>([])
const searchQuery = ref('')

const filteredUsers = computed(() => {
  if (!searchQuery.value) return users.value
  
  const query = searchQuery.value.toLowerCase()
  return users.value.filter(user => 
    user.username.toLowerCase().includes(query) ||
    user.email.toLowerCase().includes(query)
  )
})

const loadUsers = async () => {
  try {
    loading.value = true
    const response = await api.get('/admin/users')
    users.value = response.data
  } catch (error: any) {
    console.error('Error loading users:', error)
    // Demo data
    users.value = [
      {
        id: 1,
        username: 'john_doe',
        email: 'john@example.com',
        total_bookings: 15,
        active_bookings: 1,
        total_spent: 1250,
        created_at: new Date().toISOString()
      }
    ]
  } finally {
    loading.value = false
  }
}

const filterUsers = () => {
  // Computed property handles filtering
}

const formatDate = (dateString: string) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.table th {
  background-color: #f8f9fa;
  font-weight: 600;
}
</style>

