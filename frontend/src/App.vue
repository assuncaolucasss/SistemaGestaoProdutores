<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <AppNavbar />
    <main class="flex-1">
      <RouterView v-slot="{ Component, route }">
        <KeepAlive :include="['LoginView']">
          <component :is="Component" :key="route.path" />
        </KeepAlive>
      </RouterView>
    </main>
    <AppFooter />
  </div>
</template>

<script setup>
import AppNavbar from './components/AppNavbar.vue'
import AppFooter from './components/AppFooter.vue'
</script>