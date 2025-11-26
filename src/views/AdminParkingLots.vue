<template>
  <div class="container-fluid py-4">
    <div class="row mb-4">
      <div class="col d-flex justify-content-between align-items-center">
        <div>
          <h2 class="fw-bold">
            <i class="bi bi-building me-2 text-primary"></i>Parking Lots Management
          </h2>
          <p class="text-muted">Create, edit, and manage parking lots</p>
        </div>
        <button class="btn btn-primary" @click="showCreateModal = true">
          <i class="bi bi-plus-circle me-2"></i>Create New Lot
        </button>
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
        v-for="lot in parkingLots" 
        :key="lot.id"
      >
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <div>
                <h5 class="card-title fw-bold">{{ lot.prime_location_name }}</h5>
                <p class="text-muted mb-1 small">
                  <i class="bi bi-geo-alt me-1"></i>{{ lot.address }}
                </p>
                <p class="text-muted mb-0 small">
                  <i class="bi bi-pin-map me-1"></i>PIN: {{ lot.pin_code }}
                </p>
              </div>
              <div class="dropdown">
                <button 
                  class="btn btn-sm btn-outline-secondary" 
                  type="button" 
                  data-bs-toggle="dropdown"
                >
                  <i class="bi bi-three-dots-vertical"></i>
                </button>
                <ul class="dropdown-menu dropdown-menu-end">
                  <li>
                    <a class="dropdown-item" href="#" @click.prevent="editLot(lot)">
                      <i class="bi bi-pencil me-2"></i>Edit
                    </a>
                  </li>
                  <li>
                    <a class="dropdown-item text-danger" href="#" @click.prevent="confirmDelete(lot)">
                      <i class="bi bi-trash me-2"></i>Delete
                    </a>
                  </li>
                </ul>
              </div>
            </div>

            <div class="mb-3">
              <div class="d-flex justify-content-between mb-2">
                <span class="text-muted">Price per hour:</span>
                <span class="fw-bold text-success">₹{{ lot.price }}</span>
              </div>
              <div class="d-flex justify-content-between mb-2">
                <span class="text-muted">Total Spots:</span>
                <span class="fw-bold">{{ lot.number_of_spots }}</span>
              </div>
              <div class="d-flex justify-content-between">
                <span class="text-muted">Available:</span>
                <span class="fw-bold text-success">{{ lot.available_spots || 0 }}</span>
              </div>
            </div>

            <button 
              class="btn btn-sm btn-outline-primary w-100"
              @click="viewLotDetails(lot)"
            >
              <i class="bi bi-eye me-2"></i>View Details
            </button>
          </div>
        </div>
      </div>

      <div v-if="parkingLots.length === 0" class="col-12">
        <div class="card border-0 shadow-sm text-center py-5">
          <i class="bi bi-building text-muted" style="font-size: 3rem;"></i>
          <p class="text-muted mt-3">No parking lots created yet</p>
          <button class="btn btn-primary" @click="showCreateModal = true">
            Create First Parking Lot
          </button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div 
      class="modal fade" 
      :class="{ show: showCreateModal || showEditModal }" 
      :style="{ display: (showCreateModal || showEditModal) ? 'block' : 'none' }"
      tabindex="-1"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              {{ showEditModal ? 'Edit' : 'Create' }} Parking Lot
            </h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveLot">
              <div class="mb-3">
                <label class="form-label">Location Name *</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="lotForm.prime_location_name"
                  required
                />
              </div>
              <div class="mb-3">
                <label class="form-label">Address *</label>
                <textarea 
                  class="form-control" 
                  v-model="lotForm.address"
                  rows="2"
                  required
                ></textarea>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">PIN Code *</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="lotForm.pin_code"
                    required
                    pattern="[0-9]{6}"
                  />
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Price per Hour (₹) *</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    v-model.number="lotForm.price"
                    min="0"
                    step="0.01"
                    required
                  />
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Number of Spots *</label>
                <input 
                  type="number" 
                  class="form-control" 
                  v-model.number="lotForm.number_of_spots"
                  min="1"
                  required
                />
                <small class="form-text text-muted">
                  This will create {{ lotForm.number_of_spots || 0 }} parking spots automatically
                </small>
              </div>
              <div class="alert alert-danger" v-if="errorMessage">
                {{ errorMessage }}
              </div>
              <div class="d-flex justify-content-end gap-2">
                <button type="button" class="btn btn-secondary" @click="closeModal">
                  Cancel
                </button>
                <button type="submit" class="btn btn-primary" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                  {{ saving ? 'Saving...' : 'Save' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    <div 
      class="modal-backdrop fade" 
      :class="{ show: showCreateModal || showEditModal }"
      v-if="showCreateModal || showEditModal"
    ></div>

    <!-- Lot Details Modal -->
    <div 
      class="modal fade" 
      :class="{ show: showDetailsModal }" 
      :style="{ display: showDetailsModal ? 'block' : 'none' }"
      tabindex="-1"
    >
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Parking Lot Details - {{ selectedLot?.prime_location_name }}</h5>
            <button type="button" class="btn-close" @click="showDetailsModal = false"></button>
          </div>
          <div class="modal-body">
            <div v-if="loadingSpots" class="text-center py-4">
              <div class="spinner-border text-primary" role="status"></div>
            </div>
            <div v-else>
              <div class="row mb-4">
                <div class="col-md-3">
                  <div class="card bg-light">
                    <div class="card-body text-center">
                      <h3 class="text-primary">{{ lotSpots.length }}</h3>
                      <p class="mb-0 text-muted">Total Spots</p>
                    </div>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="card bg-light">
                    <div class="card-body text-center">
                      <h3 class="text-success">{{ availableCount }}</h3>
                      <p class="mb-0 text-muted">Available</p>
                    </div>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="card bg-light">
                    <div class="card-body text-center">
                      <h3 class="text-danger">{{ occupiedCount }}</h3>
                      <p class="mb-0 text-muted">Occupied</p>
                    </div>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="card bg-light">
                    <div class="card-body text-center">
                      <h3 class="text-info">₹{{ selectedLot?.price }}</h3>
                      <p class="mb-0 text-muted">Price/Hour</p>
                    </div>
                  </div>
                </div>
              </div>

              <h6 class="mb-3">Parking Spots</h6>
              <div class="row g-2">
                <div 
                  class="col-md-2 col-sm-3 col-4" 
                  v-for="spot in lotSpots" 
                  :key="spot.id"
                >
                  <div 
                    class="card text-center p-2"
                    :class="spot.status === 'O' ? 'bg-danger text-white' : 'bg-success text-white'"
                  >
                    <small class="fw-bold">Spot #{{ spot.id }}</small>
                    <br>
                    <small>{{ spot.status === 'O' ? 'Occupied' : 'Available' }}</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div 
      class="modal-backdrop fade" 
      :class="{ show: showDetailsModal }"
      v-if="showDetailsModal"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import api from '../services/api'

const loading = ref(true)
const saving = ref(false)
const loadingSpots = ref(false)
const parkingLots = ref<any[]>([])
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDetailsModal = ref(false)
const selectedLot = ref<any>(null)
const lotSpots = ref<any[]>([])
const errorMessage = ref('')

const lotForm = reactive({
  id: null,
  prime_location_name: '',
  address: '',
  pin_code: '',
  price: 0,
  number_of_spots: 1
})

const loadParkingLots = async () => {
  try {
    loading.value = true
    const response = await api.get('/admin/parking-lots')
    parkingLots.value = response.data
  } catch (error: any) {
    console.error('Error loading parking lots:', error)
    // Demo data
    parkingLots.value = [
      {
        id: 1,
        prime_location_name: 'Downtown Parking',
        address: '123 Main Street',
        pin_code: '123456',
        price: 50,
        number_of_spots: 20,
        available_spots: 15
      }
    ]
  } finally {
    loading.value = false
  }
}

const saveLot = async () => {
  try {
    saving.value = true
    errorMessage.value = ''

    const url = lotForm.id 
      ? `/admin/parking-lots/${lotForm.id}`
      : '/admin/parking-lots'
    
    const method = lotForm.id ? 'put' : 'post'
    
    const response = await api[method](url, {
      prime_location_name: lotForm.prime_location_name,
      address: lotForm.address,
      pin_code: lotForm.pin_code,
      price: lotForm.price,
      number_of_spots: lotForm.number_of_spots
    })

    console.log('Save response:', response.data)
    closeModal()
    loadParkingLots()
  } catch (error: any) {
    console.error('Save error:', error)
    const errorMsg = error.response?.data?.message || error.message || 'Failed to save parking lot'
    errorMessage.value = errorMsg
    console.error('Full error:', error.response)
  } finally {
    saving.value = false
  }
}

const editLot = (lot: any) => {
  Object.assign(lotForm, {
    id: lot.id,
    prime_location_name: lot.prime_location_name,
    address: lot.address,
    pin_code: lot.pin_code,
    price: lot.price,
    number_of_spots: lot.number_of_spots
  })
  showEditModal.value = true
}

const confirmDelete = async (lot: any) => {
  if (confirm(`Are you sure you want to delete "${lot.prime_location_name}"? This can only be done if all spots are empty.`)) {
    try {
      await api.delete(`/admin/parking-lots/${lot.id}`)
      loadParkingLots()
    } catch (error: any) {
      alert(error.response?.data?.message || 'Failed to delete parking lot')
    }
  }
}

const viewLotDetails = async (lot: any) => {
  selectedLot.value = lot
  showDetailsModal.value = true
  loadingSpots.value = true

  try {
    const response = await api.get(`/admin/parking-lots/${lot.id}/spots`)
    lotSpots.value = response.data
  } catch (error: any) {
    console.error('Error loading spots:', error)
    lotSpots.value = []
  } finally {
    loadingSpots.value = false
  }
}

const closeModal = () => {
  showCreateModal.value = false
  showEditModal.value = false
  Object.assign(lotForm, {
    id: null,
    prime_location_name: '',
    address: '',
    pin_code: '',
    price: 0,
    number_of_spots: 1
  })
  errorMessage.value = ''
}

const availableCount = computed(() => lotSpots.value.filter((s: any) => s.status === 'A').length)
const occupiedCount = computed(() => lotSpots.value.filter((s: any) => s.status === 'O').length)

onMounted(() => {
  loadParkingLots()
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

