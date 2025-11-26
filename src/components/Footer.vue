<template>
  <footer class="bg-dark text-light mt-auto py-4">
    <div class="container">
      <div class="row">
        <div class="col-md-6">
          <h5><i class="bi bi-p-square-fill me-2"></i>VPMS</h5>
          <p class="text-muted mb-0">Vehicle Parking Management System</p>
        </div>
        <div class="col-md-6 text-md-end">
          <p class="text-muted mb-0">
            &copy; {{ new Date().getFullYear() }} VPMS. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
</script>

<style scoped>
footer {
  margin-top: auto;
}
</style>

