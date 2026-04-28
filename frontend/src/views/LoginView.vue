<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 px-4">
    <div class="bg-white w-full max-w-sm rounded-2xl shadow-lg p-8">

      <!-- Header -->
      <div class="text-center mb-6">
        <div class="flex justify-center mb-3">
          <div class="bg-primary-50 p-3 rounded-full">
            <Sprout class="w-8 h-8 text-primary-600" />
          </div>
        </div>
        <h2 class="text-xl font-bold text-primary-600">Sistema de Gestão de Assentamentos</h2>
        <p class="text-gray-500 text-sm mt-1">
          Secretaria de Agricultura<br>Canaã dos Carajás
        </p>
      </div>

      <!-- Email -->
      <div class="mb-4">
        <label class="block text-xs font-medium text-gray-600 mb-1">E-mail</label>
        <div class="relative">
          <Mail class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            ref="inputEmail"
            type="email"
            placeholder="seu@email.com"
            autocomplete="username"
            class="w-full pl-9 pr-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600 focus:border-transparent" />
        </div>
      </div>

      <!-- Senha -->
      <div class="mb-2">
        <label class="block text-xs font-medium text-gray-600 mb-1">Senha</label>
        <div class="relative">
          <Lock class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            ref="inputSenha"
            type="password"
            placeholder="••••••••"
            autocomplete="current-password"
            @keydown.enter.prevent="entrar"
            :class="[
              'w-full pl-9 pr-3 py-2.5 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:border-transparent',
              senhaIncorreta
                ? 'border-red-400 focus:ring-red-400'
                : 'border-gray-300 focus:ring-primary-600'
            ]" />
        </div>
      </div>

      <!-- Link Esqueci minha senha -->
      <div class="flex justify-center mb-5">
        <router-link to="/recuperar-senha"
          class="text-xs text-primary-600 hover:text-primary-700 hover:underline transition-colors">
          Esqueci minha senha
        </router-link>
      </div>

      <!-- Botão -->
      <button type="button" @click="entrar" :disabled="carregando"
        class="w-full flex items-center justify-center gap-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-60 text-white font-semibold py-2.5 rounded-lg text-sm transition-colors cursor-pointer border-none">
        <Loader2 v-if="carregando" class="w-4 h-4 animate-spin" />
        <LogIn v-else class="w-4 h-4" />
        {{ carregando ? 'Conectando...' : 'Entrar' }}
      </button>

      <!-- Erro genérico -->
      <p v-if="erro && !senhaIncorreta"
        class="flex items-center justify-center gap-1.5 text-red-600 text-xs text-center mt-4">
        <AlertCircle class="w-3.5 h-3.5" />
        {{ erro }}
      </p>

      <!-- Erro de senha incorreta -->
      <div v-if="senhaIncorreta"
        class="mt-4 flex flex-col items-center gap-1 bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-center">
        <p class="flex items-center gap-1.5 text-red-600 text-xs font-medium">
          <AlertCircle class="w-3.5 h-3.5 shrink-0" />
          Senha incorreta.
        </p>
        <router-link to="/recuperar-senha"
          class="text-xs text-primary-600 hover:underline mt-0.5">
          Redefinir minha senha
        </router-link>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { Sprout, Mail, Lock, LogIn, Loader2, AlertCircle } from 'lucide-vue-next'

defineOptions({ name: 'LoginView' })

const inputEmail = ref(null)
const inputSenha = ref(null)
const erro = ref('')
const erroStatus = ref(null)
const carregando = ref(false)
const auth = useAuthStore()
const router = useRouter()

const senhaIncorreta = computed(() => erroStatus.value === 401)

onMounted(() => console.log('✅ LoginView MONTADO'))
onUnmounted(() => console.log('❌ LoginView DESMONTADO'))

async function entrar() {
  if (carregando.value) return

  // Lê os valores direto do DOM — sem reatividade
  const email = inputEmail.value?.value || ''
  const senha = inputSenha.value?.value || ''

  erro.value = ''
  erroStatus.value = null
  carregando.value = true

  const MAX_TENTATIVAS = 3
  const DELAY = 3000

  for (let tentativa = 1; tentativa <= MAX_TENTATIVAS; tentativa++) {
    try {
      await auth.login(email, senha)
      router.push('/produtores')
      return
    } catch (e) {
      const status = e.response?.status
      erroStatus.value = status

      if (status === 401 || status === 403) {
        erro.value = e.response?.data?.detail || 'E-mail ou senha incorretos.'
        console.log('🔴 Erro definido:', erro.value)
        break
      }

      if (tentativa === MAX_TENTATIVAS) {
        erro.value = 'Não foi possível conectar ao servidor. Tente novamente.'
        break
      }

      erro.value = `Servidor iniciando... tentativa ${tentativa}/${MAX_TENTATIVAS}`
      await new Promise(r => setTimeout(r, DELAY))
    }
  }

  carregando.value = false
}
</script>