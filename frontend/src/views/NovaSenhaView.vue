<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 px-4">
    <div class="bg-white w-full max-w-sm rounded-2xl shadow-lg p-8">

      <!-- Header -->
      <div class="text-center mb-6">
        <div class="flex justify-center mb-3">
          <div class="bg-primary-50 p-3 rounded-full">
            <LockKeyhole class="w-8 h-8 text-primary-600" />
          </div>
        </div>
        <h2 class="text-xl font-bold text-primary-600">Nova Senha</h2>
        <p class="text-gray-500 text-sm mt-1">Crie uma nova senha para sua conta</p>
      </div>

      <!-- Nova senha -->
      <div class="mb-4">
        <label class="block text-xs font-medium text-gray-600 mb-1">Nova senha</label>
        <div class="relative">
          <Lock class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input v-model="novaSenha" :type="mostrarSenha ? 'text' : 'password'" placeholder="••••••••"
            class="w-full pl-9 pr-9 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600 focus:border-transparent" />
          <button type="button" @click="mostrarSenha = !mostrarSenha"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 border-none bg-transparent cursor-pointer">
            <Eye v-if="!mostrarSenha" class="w-4 h-4" />
            <EyeOff v-else class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- Confirmar senha -->
      <div class="mb-6">
        <label class="block text-xs font-medium text-gray-600 mb-1">Confirmar senha</label>
        <div class="relative">
          <Lock class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input v-model="confirmarSenha" :type="mostrarSenha ? 'text' : 'password'" placeholder="••••••••"
            @keyup.enter="salvar"
            :class="[
              'w-full pl-9 pr-3 py-2.5 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:border-transparent',
              senhasIncompativeis
                ? 'border-red-400 focus:ring-red-400'
                : 'border-gray-300 focus:ring-primary-600'
            ]" />
        </div>
        <p v-if="senhasIncompativeis" class="text-red-500 text-xs mt-1 flex items-center gap-1">
          <AlertCircle class="w-3 h-3" /> As senhas não coincidem
        </p>
      </div>

      <!-- Botão -->
      <button @click="salvar" :disabled="carregando || senhasIncompativeis || !novaSenha"
        class="w-full flex items-center justify-center gap-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-60 text-white font-semibold py-2.5 rounded-lg text-sm transition-colors cursor-pointer border-none">
        <Loader2 v-if="carregando" class="w-4 h-4 animate-spin" />
        <Check v-else class="w-4 h-4" />
        {{ carregando ? 'Salvando...' : 'Salvar nova senha' }}
      </button>

      <!-- Erro -->
      <p v-if="erro" class="flex items-center justify-center gap-1.5 text-red-600 text-xs text-center mt-4">
        <AlertCircle class="w-3.5 h-3.5" />
        {{ erro }}
      </p>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../services/api'
import { LockKeyhole, Lock, Eye, EyeOff, Check, Loader2, AlertCircle } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const email = route.query.email || ''
const codigo = route.query.codigo || ''

const novaSenha = ref('')
const confirmarSenha = ref('')
const mostrarSenha = ref(false)
const erro = ref('')
const carregando = ref(false)

const senhasIncompativeis = computed(() =>
  confirmarSenha.value.length > 0 && novaSenha.value !== confirmarSenha.value
)

async function salvar() {
  if (senhasIncompativeis.value) return
  erro.value = ''
  carregando.value = true
  try {
    await api.post('/auth/nova-senha', { email, codigo, nova_senha: novaSenha.value })
    router.push({ name: 'login', query: { senhaAtualizada: '1' } })
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao salvar nova senha.'
  } finally {
    carregando.value = false
  }
}
</script>
