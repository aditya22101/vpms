<template>
  <div class="container-fluid py-4">
    <div class="row mb-4">
      <div class="col">
        <h2 class="fw-bold">
          <i class="bi bi-plus-circle me-2 text-primary"></i>Book Parking Spot
        </h2>
        <p class="text-muted">Select a parking lot to book an available spot</p>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else class="row g-4">
      <div 
        class="col-md-6 col-lg-4" 
        v-for="lot in availableLots" 
        :key="lot.id"
      >
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <h5 class="card-title fw-bold">{{ lot.prime_location_name }}</h5>
            <p class="text-muted mb-2 small">
              <i class="bi bi-geo-alt me-1"></i>{{ lot.address }}
            </p>
            <p class="text-muted mb-3 small">
              <i class="bi bi-pin-map me-1"></i>PIN: {{ lot.pin_code }}
            </p>

            <div class="mb-3">
              <div class="d-flex justify-content-between mb-2">
                <span class="text-muted">Price per hour:</span>
                <span class="fw-bold text-success">₹{{ lot.price }}</span>
              </div>
              <div class="d-flex justify-content-between mb-2">
                <span class="text-muted">Available spots:</span>
                <span class="fw-bold text-primary">{{ lot.available_spots }}</span>
              </div>
              <div class="d-flex justify-content-between">
                <span class="text-muted">Total spots:</span>
                <span class="fw-bold">{{ lot.number_of_spots }}</span>
              </div>
            </div>

            <button 
              class="btn btn-primary w-100"
              @click="bookParking(lot.id)"
              :disabled="lot.available_spots === 0 || booking"
            >
              <span v-if="booking" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bi bi-check-circle me-2"></i>
              {{ lot.available_spots === 0 ? 'No Spots Available' : (booking ? 'Booking...' : 'Book Now') }}
            </button>
          </div>
        </div>
      </div>

      <div v-if="availableLots.length === 0" class="col-12">
        <div class="card border-0 shadow-sm text-center py-5">
          <i class="bi bi-building text-muted" style="font-size: 3rem;"></i>
          <p class="text-muted mt-3">No parking lots available at the moment</p>
        </div>
      </div>
    </div>

    <!-- Booking Confirmation Modal -->
    <div 
      class="modal fade" 
      :class="{ show: showConfirmModal }" 
      :style="{ display: showConfirmModal ? 'block' : 'none' }"
      tabindex="-1"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Booking Confirmation</h5>
            <button type="button" class="btn-close" @click="showConfirmModal = false"></button>
          </div>
          <div class="modal-body">
            <div v-if="bookingDetails">
              <p><strong>Parking Lot:</strong> {{ bookingDetails.lot_name }}</p>
              <p><strong>Spot Number:</strong> #{{ bookingDetails.spot_id }}</p>
              <p><strong>Price:</strong> ₹{{ bookingDetails.price }}/hour</p>
              <p class="text-muted small">Your spot has been automatically allocated. Please proceed to the parking location.</p>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showConfirmModal = false">
              Close
            </button>
            <router-link to="/user" class="btn btn-primary">
              Go to Dashboard
            </router-link>
          </div>
        </div>
      </div>
    </div>
    <div 
      class="modal-backdrop fade" 
      :class="{ show: showConfirmModal }"
      v-if="showConfirmModal"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()

const loading = ref(true)
const booking = ref(false)
const availableLots = ref<any[]>([])
const showConfirmModal = ref(false)
const bookingDetails = ref<any>(null)

const loadAvailableLots = async () => {
  try {
    loading.value = true
    const response = await api.get('/user/parking-lots/available')
    availableLots.value = response.data
  } catch (error: any) {
    console.error('Error loading parking lots:', error)
    // Demo data
    availableLots.value = [
      {
        id: 1,
        prime_location_name: 'Downtown Parking',
        address: '123 Main Street',
        pin_code: '123456',
        price: 50,
        number_of_spots: 20,
        available_spots: 15
      },
      {
        id: 2,
        prime_location_name: 'Mall Parking',
        address: '456 Shopping Ave',
        pin_code: '123457',
        price: 40,
        number_of_spots: 30,
        available_spots: 25
      }
    ]
  } finally {
    loading.value = false
  }
}

const bookParking = async (lotId: number) => {
  if (!confirm('Confirm booking for this parking lot? A spot will be automatically allocated.')) {
    return
  }

  try {
    booking.value = true
    const response = await api.post('/user/book-parking', { lot_id: lotId })
    // Backend returns booking data directly
    bookingDetails.value = response.data.booking || response.data
    showConfirmModal.value = true
    loadAvailableLots() // Refresh to update available spots
  } catch (error: any) {
    console.error('Booking error:', error)
    const errorMsg = error.response?.data?.message || error.message || 'Failed to book parking spot'
    alert(errorMsg)
  } finally {
    booking.value = false
  }
}

onMounted(() => {
  loadAvailableLots()
})
</script>

<style scoped>
.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-5px);
}

.modal.show {
  display: block !important;
}
</style>

