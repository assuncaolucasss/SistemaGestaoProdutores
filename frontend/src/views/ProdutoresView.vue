<template>
  <div class="max-w-4xl mx-auto px-6 py-10">

    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-primary-600">Produtores Cadastrados</h2>
      <button v-if="isAdmin" @click="abrirModalNovo"
        class="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors cursor-pointer border-none">
        <UserPlus class="w-4 h-4" /> Novo Produtor
      </button>
    </div>

    <!-- Filtros -->
    <div class="flex flex-col sm:flex-row gap-3 mb-6">
      <div class="relative flex-1">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input v-model="busca" @input="onBusca" placeholder="Buscar por nome, CPF, lote ou comunidade..."
          class="w-full pl-9 pr-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600 focus:border-transparent" />
      </div>
      <select v-model="assentamentoFiltro" @change="onFiltro"
  class="py-2.5 px-3 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600 focus:border-transparent uppercase">
  <option value="">Todos os assentamentos</option>
  <option value="PA BRASÍLIA">PA BRASÍLIA</option>
  <option value="PA MARIA DE LOURDES RODRIGUES">PA MARIA DE LOURDES RODRIGUES</option>
  <option value="PA MONTEPÍO">PA MONTEPÍO</option>
  <option value="PA UNIÃO AMEIRCO SANTANA">PA UNIÃO AMERICO SANTANA</option>
</select>
    </div>

    <!-- Loading -->
    <div v-if="carregando" class="flex items-center justify-center gap-2 text-gray-400 py-16">
      <Loader2 class="w-5 h-5 animate-spin" /> Carregando...
    </div>

    <div v-else>
      <!-- Contagem -->
      <p class="text-xs text-gray-400 mb-3">
        {{ total }} produtor(es) encontrado(s) — página {{ paginaAtual }} de {{ totalPaginas }}
      </p>

      <div v-for="p in produtores" :key="p.id"
        class="bg-white border border-gray-200 rounded-xl px-5 py-4 mb-3 hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between gap-4">
          <div class="flex-1 cursor-pointer" @click="$router.push(`/produtores/${p.id}`)">
            <span class="font-semibold text-primary-600 uppercase">{{ p.nome_completo || 'Nome não informado' }}</span>
            <span class="text-gray-400 text-xs ml-3">CPF: {{ formatarCPF(p.cpf_beneficiario) }}</span>
          </div>
          <div class="flex items-center gap-3">
            <div class="text-right">
              <span class="bg-primary-50 text-primary-600 text-xs px-3 py-1 rounded-full uppercase">
                {{ p.assentamento || 'Assentamento não informado' }}
              </span>
              <div class="text-gray-400 text-xs mt-1 uppercase">Lote: {{ p.lote || '—' }}</div>
            </div>
            <button v-if="isAdmin" @click.stop="confirmarRemocao(p)"
              class="flex items-center gap-1 bg-red-50 hover:bg-red-100 text-red-700 text-xs px-3 py-1.5 rounded-lg transition-colors cursor-pointer border-none">
              <Trash2 class="w-3.5 h-3.5" /> Remover
            </button>
          </div>
        </div>
      </div>

      <div v-if="produtores.length === 0" class="flex flex-col items-center justify-center text-gray-400 py-16 gap-2">
        <Users class="w-10 h-10 opacity-30" />
        <p class="text-sm">Nenhum produtor encontrado.</p>
      </div>

      <!-- Paginação -->
      <div v-if="totalPaginas > 1" class="flex items-center justify-center gap-2 mt-6">
        <button @click="irPara(paginaAtual - 1)" :disabled="paginaAtual === 1"
          class="flex items-center gap-1 px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer bg-white transition-colors">
          <ChevronLeft class="w-4 h-4" /> Anterior
        </button>

        <div class="flex gap-1">
          <button v-for="p in paginasVisiveis" :key="p"
            @click="typeof p === 'number' && irPara(p)"
            :disabled="p === '...'"
            :class="[
              'px-3 py-2 rounded-lg text-sm font-medium transition-colors',
              p === paginaAtual
                ? 'bg-primary-600 text-white border border-primary-600'
                : p === '...'
                  ? 'text-gray-400 cursor-default bg-transparent border-none'
                  : 'border border-gray-300 text-gray-600 hover:bg-gray-50 cursor-pointer bg-white'
            ]">
            {{ p }}
          </button>
        </div>

        <button @click="irPara(paginaAtual + 1)" :disabled="paginaAtual === totalPaginas"
          class="flex items-center gap-1 px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer bg-white transition-colors">
          Próximo <ChevronRight class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Modal Novo Produtor -->
    <div v-if="modalAberto" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-md max-h-[90vh] overflow-y-auto p-8">
        <div class="flex items-center gap-2 mb-6">
          <div class="bg-primary-50 p-2 rounded-full">
            <UserPlus class="w-5 h-5 text-primary-600" />
          </div>
          <h3 class="text-lg font-bold text-primary-600">Novo Produtor</h3>
        </div>
        <div class="flex flex-col gap-3">
          <input v-model="form.nome_completo"
            @input="form.nome_completo = form.nome_completo.toUpperCase()"
            placeholder="NOME COMPLETO *"
            class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm uppercase focus:outline-none focus:ring-2 focus:ring-primary-600" />
          <input
            v-model="form.cpf_beneficiario"
            @input="form.cpf_beneficiario = formatarCPF(form.cpf_beneficiario)"
            placeholder="CPF (XXX.XXX.XXX-XX)"
            maxlength="14"
            class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600" />
          <input v-model="form.codigo_beneficiario"
            @input="form.codigo_beneficiario = form.codigo_beneficiario.toUpperCase()"
            placeholder="CÓDIGO DO BENEFICIÁRIO"
            class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm uppercase focus:outline-none focus:ring-2 focus:ring-primary-600" />
          <select v-model="form.assentamento"
            class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm uppercase focus:outline-none focus:ring-2 focus:ring-primary-600">
            <option value="">SELECIONE O ASSENTAMENTO *</option>
            <option>PA BRASÍLIA</option>
            <option>PA MARIA DE LOURDES RODRIGUES</option>
            <option>PA MONTEPÍO</option>
            <option>PA UNIÃO AMEIRCO SANTANA</option>
          </select>
          <input v-model="form.lote"
            @input="form.lote = form.lote.toUpperCase()"
            placeholder="LOTE"
            class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm uppercase focus:outline-none focus:ring-2 focus:ring-primary-600" />
          <input v-model="form.situacao"
            @input="form.situacao = form.situacao.toUpperCase()"
            placeholder="SITUAÇÃO"
            class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm uppercase focus:outline-none focus:ring-2 focus:ring-primary-600" />
          <input v-model="form.telefone"
            placeholder="Telefone"
            class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600" />
          <input v-model="form.email"
            placeholder="E-mail"
            class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600" />
        </div>
        <p v-if="erroModal" class="flex items-center gap-1.5 text-red-600 text-xs mt-3">
          <AlertCircle class="w-3.5 h-3.5" /> {{ erroModal }}
        </p>
        <div class="flex gap-3 mt-6 justify-end">
          <button @click="modalAberto = false"
            class="px-5 py-2 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 cursor-pointer bg-white transition-colors">
            Cancelar
          </button>
          <button @click="salvarProdutor" :disabled="salvando"
            class="flex items-center gap-2 px-5 py-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-60 text-white text-sm font-semibold rounded-lg cursor-pointer border-none transition-colors">
            <Loader2 v-if="salvando" class="w-4 h-4 animate-spin" />
            <Save v-else class="w-4 h-4" />
            {{ salvando ? 'Salvando...' : 'Salvar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal confirmar remoção -->
    <div v-if="produtorParaRemover" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-8 text-center">
        <div class="flex justify-center mb-4">
          <div class="bg-red-50 p-4 rounded-full">
            <Trash2 class="w-7 h-7 text-red-500" />
          </div>
        </div>
        <h3 class="text-lg font-bold text-gray-700 mb-2">Remover produtor?</h3>
        <p class="text-gray-400 text-sm mb-6">
          Tem certeza que deseja remover
          <strong class="text-gray-600 uppercase">{{ produtorParaRemover.nome_completo || 'este produtor' }}</strong>?
          Esta ação não pode ser desfeita.
        </p>
        <div class="flex gap-3">
          <button @click="produtorParaRemover = null"
            class="flex-1 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 cursor-pointer bg-white transition-colors">
            Cancelar
          </button>
          <button @click="executarRemocao" :disabled="removendo"
            class="flex-1 flex items-center justify-center gap-2 py-2.5 bg-red-600 hover:bg-red-700 disabled:opacity-60 text-white text-sm font-semibold rounded-lg border-none cursor-pointer transition-colors">
            <Loader2 v-if="removendo" class="w-4 h-4 animate-spin" />
            <Trash2 v-else class="w-4 h-4" />
            {{ removendo ? 'Removendo...' : 'Remover' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'
import {
  Search, UserPlus, Users, Trash2, Loader2,
  Save, AlertCircle, ChevronLeft, ChevronRight
} from 'lucide-vue-next'

const auth    = useAuthStore()
const isAdmin = computed(() => auth.eSuperusuario)

const produtores          = ref([])
const busca               = ref('')
const assentamentoFiltro  = ref('')
const carregando          = ref(true)
const modalAberto         = ref(false)
const salvando            = ref(false)
const erroModal           = ref('')
const produtorParaRemover = ref(null)
const removendo           = ref(false)

const POR_PAGINA  = 15
const paginaAtual = ref(1)
const total       = ref(0)

const totalPaginas = computed(() => Math.max(1, Math.ceil(total.value / POR_PAGINA)))

const paginasVisiveis = computed(() => {
  const t = totalPaginas.value
  const c = paginaAtual.value
  if (t <= 7) return Array.from({ length: t }, (_, i) => i + 1)
  if (c <= 4) return [1, 2, 3, 4, 5, '...', t]
  if (c >= t - 3) return [1, '...', t - 4, t - 3, t - 2, t - 1, t]
  return [1, '...', c - 1, c, c + 1, '...', t]
})

const formVazio = () => ({
  nome_completo: '', cpf_beneficiario: '', codigo_beneficiario: '',
  assentamento: '', lote: '', situacao: '', telefone: '', email: '',
})
const form = ref(formVazio())

// ── Formata CPF: aceita com ou sem máscara, sempre retorna XXX.XXX.XXX-XX ──
function formatarCPF(valor) {
  if (!valor) return ''
  const nums = String(valor).replace(/\D/g, '').slice(0, 11)
  return nums
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d{1,2})$/, '$1-$2')
}

let debounceTimer = null

async function buscar() {
  carregando.value = true
  try {
    const params = {
      limit: POR_PAGINA,
      skip: (paginaAtual.value - 1) * POR_PAGINA,
    }
    if (busca.value)              params.busca        = busca.value
    if (assentamentoFiltro.value) params.assentamento = assentamentoFiltro.value

    const [lista, tot] = await Promise.all([
      api.get('/produtores/', { params }),
      api.get('/produtores/total', { params: {
        busca: busca.value || undefined,
        assentamento: assentamentoFiltro.value || undefined,
      }}),
    ])
    produtores.value = lista.data
    total.value      = tot.data
  } catch (err) {
    console.error('Erro ao buscar produtores:', err)
    produtores.value = []
  } finally {
    carregando.value = false
  }
}

function onBusca() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    paginaAtual.value = 1
    buscar()
  }, 350)
}

function onFiltro() {
  paginaAtual.value = 1
  buscar()
}

function irPara(pagina) {
  if (pagina < 1 || pagina > totalPaginas.value) return
  paginaAtual.value = pagina
  buscar()
}

function abrirModalNovo() {
  form.value      = formVazio()
  erroModal.value = ''
  modalAberto.value = true
}

async function salvarProdutor() {
  if (!form.value.nome_completo || !form.value.assentamento) {
    erroModal.value = 'Nome completo e assentamento são obrigatórios.'
    return
  }
  salvando.value  = true
  erroModal.value = ''
  try {
    await api.post('/produtores/', form.value)
    modalAberto.value = false
    paginaAtual.value = 1
    await buscar()
  } catch (err) {
    erroModal.value = err.response?.data?.detail || 'Erro ao salvar produtor.'
  } finally {
    salvando.value = false
  }
}

function confirmarRemocao(p) {
  produtorParaRemover.value = p
}

async function executarRemocao() {
  removendo.value = true
  try {
    await api.delete(`/produtores/${produtorParaRemover.value.id}`)
    produtorParaRemover.value = null
    await buscar()
  } catch (err) {
    alert(err.response?.data?.detail || 'Erro ao remover produtor.')
  } finally {
    removendo.value = false
  }
}

onMounted(buscar)
</script>
