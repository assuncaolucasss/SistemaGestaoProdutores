<template>
  <footer class="bg-primary-600 text-white/80 text-center py-5 px-6 text-xs mt-auto">
    <div class="flex items-center justify-center gap-1.5">
      <Sprout class="w-3.5 h-3.5" />
      © {{ ano }} ABLtech — Todos os direitos reservados
    </div>
  </footer>
</template>

<script setup>
import { Sprout } from 'lucide-vue-next'
const ano = new Date().getFullYear()
</script>
