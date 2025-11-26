<template>
  <div class="container-fluid py-4">
    <div class="row mb-4">
      <div class="col">
        <h2 class="fw-bold">
          <i class="bi bi-speedometer2 me-2 text-primary"></i>Admin Dashboard
        </h2>
        <p class="text-muted">Manage parking lots, spots, and users</p>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="row g-4 mb-4">
      <div class="col-md-3">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="text-muted mb-2">Total Parking Lots</h6>
                <h3 class="mb-0 fw-bold text-primary">{{ stats.totalLots }}</h3>
              </div>
              <div class="bg-primary bg-opacity-10 p-3 rounded-circle">
                <i class="bi bi-building fs-4 text-primary"></i>
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
                <h6 class="text-muted mb-2">Total Spots</h6>
                <h3 class="mb-0 fw-bold text-success">{{ stats.totalSpots }}</h3>
              </div>
              <div class="bg-success bg-opacity-10 p-3 rounded-circle">
                <i class="bi bi-p-square fs-4 text-success"></i>
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
                <h6 class="text-muted mb-2">Occupied Spots</h6>
                <h3 class="mb-0 fw-bold text-danger">{{ stats.occupiedSpots }}</h3>
              </div>
              <div class="bg-danger bg-opacity-10 p-3 rounded-circle">
                <i class="bi bi-p-circle-fill fs-4 text-danger"></i>
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
                <h6 class="text-muted mb-2">Total Users</h6>
                <h3 class="mb-0 fw-bold text-info">{{ stats.totalUsers }}</h3>
              </div>
              <div class="bg-info bg-opacity-10 p-3 rounded-circle">
                <i class="bi bi-people fs-4 text-info"></i>
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
              <i class="bi bi-bar-chart me-2"></i>Parking Lot Status
            </h5>
          </div>
          <div class="card-body">
            <canvas ref="lotStatusChart"></canvas>
          </div>
        </div>
      </div>

      <div class="col-md-6">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-0 py-3">
            <h5 class="mb-0">
              <i class="bi bi-pie-chart me-2"></i>Spot Occupancy
            </h5>
          </div>
          <div class="card-body">
            <canvas ref="occupancyChart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="row">
      <div class="col-12">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-0 py-3 d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
              <i class="bi bi-clock-history me-2"></i>Recent Parking Activity
            </h5>
            <router-link to="/admin/parking-lots" class="btn btn-sm btn-primary">
              View All
            </router-link>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <div v-else-if="recentActivity.length === 0" class="text-center py-4 text-muted">
              No recent activity
            </div>
            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>User</th>
                    <th>Parking Lot</th>
                    <th>Spot</th>
                    <th>Status</th>
                    <th>Time</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="activity in recentActivity" :key="activity.id">
                    <td>{{ activity.username }}</td>
                    <td>{{ activity.lot_name }}</td>
                    <td>Spot #{{ activity.spot_id }}</td>
                    <td>
                      <span class="badge" :class="activity.status === 'O' ? 'bg-danger' : 'bg-success'">
                        {{ activity.status === 'O' ? 'Occupied' : 'Available' }}
                      </span>
                    </td>
                    <td>{{ formatDate(activity.timestamp) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import Chart from '../utils/chart'
import api from '../services/api'

const loading = ref(true)
const stats = ref({
  totalLots: 0,
  totalSpots: 0,
  occupiedSpots: 0,
  totalUsers: 0
})
const recentActivity = ref<any[]>([])
const lotStatusChart = ref<HTMLCanvasElement | null>(null)
const occupancyChart = ref<HTMLCanvasElement | null>(null)

const loadDashboardData = async () => {
  try {
    loading.value = true
    
    // Load statistics
    const statsRes = await api.get('/admin/stats')
    stats.value = statsRes.data

    // Load recent activity
    const activityRes = await api.get('/admin/recent-activity')
    recentActivity.value = activityRes.data

    await nextTick()
    renderCharts()
  } catch (error: any) {
    console.error('Error loading dashboard data:', error)
    // Set default values for demo
    stats.value = {
      totalLots: 5,
      totalSpots: 50,
      occupiedSpots: 12,
      totalUsers: 25
    }
    recentActivity.value = []
  } finally {
    loading.value = false
  }
}

const renderCharts = () => {
  if (lotStatusChart.value) {
    new Chart(lotStatusChart.value, {
      type: 'bar',
      data: {
        labels: ['Lot 1', 'Lot 2', 'Lot 3', 'Lot 4', 'Lot 5'],
        datasets: [{
          label: 'Available',
          data: [8, 7, 9, 6, 8],
          backgroundColor: 'rgba(40, 167, 69, 0.8)'
        }, {
          label: 'Occupied',
          data: [2, 3, 1, 4, 2],
          backgroundColor: 'rgba(220, 53, 69, 0.8)'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            position: 'top'
          }
        }
      }
    })
  }

  if (occupancyChart.value) {
    new Chart(occupancyChart.value, {
      type: 'doughnut',
      data: {
        labels: ['Available', 'Occupied'],
        datasets: [{
          data: [stats.value.totalSpots - stats.value.occupiedSpots, stats.value.occupiedSpots],
          backgroundColor: [
            'rgba(40, 167, 69, 0.8)',
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

