<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 px-4">
    <div class="bg-white w-full max-w-sm rounded-2xl shadow-lg p-8">

      <!-- Header -->
      <div class="text-center mb-6">
        <div class="flex justify-center mb-3">
          <div class="bg-primary-50 p-3 rounded-full">
            <KeyRound class="w-8 h-8 text-primary-600" />
          </div>
        </div>
        <h2 class="text-xl font-bold text-primary-600">Recuperar Acesso</h2>
        <p class="text-gray-500 text-sm mt-1">
          Informe seu e-mail para receber<br>o código de verificação
        </p>
      </div>

      <!-- Email -->
      <div class="mb-6">
        <label class="block text-xs font-medium text-gray-600 mb-1">E-mail</label>
        <div class="relative">
          <Mail class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input v-model="email" type="email" placeholder="seu@email.com"
            @keyup.enter="enviarCodigo"
            class="w-full pl-9 pr-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600 focus:border-transparent" />
        </div>
      </div>

      <!-- Botão -->
      <button @click="enviarCodigo" :disabled="carregando"
        class="w-full flex items-center justify-center gap-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-60 text-white font-semibold py-2.5 rounded-lg text-sm transition-colors cursor-pointer border-none">
        <Loader2 v-if="carregando" class="w-4 h-4 animate-spin" />
        <Send v-else class="w-4 h-4" />
        {{ carregando ? 'Enviando...' : 'Enviar código' }}
      </button>

      <!-- Erro -->
      <p v-if="erro" class="flex items-center justify-center gap-1.5 text-red-600 text-xs text-center mt-4">
        <AlertCircle class="w-3.5 h-3.5" />
        {{ erro }}
      </p>

      <!-- Voltar -->
      <div class="flex justify-center mt-5">
        <router-link to="/login"
          class="flex items-center gap-1 text-xs text-gray-500 hover:text-primary-600 transition-colors">
          <ArrowLeft class="w-3.5 h-3.5" />
          Voltar ao login
        </router-link>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import { KeyRound, Mail, Send, Loader2, AlertCircle, ArrowLeft } from 'lucide-vue-next'

const email = ref('')
const erro = ref('')
const carregando = ref(false)
const router = useRouter()

async function enviarCodigo() {
  if (!email.value) {
    erro.value = 'Informe o e-mail.'
    return
  }
  erro.value = ''
  carregando.value = true
  try {
    await api.post('/auth/recuperar-senha', { email: email.value })
    router.push({ name: 'verificar-codigo', query: { email: email.value } })
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao enviar código.'
  } finally {
    carregando.value = false
  }
}
</script>
