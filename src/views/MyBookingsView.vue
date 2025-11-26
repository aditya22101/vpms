<template>
  <div class="container-fluid py-4">
    <div class="row mb-4">
      <div class="col d-flex justify-content-between align-items-center">
        <div>
          <h2 class="fw-bold">
            <i class="bi bi-calendar-check me-2 text-primary"></i>My Bookings
          </h2>
          <p class="text-muted">View your parking booking history</p>
        </div>
        <button class="btn btn-outline-primary" @click="loadBookings">
          <i class="bi bi-arrow-clockwise me-2"></i>Refresh
        </button>
      </div>
    </div>

    <!-- Filter Tabs -->
    <ul class="nav nav-pills mb-4">
      <li class="nav-item">
        <button 
          class="nav-link" 
          :class="{ active: filter === 'all' }"
          @click="filter = 'all'"
        >
          All
        </button>
      </li>
      <li class="nav-item">
        <button 
          class="nav-link" 
          :class="{ active: filter === 'active' }"
          @click="filter = 'active'"
        >
          Active
        </button>
      </li>
      <li class="nav-item">
        <button 
          class="nav-link" 
          :class="{ active: filter === 'completed' }"
          @click="filter = 'completed'"
        >
          Completed
        </button>
      </li>
    </ul>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else class="row g-4">
      <div 
        class="col-12" 
        v-for="booking in filteredBookings" 
        :key="booking.id"
      >
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <div class="row align-items-center">
              <div class="col-md-8">
                <div class="d-flex align-items-center mb-2">
                  <h5 class="mb-0 me-3">{{ booking.lot_name }}</h5>
                  <span 
                    class="badge"
                    :class="booking.status === 'active' ? 'bg-success' : 'bg-secondary'"
                  >
                    {{ booking.status === 'active' ? 'Active' : 'Completed' }}
                  </span>
                </div>
                <p class="text-muted mb-2">
                  <i class="bi bi-geo-alt me-2"></i>{{ booking.address }}
                </p>
                <div class="row">
                  <div class="col-md-4">
                    <small class="text-muted">Spot Number</small>
                    <p class="mb-0 fw-bold">#{{ booking.spot_id }}</p>
                  </div>
                  <div class="col-md-4">
                    <small class="text-muted">Parked At</small>
                    <p class="mb-0">{{ formatDate(booking.parking_timestamp) }}</p>
                  </div>
                  <div class="col-md-4" v-if="booking.leaving_timestamp">
                    <small class="text-muted">Released At</small>
                    <p class="mb-0">{{ formatDate(booking.leaving_timestamp) }}</p>
                  </div>
                </div>
              </div>
              <div class="col-md-4 text-md-end">
                <div class="mb-3">
                  <h4 class="text-primary mb-0">₹{{ booking.parking_cost || 0 }}</h4>
                  <small class="text-muted">Total Cost</small>
                </div>
                <button 
                  v-if="booking.status === 'active'"
                  class="btn btn-danger"
                  @click="releaseParking(booking.id)"
                >
                  <i class="bi bi-box-arrow-right me-2"></i>Release Spot
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="filteredBookings.length === 0" class="col-12">
        <div class="card border-0 shadow-sm text-center py-5">
          <i class="bi bi-calendar-x text-muted" style="font-size: 3rem;"></i>
          <p class="text-muted mt-3">No bookings found</p>
          <router-link to="/user/book-parking" class="btn btn-primary">
            Book a Parking Spot
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()

const loading = ref(true)
const bookings = ref<any[]>([])
const filter = ref<'all' | 'active' | 'completed'>('all')

const filteredBookings = computed(() => {
  if (filter.value === 'all') return bookings.value
  if (filter.value === 'active') {
    return bookings.value.filter(b => b.status === 'active' || !b.leaving_timestamp)
  }
  return bookings.value.filter(b => b.status === 'completed' || b.leaving_timestamp)
})

const loadBookings = async () => {
  try {
    loading.value = true
    const response = await api.get('/user/bookings')
    bookings.value = response.data
  } catch (error: any) {
    console.error('Error loading bookings:', error)
    // Demo data
    bookings.value = [
      {
        id: 1,
        lot_name: 'Downtown Parking',
        address: '123 Main Street',
        spot_id: 5,
        parking_timestamp: new Date().toISOString(),
        leaving_timestamp: null,
        parking_cost: 150,
        status: 'active'
      },
      {
        id: 2,
        lot_name: 'Mall Parking',
        address: '456 Shopping Ave',
        spot_id: 12,
        parking_timestamp: new Date(Date.now() - 86400000).toISOString(),
        leaving_timestamp: new Date(Date.now() - 82800000).toISOString(),
        parking_cost: 200,
        status: 'completed'
      }
    ]
  } finally {
    loading.value = false
  }
}

const releaseParking = async (bookingId: number) => {
  if (!confirm('Are you sure you want to release this parking spot?')) {
    return
  }

  try {
    await api.post(`/user/bookings/${bookingId}/release`)
    loadBookings()
    router.push('/user')
  } catch (error: any) {
    alert(error.response?.data?.message || 'Failed to release parking spot')
  }
}

const formatDate = (dateString: string) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleString()
}

onMounted(() => {
  loadBookings()
})
</script>

<style scoped>
.nav-pills .nav-link {
  color: #495057;
  border-radius: 10px;
}

.nav-pills .nav-link.active {
  background-color: #0d6efd;
  color: white;
}

.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-3px);
}
</style>

