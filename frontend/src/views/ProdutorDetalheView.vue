<template>
  <div class="max-w-3xl mx-auto px-6 py-10">

    <button
      @click="$router.back()"
      class="flex items-center gap-1.5 text-primary-600 hover:text-primary-700 text-sm mb-6 bg-transparent border-none cursor-pointer"
    >
      <ArrowLeft class="w-4 h-4" /> Voltar
    </button>

    <div v-if="produtor">

      <div class="flex items-center justify-between mb-5">
        <div class="flex items-center gap-3">
          <div class="bg-primary-50 p-3 rounded-full">
            <User class="w-6 h-6 text-primary-600" />
          </div>
          <h2 class="text-xl font-bold text-primary-600 uppercase">
            {{ produtor.nome_completo || 'Produtor' }}
          </h2>
        </div>

        <div class="flex gap-2">
          <button
            v-if="isAdmin && !editando"
            @click="iniciarEdicao"
            class="flex items-center gap-1.5 bg-primary-600 hover:bg-primary-700 text-white text-sm px-4 py-2 rounded-lg border-none cursor-pointer transition-colors"
          >
            <Pencil class="w-3.5 h-3.5" /> Editar
          </button>

          <template v-if="editando">
            <button
              @click="salvar"
              :disabled="salvando"
              class="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-60 text-white text-sm px-4 py-2 rounded-lg border-none cursor-pointer transition-colors"
            >
              <Loader2 v-if="salvando" class="w-3.5 h-3.5 animate-spin" />
              <Save v-else class="w-3.5 h-3.5" />
              {{ salvando ? 'Salvando...' : 'Salvar' }}
            </button>

            <button
              @click="cancelarEdicao"
              class="flex items-center gap-1.5 bg-white border border-gray-300 text-gray-600 hover:bg-gray-50 text-sm px-4 py-2 rounded-lg cursor-pointer transition-colors"
            >
              <X class="w-3.5 h-3.5" /> Cancelar
            </button>
          </template>
        </div>
      </div>

      <div
        v-if="erroSalvar"
        class="flex items-center gap-2 text-red-600 text-xs bg-red-50 border border-red-200 rounded-lg px-4 py-2.5 mb-4"
      >
        <AlertCircle class="w-4 h-4" /> {{ erroSalvar }}
      </div>

      <div
        v-if="sucessoSalvar"
        class="flex items-center gap-2 text-green-700 text-xs bg-green-50 border border-green-200 rounded-lg px-4 py-2.5 mb-4"
      >
        <CheckCircle class="w-4 h-4" /> Dados salvos com sucesso!
      </div>

      <div class="bg-white border border-gray-200 rounded-2xl p-7 mb-8 text-sm">

        <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-4">
          Dados Pessoais
        </h3>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <FieldEdit label="Nome Completo"      :editing="editando" v-model="form.nome_completo"    :value="produtor.nome_completo" />
          <FieldEdit label="CPF"                :editing="editando" v-model="form.cpf_beneficiario" :value="produtor.cpf_beneficiario" type="cpf" />
          <FieldEdit label="Data de Nascimento" :editing="editando" v-model="form.data_nascimento"  :value="produtor.data_nascimento" type="date" />
          <FieldEdit label="RG"                 :editing="editando" v-model="form.rg"               :value="produtor.rg" type="cpf" />
          <FieldEdit label="Órgão Emissor"      :editing="editando" v-model="form.orgao_emissor"    :value="produtor.orgao_emissor" />
          <FieldEdit label="Telefone"           :editing="editando" v-model="form.telefone"         :value="produtor.telefone" type="cpf" />
          <FieldEdit label="E-mail"             :editing="editando" v-model="form.email"            :value="produtor.email" type="email" />
        </div>

        <hr class="border-gray-100 my-6" />

        <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-4">
          Cônjuge
        </h3>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <FieldEdit label="Nome do Cônjuge" :editing="editando" v-model="form.conjuge_nome" :value="produtor.conjuge_nome" />
          <FieldEdit label="CPF do Cônjuge"  :editing="editando" v-model="form.cpf_conjuge"  :value="produtor.cpf_conjuge" type="cpf" />
        </div>

        <hr class="border-gray-100 my-6" />

        <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-4">
          Assentamento
        </h3>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div>
            <div class="text-xs text-gray-400 mb-1">Assentamento</div>
            <select
              v-if="editando"
              v-model="form.assentamento"
              class="w-full px-3 py-2 border border-primary-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600 uppercase"
            >
              <option value="">—</option>
              <option>PA BRASÍLIA</option>
              <option>PA MARIA DE LOURDES RODRIGUES</option>
              <option>PA MONTEPÍO</option>
              <option>PA UNIÃO AMEIRCO SANTANA</option>
            </select>
            <div v-else class="text-gray-700 uppercase">{{ produtor.assentamento || '—' }}</div>
          </div>

          <FieldEdit label="Lote"                :editing="editando" v-model="form.lote"                :value="produtor.lote" />
          <FieldEdit label="Comunidade"          :editing="editando" v-model="form.comunidade"          :value="produtor.comunidade" />
          <FieldEdit label="Código Beneficiário" :editing="editando" v-model="form.codigo_beneficiario" :value="produtor.codigo_beneficiario" />
          <FieldEdit label="Situação"            :editing="editando" v-model="form.situacao"            :value="produtor.situacao" />
          <FieldEdit label="Homologação"         :editing="editando" v-model="form.data_homologacao"    :value="produtor.data_homologacao" type="date" />
          <FieldEdit label="Área do Lote (ha)"   :editing="editando" v-model="form.area_lote_ha"        :value="produtor.area_lote_ha" type="number" />
          <FieldEdit label="Atividade Principal" :editing="editando" v-model="form.atividade_principal" :value="produtor.atividade_principal" />
        </div>

        <hr class="border-gray-100 my-6" />

        <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-4">
          Endereço
        </h3>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <FieldEdit label="Endereço"  :editing="editando" v-model="form.endereco"  :value="produtor.endereco" />
          <FieldEdit label="CEP"       :editing="editando" v-model="form.cep"       :value="produtor.cep" type="cpf" />
          <FieldEdit label="Município" :editing="editando" v-model="form.municipio" :value="produtor.municipio" />
          <FieldEdit label="UF"        :editing="editando" v-model="form.uf"        :value="produtor.uf" />
        </div>

        <hr class="border-gray-100 my-6" />

        <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-4">
          DAP / CAF
        </h3>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <FieldEdit label="DAP/CAF"      :editing="editando" v-model="form.dap_caf"      :value="produtor.dap_caf" />
          <FieldEdit label="Data DAP/CAF" :editing="editando" v-model="form.data_dap_caf" :value="produtor.data_dap_caf" type="date" />
        </div>

      </div>

      <!-- Programas de Fomento -->
      <h3 class="font-semibold text-gray-700 mb-4 flex items-center gap-2">
        <ClipboardList class="w-5 h-5 text-primary-600" /> Selecionar Programa de Fomento
      </h3>

      <div v-if="carregandoFomentos" class="flex items-center gap-2 text-gray-400 text-sm py-6">
        <Loader2 class="w-4 h-4 animate-spin" /> Carregando fomentos...
      </div>

      <div
        v-else-if="fomentos.length === 0"
        class="flex flex-col items-center justify-center text-gray-400 py-8 gap-2 border border-dashed border-gray-200 rounded-xl mb-8"
      >
        <ClipboardList class="w-7 h-7 opacity-30" />
        <p class="text-sm">Nenhum programa de fomento cadastrado.</p>
      </div>

      <div v-else>
        <div
          v-for="f in fomentos"
          :key="f.id"
          @click.stop="irParaFormulario(f.id)"
          class="bg-white border border-gray-200 hover:border-primary-600 rounded-xl px-5 py-4 mb-3 cursor-pointer transition-colors"
        >
          <strong class="text-primary-600 text-sm">{{ f.nome }}</strong>
          <p class="text-gray-400 text-xs mt-1">{{ f.descricao }}</p>
        </div>
      </div>

      <hr class="border-gray-100 my-8" />

      <!-- Rascunhos -->
      <RascunhosProdutor
        :produtor-id="produtorId"
        :produtor="produtor"
        :fomentos="fomentos"
        :submissoes-iniciais="submissoes"
      />

    </div>

    <div v-else class="flex items-center justify-center gap-2 text-gray-400 py-24">
      <Loader2 class="w-5 h-5 animate-spin" /> Carregando...
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'
import FieldEdit from '../components/FieldEdit.vue'
import RascunhosProdutor from '../components/RascunhosProdutor.vue'
import {
  ArrowLeft, User, Pencil, Save, X, Loader2,
  AlertCircle, CheckCircle, ClipboardList
} from 'lucide-vue-next'

const auth = useAuthStore()
const isAdmin = computed(() => auth.eSuperusuario)

const route = useRoute()
const router = useRouter()
const produtorId = route.params.id

const produtor = ref(null)
const fomentos = ref([])
const submissoes = ref([])
const carregandoFomentos = ref(false)
const editando = ref(false)
const salvando = ref(false)
const erroSalvar = ref('')
const sucessoSalvar = ref(false)
const form = ref({})

function irParaFormulario(fomentoId) {
  router.push(`/formulario/${produtorId}/${fomentoId}`)
}

function iniciarEdicao() {
  form.value = { ...produtor.value }
  erroSalvar.value = ''
  sucessoSalvar.value = false
  editando.value = true
}

function cancelarEdicao() {
  editando.value = false
  erroSalvar.value = ''
}

async function salvar() {
  salvando.value = true
  erroSalvar.value = ''
  sucessoSalvar.value = false

  try {
    const { data } = await api.patch(`/produtores/${produtorId}`, form.value)
    produtor.value = data
    editando.value = false
    sucessoSalvar.value = true
    setTimeout(() => (sucessoSalvar.value = false), 3000)
  } catch (err) {
    erroSalvar.value = err.response?.data?.detail || 'Erro ao salvar.'
  } finally {
    salvando.value = false
  }
}

onMounted(async () => {
  try {
    const p = await api.get(`/produtores/${produtorId}`)
    produtor.value = p.data
  } catch (err) {
    console.error('Erro ao carregar produtor:', err)
  }

  carregandoFomentos.value = true
  try {
    const f = await api.get('/fomentos')
    fomentos.value = f.data
  } catch (err) {
    console.error('Erro ao carregar fomentos:', err)
  } finally {
    carregandoFomentos.value = false
  }

  try {
    const s = await api.get('/submissoes', {
      params: { produtor_id: produtorId }
    })
    submissoes.value = s.data
  } catch (err) {
    console.error('Erro ao carregar submissões:', err)
    submissoes.value = []
  }
})
</script>
