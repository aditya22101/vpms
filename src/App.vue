<template>
  <div id="app">
    <Navbar v-if="showNavbar" />
    <main class="main-content">
      <router-view />
    </main>
    <Footer v-if="showNavbar" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from './components/Navbar.vue'
import Footer from './components/Footer.vue'

const route = useRoute()

const showNavbar = computed(() => {
  return route.name !== 'Login' && route.name !== 'Register'
})
</script>

<style>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding-top: 20px;
}

body {
  margin: 0;
  padding: 0;
  background-color: #f8f9fa;
}
</style>
