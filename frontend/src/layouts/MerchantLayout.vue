<template>
  <div class="min-h-screen flex bg-gray-50">
    <SideBar />
    <main class="flex-1 p-6 overflow-auto">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import SideBar from '../components/SideBar.vue'
</script>
