<template>
  <div class="container-fluid py-4">
    <div class="row mb-4">
      <div class="col">
        <h2 class="fw-bold">
          <i class="bi bi-speedometer2 me-2 text-primary"></i>My Dashboard
        </h2>
        <p class="text-muted">Welcome back, {{ authStore.user?.username }}!</p>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="row g-4 mb-4">
      <div class="col-md-3">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="text-muted mb-2">Total Bookings</h6>
                <h3 class="mb-0 fw-bold text-primary">{{ stats.totalBookings }}</h3>
              </div>
              <div class="bg-primary bg-opacity-10 p-3 rounded-circle">
                <i class="bi bi-calendar-check fs-4 text-primary"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="text-muted mb-2">Active Bookings</h6>
                <h3 class="mb-0 fw-bold text-success">{{ stats.activeBookings }}</h3>
              </div>
              <div class="bg-success bg-opacity-10 p-3 rounded-circle">
                <i class="bi bi-p-circle-fill fs-4 text-success"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="text-muted mb-2">Total Spent</h6>
                <h3 class="mb-0 fw-bold text-info">₹{{ stats.totalSpent }}</h3>
              </div>
              <div class="bg-info bg-opacity-10 p-3 rounded-circle">
                <i class="bi bi-currency-rupee fs-4 text-info"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="text-muted mb-2">This Month</h6>
                <h3 class="mb-0 fw-bold text-warning">{{ stats.monthlyBookings }}</h3>
              </div>
              <div class="bg-warning bg-opacity-10 p-3 rounded-circle">
                <i class="bi bi-calendar-month fs-4 text-warning"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="row g-4 mb-4">
      <div class="col-md-6">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-0 py-3">
            <h5 class="mb-0">
              <i class="bi bi-bar-chart me-2"></i>Monthly Bookings
            </h5>
          </div>
          <div class="card-body">
            <canvas ref="monthlyChart"></canvas>
          </div>
        </div>
      </div>

      <div class="col-md-6">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-0 py-3">
            <h5 class="mb-0">
              <i class="bi bi-pie-chart me-2"></i>Parking Lot Usage
            </h5>
          </div>
          <div class="card-body">
            <canvas ref="lotUsageChart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- Active Booking -->
    <div class="row mb-4" v-if="activeBooking">
      <div class="col-12">
        <div class="card border-0 shadow-sm border-start border-4 border-success">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h5 class="mb-2">
                  <i class="bi bi-p-circle-fill text-success me-2"></i>Active Parking
                </h5>
                <p class="mb-1">
                  <strong>Location:</strong> {{ activeBooking.lot_name }}
                </p>
                <p class="mb-1">
                  <strong>Spot:</strong> #{{ activeBooking.spot_id }}
                </p>
                <p class="mb-0 text-muted small">
                  Parked at: {{ formatDate(activeBooking.parking_timestamp) }}
                </p>
              </div>
              <div class="text-end">
                <p class="mb-2">
                  <span class="badge bg-success fs-6">Active</span>
                </p>
                <button 
                  class="btn btn-danger"
                  @click="releaseParking(activeBooking.id)"
                >
                  <i class="bi bi-box-arrow-right me-2"></i>Release Spot
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="row">
      <div class="col-md-6 mb-3">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body text-center py-5">
            <i class="bi bi-plus-circle text-primary" style="font-size: 3rem;"></i>
            <h5 class="mt-3 mb-3">Book a Parking Spot</h5>
            <router-link to="/user/book-parking" class="btn btn-primary">
              <i class="bi bi-plus-circle me-2"></i>Book Now
            </router-link>
          </div>
        </div>
      </div>

      <div class="col-md-6 mb-3">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body text-center py-5">
            <i class="bi bi-file-earmark-spreadsheet text-info" style="font-size: 3rem;"></i>
            <h5 class="mt-3 mb-3">Export Booking History</h5>
            <button class="btn btn-info" @click="exportCSV" :disabled="exporting">
              <span v-if="exporting" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bi bi-download me-2"></i>
              {{ exporting ? 'Exporting...' : 'Export CSV' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import Chart from '../utils/chart'
import { useAuthStore } from '../stores/auth'
import api from '../services/api'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const exporting = ref(false)
const stats = ref({
  totalBookings: 0,
  activeBookings: 0,
  totalSpent: 0,
  monthlyBookings: 0
})
const activeBooking = ref<any>(null)
const monthlyChart = ref<HTMLCanvasElement | null>(null)
const lotUsageChart = ref<HTMLCanvasElement | null>(null)

const loadDashboardData = async () => {
  try {
    loading.value = true
    
    // Load statistics
    const statsRes = await api.get('/user/stats')
    stats.value = statsRes.data

    // Load active booking
    const bookingRes = await api.get('/user/active-booking')
    activeBooking.value = bookingRes.data || null

    await nextTick()
    renderCharts()
  } catch (error: any) {
    console.error('Error loading dashboard data:', error)
    // Demo data
    stats.value = {
      totalBookings: 12,
      activeBookings: 1,
      totalSpent: 850,
      monthlyBookings: 3
    }
  } finally {
    loading.value = false
  }
}

const renderCharts = () => {
  if (monthlyChart.value) {
    new Chart(monthlyChart.value, {
      type: 'line',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
          label: 'Bookings',
          data: [2, 3, 1, 4, 2, 3],
          borderColor: 'rgb(13, 110, 253)',
          backgroundColor: 'rgba(13, 110, 253, 0.1)',
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            display: false
          }
        }
      }
    })
  }

  if (lotUsageChart.value) {
    new Chart(lotUsageChart.value, {
      type: 'doughnut',
      data: {
        labels: ['Downtown', 'Mall', 'Airport', 'Station'],
        datasets: [{
          data: [5, 3, 2, 2],
          backgroundColor: [
            'rgba(13, 110, 253, 0.8)',
            'rgba(40, 167, 69, 0.8)',
            'rgba(255, 193, 7, 0.8)',
            'rgba(220, 53, 69, 0.8)'
          ]
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            position: 'bottom'
          }
        }
      }
    })
  }
}

const releaseParking = async (bookingId: number) => {
  if (!confirm('Are you sure you want to release this parking spot?')) {
    return
  }

  try {
    await api.post(`/user/bookings/${bookingId}/release`)
    activeBooking.value = null
    loadDashboardData()
    alert('Parking spot released successfully!')
  } catch (error: any) {
    alert(error.response?.data?.message || 'Failed to release parking spot')
  }
}

const exportCSV = async () => {
  try {
    exporting.value = true
    const response = await api.get('/user/export-csv', {
      responseType: 'blob'
    })
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data], { type: 'text/csv' }))
    const link = document.createElement('a')
    link.href = url
    const filename = response.headers['content-disposition'] 
      ? response.headers['content-disposition'].split('filename=')[1]?.replace(/"/g, '')
      : `parking-history-${new Date().getTime()}.csv`
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    
    alert('CSV exported successfully!')
  } catch (error: any) {
    console.error('Export error:', error)
    alert(error.response?.data?.message || 'Failed to export CSV. Please try again.')
  } finally {
    exporting.value = false
  }
}

const formatDate = (dateString: string) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleString()
}

onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-5px);
}
</style>

