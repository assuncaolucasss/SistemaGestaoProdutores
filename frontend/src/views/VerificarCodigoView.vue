<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 px-4">
    <div class="bg-white w-full max-w-sm rounded-2xl shadow-lg p-8">

      <!-- Header -->
      <div class="text-center mb-6">
        <div class="flex justify-center mb-3">
          <div class="bg-primary-50 p-3 rounded-full">
            <ShieldCheck class="w-8 h-8 text-primary-600" />
          </div>
        </div>
        <h2 class="text-xl font-bold text-primary-600">Verificar Código</h2>
        <p class="text-gray-500 text-sm mt-1">
          Código enviado para<br>
          <span class="font-medium text-gray-700">{{ email }}</span>
        </p>
        <!-- Timer -->
        <p :class="['text-xs mt-2 font-medium', expirado ? 'text-red-500' : 'text-primary-600']">
          <Clock class="w-3.5 h-3.5 inline mr-1" />
          {{ expirado ? 'Código expirado' : `Expira em ${minutos}:${segundos}` }}
        </p>
      </div>

      <!-- Inputs do código -->
      <div class="flex justify-center gap-2 mb-6">
        <input
          v-for="(_, i) in 6"
          :key="i"
          :ref="el => inputs[i] = el"
          v-model="digitos[i]"
          type="text"
          inputmode="numeric"
          maxlength="1"
          @input="onInput(i)"
          @keydown.backspace="onBackspace(i)"
          @paste.prevent="onPaste($event)"
          :class="[
            'w-10 h-12 text-center text-lg font-bold border rounded-lg focus:outline-none focus:ring-2 focus:border-transparent transition-colors',
            erroDigitos
              ? 'border-red-400 focus:ring-red-400 text-red-600'
              : 'border-gray-300 focus:ring-primary-600'
          ]"
        />
      </div>

      <!-- Botão -->
      <button @click="verificar" :disabled="carregando || expirado || codigoIncompleto"
        class="w-full flex items-center justify-center gap-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-60 text-white font-semibold py-2.5 rounded-lg text-sm transition-colors cursor-pointer border-none">
        <Loader2 v-if="carregando" class="w-4 h-4 animate-spin" />
        <ShieldCheck v-else class="w-4 h-4" />
        {{ carregando ? 'Verificando...' : 'Verificar código' }}
      </button>

      <!-- Erro -->
      <p v-if="erro" class="flex items-center justify-center gap-1.5 text-red-600 text-xs text-center mt-4">
        <AlertCircle class="w-3.5 h-3.5" />
        {{ erro }}
      </p>

      <!-- Reenviar -->
      <div class="flex justify-center mt-5">
        <button @click="reenviar" :disabled="!expirado && tempoRestante > 0"
          class="flex items-center gap-1 text-xs text-gray-500 hover:text-primary-600 disabled:opacity-40 transition-colors cursor-pointer border-none bg-transparent">
          <RefreshCw class="w-3.5 h-3.5" />
          Reenviar código
        </button>
      </div>

      <!-- Voltar -->
      <div class="flex justify-center mt-3">
        <router-link to="/recuperar-senha"
          class="flex items-center gap-1 text-xs text-gray-500 hover:text-primary-600 transition-colors">
          <ArrowLeft class="w-3.5 h-3.5" />
          Trocar e-mail
        </router-link>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../services/api'
import { ShieldCheck, Clock, Loader2, AlertCircle, RefreshCw, ArrowLeft } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const email = route.query.email || ''

const digitos = ref(Array(6).fill(''))
const inputs = ref([])
const erro = ref('')
const erroDigitos = ref(false)
const carregando = ref(false)

// Timer — 5 minutos
const DURACAO = 5 * 60
const tempoRestante = ref(DURACAO)
let intervalo = null

const expirado = computed(() => tempoRestante.value <= 0)
const minutos = computed(() => String(Math.floor(tempoRestante.value / 60)).padStart(2, '0'))
const segundos = computed(() => String(tempoRestante.value % 60).padStart(2, '0'))
const codigoIncompleto = computed(() => digitos.value.some(d => d === ''))

function iniciarTimer() {
  tempoRestante.value = DURACAO
  clearInterval(intervalo)
  intervalo = setInterval(() => {
    if (tempoRestante.value > 0) tempoRestante.value--
    else clearInterval(intervalo)
  }, 1000)
}

onMounted(() => {
  iniciarTimer()
  inputs.value[0]?.focus()
})
onUnmounted(() => clearInterval(intervalo))

function onInput(i) {
  erroDigitos.value = false
  digitos.value[i] = digitos.value[i].replace(/\D/g, '')
  if (digitos.value[i] && i < 5) inputs.value[i + 1]?.focus()
}

function onBackspace(i) {
  if (!digitos.value[i] && i > 0) {
    digitos.value[i - 1] = ''
    inputs.value[i - 1]?.focus()
  }
}

function onPaste(e) {
  const texto = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6)
  texto.split('').forEach((c, i) => { digitos.value[i] = c })
  inputs.value[Math.min(texto.length, 5)]?.focus()
}

async function verificar() {
  erro.value = ''
  erroDigitos.value = false
  carregando.value = true
  const codigo = digitos.value.join('')
  try {
    await api.post('/auth/verificar-codigo', { email, codigo })
    router.push({ name: 'nova-senha', query: { email, codigo } })
  } catch (e) {
    erroDigitos.value = true
    erro.value = e.response?.data?.detail || 'Código inválido ou expirado.'
  } finally {
    carregando.value = false
  }
}

async function reenviar() {
  digitos.value = Array(6).fill('')
  erro.value = ''
  erroDigitos.value = false
  try {
    await api.post('/auth/recuperar-senha', { email })
    iniciarTimer()
    inputs.value[0]?.focus()
  } catch (e) {
    erro.value = 'Erro ao reenviar código.'
  }
}
</script>
