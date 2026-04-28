<template>
  <div class="max-w-4xl mx-auto px-6 py-10">

    <button @click="$router.back()"
      class="flex items-center gap-1.5 text-primary-600 hover:text-primary-700 text-sm mb-6 bg-transparent border-none cursor-pointer">
      <ArrowLeft class="w-4 h-4" /> Voltar
    </button>

    <div v-if="produtor && fomento" class="bg-white border border-gray-200 rounded-2xl p-8">

      <!-- Cabeçalho -->
      <div class="flex items-center justify-between mb-2">
        <div>
          <p class="text-xs text-gray-400 uppercase tracking-widest mb-0.5">
            {{ produtor.codigo_beneficiario || produtorId }}
          </p>
          <h2 class="text-xl font-bold text-primary-600 uppercase">{{ fomento.nome }}</h2>
        </div>
        <button @click="emitirPDF" :disabled="gerandoPDF"
          class="flex items-center gap-2 bg-primary-50 hover:bg-primary-100 border border-primary-600 text-primary-600 text-sm font-semibold px-4 py-2 rounded-lg cursor-pointer disabled:opacity-60 transition-colors">
          <Loader2 v-if="gerandoPDF" class="w-4 h-4 animate-spin" />
          <FileText v-else class="w-4 h-4" />
          {{ gerandoPDF ? 'Gerando...' : 'Emitir PDF' }}
        </button>
      </div>
      <hr class="border-gray-100 mb-6" />

      <!-- Dados do beneficiário -->
      <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-4">Dados do Beneficiário</h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm mb-6">
        <div><span class="text-gray-400 text-xs">Beneficiário</span><p class="font-medium text-gray-700 uppercase">{{ produtor.nome_completo }}</p></div>
        <div><span class="text-gray-400 text-xs">CPF</span><p class="font-medium text-gray-700">{{ produtor.cpf_beneficiario }}</p></div>
        <div><span class="text-gray-400 text-xs">Cônjuge</span><p class="font-medium text-gray-700 uppercase">{{ produtor.conjuge_nome || '—' }}</p></div>
        <div><span class="text-gray-400 text-xs">CPF Cônjuge</span><p class="font-medium text-gray-700">{{ produtor.cpf_conjuge || '—' }}</p></div>
        <div><span class="text-gray-400 text-xs">Assentamento</span><p class="font-medium text-gray-700 uppercase">{{ produtor.assentamento }}</p></div>
        <div><span class="text-gray-400 text-xs">Lote</span><p class="font-medium text-gray-700 uppercase">{{ produtor.lote }}</p></div>
      </div>

      <hr class="border-gray-100 mb-6" />

      <!-- Campos do formulário -->
      <div class="flex flex-col gap-4 mb-6">

        <!-- Seletor cascata -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="text-xs font-medium text-gray-600 mb-1 block">Modalidade</label>
            <select v-model="form.classe_id"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600">
              <option :value="null">Selecione a classe...</option>
              <option v-for="c in hierarquia" :key="c.classe.id" :value="c.classe.id">
                {{ c.classe.nome }} ({{ c.classe.escopo.toUpperCase() }})
              </option>
            </select>
          </div>
          <div>
            <label class="text-xs font-medium text-gray-600 mb-1 block">Submodalidade</label>
            <select v-model="form.subclasse_id" :disabled="!form.classe_id"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600 disabled:opacity-50">
              <option :value="null">Selecione a subclasse...</option>
              <option v-for="si in subclassesDaClasse" :key="si.subclasse.id" :value="si.subclasse.id">
                {{ si.subclasse.nome }}
              </option>
            </select>
          </div>
        </div>

        <!-- Badge carregamento -->
        <div v-if="carregandoCaracteristica"
          class="flex items-center gap-2 text-gray-500 text-xs bg-gray-50 border border-gray-200 rounded-lg px-3 py-2">
          <Loader2 class="w-3.5 h-3.5 animate-spin" /> Carregando características...
        </div>
        <div v-else-if="caracteristicaCarregada"
          class="flex items-center gap-2 text-green-700 text-xs bg-green-50 border border-green-200 rounded-lg px-3 py-2">
          <CheckCircle class="w-3.5 h-3.5" />
          Justificativa e memória de cálculo pré-preenchidas automaticamente.
        </div>

        <!-- Segundo beneficiário -->
        <div v-if="eFomentoJovem" class="bg-amber-50 border border-amber-300 rounded-xl p-5">
          <h3 class="text-sm font-semibold text-amber-700 mb-4 flex items-center gap-2">
            <UserPlus class="w-4 h-4" /> Segundo Beneficiário
          </h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="text-xs font-medium text-gray-600 mb-1 block">Nome Completo *</label>
              <input v-model="form.segundo_beneficiario_nome"
                @input="form.segundo_beneficiario_nome = form.segundo_beneficiario_nome.toUpperCase()"
                placeholder="NOME DO BENEFICIÁRIO"
                class="w-full px-3 py-2.5 border border-amber-300 rounded-lg text-sm uppercase focus:outline-none focus:ring-2 focus:ring-amber-400" />
            </div>
            <div>
              <label class="text-xs font-medium text-gray-600 mb-1 block">CPF *</label>
              <input v-model="form.segundo_beneficiario_cpf"
                @input="form.segundo_beneficiario_cpf = formatarCPF(form.segundo_beneficiario_cpf)"
                placeholder="000.000.000-00" maxlength="14"
                class="w-full px-3 py-2.5 border border-amber-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-amber-400" />
            </div>
          </div>
        </div>

        <!-- Entidade responsável -->
        <div>
          <label class="text-xs font-medium text-gray-600 mb-1 block">Entidade Responsável pela Elaboração do Projeto</label>
          <input v-model="form.entidade_elaboracao"
            @input="form.entidade_elaboracao = form.entidade_elaboracao.toUpperCase()"
            placeholder="EX: EMATER, SINDICATO RURAL, INCRA..."
            class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm uppercase focus:outline-none focus:ring-2 focus:ring-primary-600" />
        </div>
        <div>
          <textarea v-model="form.texto_entidade_responsavel"
            @input="form.texto_entidade_responsavel = form.texto_entidade_responsavel.toUpperCase()"
            rows="3" placeholder="TEXTO ADICIONAL SOBRE A ENTIDADE RESPONSÁVEL..."
            class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm uppercase focus:outline-none focus:ring-2 focus:ring-primary-600 resize-y" />
        </div>

        <!-- Justificativa -->
        <div>
          <label class="text-xs font-medium text-gray-600 mb-1 block">Justificativa do Projeto Produtivo</label>
          <textarea v-model="form.justificativa"
            @input="form.justificativa = form.justificativa.toUpperCase()"
            rows="4"
            class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm uppercase focus:outline-none focus:ring-2 focus:ring-primary-600 resize-y" />
        </div>

      </div>

      <!-- Tabela de investimentos -->
      <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">Memória de Cálculo — Investimentos</h3>
      <div class="overflow-x-auto mb-4">
        <table class="w-full text-sm border-collapse">
          <thead>
            <tr class="bg-gray-50 text-gray-500 text-xs">
              <th class="text-left px-3 py-2.5 border border-gray-200">Discriminação</th>
              <th class="text-center px-3 py-2.5 border border-gray-200 w-20">Qtd</th>
              <th class="text-center px-3 py-2.5 border border-gray-200 w-28">Vlr Unitário</th>
              <th class="text-center px-3 py-2.5 border border-gray-200 w-28">Subtotal</th>
              <th class="w-10 border-none bg-transparent"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, i) in form.itens_investimento" :key="i">
              <td class="border border-gray-200 p-1">
                <input v-model="item.discriminacao"
                  @input="item.discriminacao = item.discriminacao.toUpperCase()"
                  class="w-full px-2 py-1.5 text-sm border-none outline-none uppercase" />
              </td>
              <td class="border border-gray-200 p-1">
                <input v-model.number="item.quantidade" type="number" @input="calcularSubtotal(item)"
                  class="w-full px-2 py-1.5 text-sm border-none outline-none text-center" />
              </td>
              <td class="border border-gray-200 p-1">
                <input v-model.number="item.valor_unitario" type="number" @input="calcularSubtotal(item)"
                  class="w-full px-2 py-1.5 text-sm border-none outline-none text-center" />
              </td>
              <td class="border border-gray-200 p-1 text-center text-primary-600 font-semibold text-xs">
                R$ {{ (item.subtotal || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}
              </td>
              <td class="border-none p-1 text-center">
                <button @click="form.itens_investimento.splice(i, 1)"
                  class="text-red-400 hover:text-red-600 bg-transparent border-none cursor-pointer p-1">
                  <X class="w-3.5 h-3.5" />
                </button>
              </td>
            </tr>
            <tr v-if="!form.itens_investimento.length">
              <td colspan="5" class="text-center text-gray-400 text-xs py-4 border border-dashed border-gray-200">
                Nenhum item adicionado.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <button @click="adicionarItem('investimento')"
        class="flex items-center gap-1.5 bg-primary-50 hover:bg-primary-100 border border-primary-600 text-primary-600 text-xs px-3 py-2 rounded-lg cursor-pointer mb-8 transition-colors">
        <Plus class="w-3.5 h-3.5" /> Adicionar item
      </button>

      <!-- Tabela de mão de obra -->
      <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">Mão de Obra Especializada</h3>
      <div class="overflow-x-auto mb-4">
        <table class="w-full text-sm border-collapse">
          <thead>
            <tr class="bg-gray-50 text-gray-500 text-xs">
              <th class="text-left px-3 py-2.5 border border-gray-200">Descrição</th>
              <th class="text-center px-3 py-2.5 border border-gray-200 w-20">Qtd</th>
              <th class="text-center px-3 py-2.5 border border-gray-200 w-28">Vlr Unitário</th>
              <th class="text-center px-3 py-2.5 border border-gray-200 w-28">Subtotal</th>
              <th class="w-10 border-none bg-transparent"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, i) in form.itens_mao_obra" :key="i">
              <td class="border border-gray-200 p-1">
                <input v-model="item.descricao"
                  @input="item.descricao = item.descricao.toUpperCase()"
                  class="w-full px-2 py-1.5 text-sm border-none outline-none uppercase" />
              </td>
              <td class="border border-gray-200 p-1">
                <input v-model.number="item.qtd" type="number" @input="calcularSubtotalMao(item)"
                  class="w-full px-2 py-1.5 text-sm border-none outline-none text-center" />
              </td>
              <td class="border border-gray-200 p-1">
                <input v-model.number="item.valor_unitario" type="number" @input="calcularSubtotalMao(item)"
                  class="w-full px-2 py-1.5 text-sm border-none outline-none text-center" />
              </td>
              <td class="border border-gray-200 p-1 text-center text-primary-600 font-semibold text-xs">
                R$ {{ (item.subtotal || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}
              </td>
              <td class="border-none p-1 text-center">
                <button @click="form.itens_mao_obra.splice(i, 1)"
                  class="text-red-400 hover:text-red-600 bg-transparent border-none cursor-pointer p-1">
                  <X class="w-3.5 h-3.5" />
                </button>
              </td>
            </tr>
            <tr v-if="!form.itens_mao_obra.length">
              <td colspan="5" class="text-center text-gray-400 text-xs py-4 border border-dashed border-gray-200">
                Nenhum item adicionado.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <button @click="adicionarItem('mao_obra')"
        class="flex items-center gap-1.5 bg-primary-50 hover:bg-primary-100 border border-primary-600 text-primary-600 text-xs px-3 py-2 rounded-lg cursor-pointer mb-8 transition-colors">
        <Plus class="w-3.5 h-3.5" /> Adicionar item
      </button>

      <!-- Município e Data -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
        <div>
          <label class="text-xs font-medium text-gray-600 mb-1 block">Município</label>
          <input v-model="form.municipio_data"
            @input="form.municipio_data = form.municipio_data.toUpperCase()"
            placeholder="EX: CANAÃ DOS CARAJÁS"
            class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm uppercase focus:outline-none focus:ring-2 focus:ring-primary-600" />
        </div>
        <div>
          <label class="text-xs font-medium text-gray-600 mb-1 block">Data</label>
          <input v-model="form.data_assinatura" type="date"
            class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600" />
        </div>
      </div>

      <!-- Total -->
      <div class="bg-primary-50 border border-primary-600 rounded-xl px-6 py-4 text-right mb-6">
        <span class="text-primary-600 font-bold text-base">
          TOTAL FINAL: R$ {{ totalFinal.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}
        </span>
      </div>

      <!-- Alertas -->
      <div v-if="erro" class="flex items-center gap-2 text-red-600 text-xs bg-red-50 border border-red-200 rounded-lg px-4 py-2.5 mb-4">
        <AlertCircle class="w-4 h-4" /> {{ erro }}
      </div>
      <div v-if="sucesso" class="flex items-center gap-2 text-green-700 text-xs bg-green-50 border border-green-200 rounded-lg px-4 py-2.5 mb-4">
        <CheckCircle class="w-4 h-4" /> Formulário salvo com sucesso!
      </div>

      <!-- Salvar -->
      <button @click="salvar" :disabled="salvando"
        class="w-full flex items-center justify-center gap-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-60 text-white font-bold py-3.5 rounded-xl border-none cursor-pointer text-sm transition-colors">
        <Loader2 v-if="salvando" class="w-4 h-4 animate-spin" />
        <Save v-else class="w-4 h-4" />
        {{ salvando ? 'Salvando...' : 'Salvar Formulário' }}
      </button>

    </div>

    <div v-else class="flex items-center justify-center gap-2 text-gray-400 py-24">
      <Loader2 class="w-5 h-5 animate-spin" /> Carregando...
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import {
  ArrowLeft, FileText, UserPlus, Plus, X,
  Save, Loader2, AlertCircle, CheckCircle
} from 'lucide-vue-next'

const route      = useRoute()
const router     = useRouter()
const produtorId = route.params.produtorId
const fomentoId  = route.params.fomentoId

const produtor                 = ref(null)
const fomento                  = ref(null)
const hierarquia               = ref([])
const salvando                 = ref(false)
const gerandoPDF               = ref(false)
const erro                     = ref('')
const sucesso                  = ref(false)
const caracteristicaCarregada  = ref(false)
const carregandoCaracteristica = ref(false)

// Flag interna para bloquear o watcher de subclasse_id durante reset da classe
let _resetandoClasse = false

// ── Form ───────────────────────────────────────────────
const form = ref({
  numero_processo:            '',
  classe_id:                  null,
  subclasse_id:               null,
  modalidade:                 '',
  justificativa:              '',
  entidade_elaboracao:        '',
  texto_entidade_responsavel: '',
  municipio_data:             'CANAÃ DOS CARAJÁS',
  data_assinatura:            '',
  itens_investimento:         [],
  itens_mao_obra:             [],
  segundo_beneficiario_nome:  '',
  segundo_beneficiario_cpf:   '',
})

// ── Computed ───────────────────────────────────────────
const subclassesDaClasse = computed(() => {
  if (!form.value.classe_id) return []
  return hierarquia.value.find(h => h.classe.id === form.value.classe_id)?.subclasses || []
})

const eFomentoJovem = computed(() => {
  const nome = hierarquia.value
    .find(h => h.classe.id === form.value.classe_id)?.classe.nome ?? ''
  return nome.toLowerCase().includes('jovem') ||
    (form.value.modalidade?.toLowerCase().includes('jovem') ?? false)
})

const totalFinal = computed(() => {
  const inv = form.value.itens_investimento.reduce((s, i) => s + (i.subtotal || 0), 0)
  const mao = form.value.itens_mao_obra.reduce((s, i) => s + (i.subtotal || 0), 0)
  return inv + mao
})

// ── Helpers internos ───────────────────────────────────
function limparCamposCaracteristica() {
  form.value.justificativa              = ''
  form.value.entidade_elaboracao        = ''
  form.value.texto_entidade_responsavel = ''
  form.value.itens_investimento         = []
  form.value.itens_mao_obra             = []
  caracteristicaCarregada.value         = false
}

// ── Watcher: troca de CLASSE ───────────────────────────
// Usa flag para evitar que o watcher de subclasse_id dispare durante o reset
watch(() => form.value.classe_id, (novaClasse) => {
  _resetandoClasse = true
  form.value.subclasse_id = null
  limparCamposCaracteristica()

  if (novaClasse) {
    const classe = hierarquia.value.find(h => h.classe.id === novaClasse)?.classe
    form.value.modalidade = classe?.nome?.toUpperCase() || ''
  } else {
    form.value.modalidade = ''
  }

  // Libera o flag no próximo tick, após o Vue processar o reset do subclasse_id
  setTimeout(() => { _resetandoClasse = false }, 0)
})

// ── Watcher: troca de SUBCLASSE → busca característica ─
watch(() => form.value.subclasse_id, async (subclasseId) => {
  // Ignora se estiver resetando por troca de classe
  if (_resetandoClasse) return

  limparCamposCaracteristica()
  erro.value = ''

  if (!subclasseId || !form.value.classe_id) return

  carregandoCaracteristica.value = true

  try {
    // ✅ Endpoint correto: busca características pré-definidas pelo admin
    const { data } = await api.get(
      `/fomentos/caracteristicas/${form.value.classe_id}/${subclasseId}`
    )

    form.value.justificativa              = data.justificativa              || ''
    form.value.entidade_elaboracao        = data.entidade_elaboracao        || ''
    form.value.texto_entidade_responsavel = data.texto_entidade_responsavel || ''

    // memoria_calculo → itens_investimento
    form.value.itens_investimento = (data.memoria_calculo || []).map(i => ({
      discriminacao:  (i.discriminacao  || '').toUpperCase(),
      quantidade:     Number(i.quantidade     ?? 0),
      valor_unitario: Number(i.valor_unitario ?? 0),
      subtotal:       Number(i.subtotal       ?? (Number(i.quantidade ?? 0) * Number(i.valor_unitario ?? 0))),
    }))

    // mao_obra_especializada → itens_mao_obra
    // Backend pode salvar visitas ou qtd — normaliza para qtd
    form.value.itens_mao_obra = (data.mao_obra_especializada || []).map(i => ({
      descricao:      (i.descricao      || '').toUpperCase(),
      qtd:            Number(i.visitas ?? i.qtd ?? 0),
      valor_unitario: Number(i.valor_unitario ?? 0),
      subtotal:       Number(i.subtotal ?? (Number(i.visitas ?? i.qtd ?? 0) * Number(i.valor_unitario ?? 0))),
    }))

    caracteristicaCarregada.value = true

  } catch (e) {
    // 404 = combinação sem característica pré-definida (esperado)
    if (e?.response?.status !== 404) {
      erro.value = e?.response?.data?.detail || 'Erro ao carregar características pré-definidas.'
    }
    caracteristicaCarregada.value = false
  } finally {
    carregandoCaracteristica.value = false
  }
})

// ── Helpers ────────────────────────────────────────────
const u = (v) => (v || '—').toString().toUpperCase()

function formatarCPF(valor) {
  const nums = valor.replace(/\D/g, '').slice(0, 11)
  return nums
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d{1,2})$/, '$1-$2')
}

function calcularSubtotal(item) {
  item.subtotal = (item.quantidade || 0) * (item.valor_unitario || 0)
}

function calcularSubtotalMao(item) {
  item.subtotal = (item.qtd || 0) * (item.valor_unitario || 0)
}

function adicionarItem(tipo) {
  if (tipo === 'investimento') {
    form.value.itens_investimento.push({ discriminacao: '', quantidade: 0, valor_unitario: 0, subtotal: 0 })
  } else {
    form.value.itens_mao_obra.push({ descricao: '', qtd: 0, valor_unitario: 0, subtotal: 0 })
  }
}

function formatarData(data) {
  if (!data) return '___/___/______'
  const [ano, mes, dia] = data.split('-')
  const meses = [
    'JANEIRO','FEVEREIRO','MARÇO','ABRIL','MAIO','JUNHO',
    'JULHO','AGOSTO','SETEMBRO','OUTUBRO','NOVEMBRO','DEZEMBRO'
  ]
  return `${dia} DE ${meses[parseInt(mes) - 1]} DE ${ano}`
}

// ── PDF ────────────────────────────────────────────────
function gerarLinhasInvestimento() {
  if (!form.value.itens_investimento.length)
    return `<tr><td colspan="4" style="padding:7px 10px;border:1px solid #ccc;text-align:center;color:#999">Nenhum item</td></tr>`
  return form.value.itens_investimento.map(item => `
    <tr>
      <td style="padding:7px 10px;border:1px solid #ccc;text-transform:uppercase">${u(item.discriminacao)}</td>
      <td style="padding:7px 10px;border:1px solid #ccc;text-align:center">${item.quantidade}</td>
      <td style="padding:7px 10px;border:1px solid #ccc;text-align:center">R$ ${Number(item.valor_unitario).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
      <td style="padding:7px 10px;border:1px solid #ccc;text-align:center;font-weight:bold">R$ ${Number(item.subtotal).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
    </tr>`).join('')
}

function gerarLinhasMaoObra() {
  if (!form.value.itens_mao_obra.length)
    return `<tr><td colspan="4" style="padding:7px 10px;border:1px solid #ccc;text-align:center;color:#999">Nenhum item</td></tr>`
  return form.value.itens_mao_obra.map(item => `
    <tr>
      <td style="padding:7px 10px;border:1px solid #ccc;text-transform:uppercase">${u(item.descricao)}</td>
      <td style="padding:7px 10px;border:1px solid #ccc;text-align:center">${item.qtd}</td>
      <td style="padding:7px 10px;border:1px solid #ccc;text-align:center">R$ ${Number(item.valor_unitario).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
      <td style="padding:7px 10px;border:1px solid #ccc;text-align:center;font-weight:bold">R$ ${Number(item.subtotal).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
    </tr>`).join('')
}

function gerarDadosSegundoBeneficiarioPDF() {
  if (!eFomentoJovem.value || !form.value.segundo_beneficiario_nome) return ''
  return `
    <tr>
      <td style="padding:7px 10px;border:1px solid #ccc"><strong>BENEFICIÁRIO:</strong> ${u(form.value.segundo_beneficiario_nome)}</td>
      <td style="padding:7px 10px;border:1px solid #ccc"><strong>CPF:</strong> ${form.value.segundo_beneficiario_cpf || '—'}</td>
    </tr>`
}

function gerarEntidadeResponsavelPDF() {
  const textoExtra = form.value.texto_entidade_responsavel
    ? `<p style="font-size:11px;line-height:1.7;white-space:pre-wrap;margin-top:6px;text-transform:uppercase">${u(form.value.texto_entidade_responsavel)}</p>`
    : ''
  return `
    <div style="margin-bottom:20px">
      <h2 style="color:#1a6b3c;font-size:13px;margin-bottom:6px;text-transform:uppercase">Entidade responsável pela elaboração/execução/acompanhamento deste projeto</h2>
      <p style="font-size:13px;font-weight:bold;text-transform:uppercase;margin:0 0 4px 0">${u(form.value.entidade_elaboracao)}</p>
      ${textoExtra}
    </div>`
}

function gerarJustificativa() {
  if (!form.value.justificativa) return ''
  return `
    <div style="margin-bottom:20px">
      <h2 style="color:#1a6b3c;font-size:13px;margin-bottom:8px;text-transform:uppercase">Justificativa do Projeto Produtivo</h2>
      <p style="font-size:11px;line-height:1.7;white-space:pre-wrap;padding:10px;border:1px solid #ccc;border-radius:4px;text-transform:uppercase">${u(form.value.justificativa)}</p>
    </div>`
}

function gerarAssinaturasNormal() {
  const conjuge = produtor.value?.conjuge_nome
    ? `<div style="text-align:center;width:40%">
        <div style="border-top:1px solid #333;padding-top:8px;font-size:11px">
          <strong>${u(produtor.value.conjuge_nome)}</strong><br/>
          <span style="color:#555">CÔNJUGE — CPF: ${produtor.value.cpf_conjuge || '—'}</span>
        </div>
      </div>`
    : ''
  return `
    <div style="display:flex;justify-content:center;gap:60px;margin-bottom:40px">
      <div style="text-align:center;width:40%">
        <div style="border-top:1px solid #333;padding-top:8px;font-size:11px">
          <strong>${u(produtor.value.nome_completo)}</strong><br/>
          <span style="color:#555">BENEFICIÁRIO — CPF: ${produtor.value.cpf_beneficiario}</span>
        </div>
      </div>
      ${conjuge}
    </div>`
}

function gerarAssinaturasJovem() {
  if (!form.value.segundo_beneficiario_nome) return gerarAssinaturasNormal()
  return `
    <div style="display:flex;justify-content:center;gap:40px;margin-bottom:40px;flex-wrap:wrap">
      <div style="text-align:center;width:28%">
        <div style="border-top:1px solid #333;padding-top:8px;font-size:11px">
          <strong>${u(produtor.value.nome_completo)}</strong><br/>
          <span style="color:#555">BENEFICIÁRIO — CPF: ${produtor.value.cpf_beneficiario}</span>
        </div>
      </div>
      <div style="text-align:center;width:28%">
        <div style="border-top:1px solid #333;padding-top:8px;font-size:11px">
          <strong>${u(produtor.value.conjuge_nome || '—')}</strong><br/>
          <span style="color:#555">CÔNJUGE — CPF: ${produtor.value.cpf_conjuge || '—'}</span>
        </div>
      </div>
      <div style="text-align:center;width:28%">
        <div style="border-top:1px solid #333;padding-top:8px;font-size:11px">
          <strong>${u(form.value.segundo_beneficiario_nome)}</strong><br/>
          <span style="color:#555">BENEFICIÁRIO — CPF: ${form.value.segundo_beneficiario_cpf || '—'}</span>
        </div>
      </div>
    </div>`
}

async function emitirPDF() {
  if (gerandoPDF.value) return
  gerandoPDF.value = true
  try {
    const nomeModalidade = form.value.modalidade ||
      hierarquia.value.find(h => h.classe.id === form.value.classe_id)?.classe.nome || ''
    const assinaturas = eFomentoJovem.value ? gerarAssinaturasJovem() : gerarAssinaturasNormal()

    const html = `
      <div style="font-family:Arial,sans-serif;padding:40px;background:white;color:#000;width:794px;box-sizing:border-box">
        <div style="text-align:center;border-bottom:2px solid #1a6b3c;padding-bottom:16px;margin-bottom:24px">
          <p style="color:#999;margin:0 0 4px 0;font-size:11px;text-transform:uppercase;letter-spacing:1px">
            ${u(produtor.value.codigo_beneficiario || produtorId)}
          </p>
          <h1 style="color:#1a6b3c;margin:0;font-size:18px;text-transform:uppercase">${u(fomento.value.nome)}</h1>
          <p style="color:#666;margin:4px 0 0 0;font-size:11px">MODALIDADE: ${u(nomeModalidade)}</p>
        </div>

        <h2 style="color:#1a6b3c;font-size:13px;margin-bottom:8px;text-transform:uppercase">Dados do Beneficiário</h2>
        <table style="width:100%;border-collapse:collapse;margin-bottom:20px;font-size:11px">
          <tr>
            <td style="padding:7px 10px;border:1px solid #ccc;width:50%"><strong>BENEFICIÁRIO:</strong> ${u(produtor.value.nome_completo)}</td>
            <td style="padding:7px 10px;border:1px solid #ccc"><strong>CPF:</strong> ${produtor.value.cpf_beneficiario}</td>
          </tr>
          <tr>
            <td style="padding:7px 10px;border:1px solid #ccc"><strong>CÔNJUGE:</strong> ${u(produtor.value.conjuge_nome)}</td>
            <td style="padding:7px 10px;border:1px solid #ccc"><strong>CPF:</strong> ${produtor.value.cpf_conjuge || '—'}</td>
          </tr>
          <tr>
            <td style="padding:7px 10px;border:1px solid #ccc"><strong>ASSENTAMENTO:</strong> ${u(produtor.value.assentamento)}</td>
            <td style="padding:7px 10px;border:1px solid #ccc"><strong>LOTE:</strong> ${u(produtor.value.lote)}</td>
          </tr>
          ${gerarDadosSegundoBeneficiarioPDF()}
        </table>

        ${gerarEntidadeResponsavelPDF()}
        ${gerarJustificativa()}

        <h2 style="color:#1a6b3c;font-size:13px;margin-bottom:8px;text-transform:uppercase">Memória de Cálculo — Investimentos</h2>
        <table style="width:100%;border-collapse:collapse;margin-bottom:20px;font-size:11px">
          <thead><tr style="background:#f0f0f0">
            <th style="padding:7px 10px;border:1px solid #ccc;text-align:left">DISCRIMINAÇÃO</th>
            <th style="padding:7px 10px;border:1px solid #ccc;text-align:center;width:60px">QTD</th>
            <th style="padding:7px 10px;border:1px solid #ccc;text-align:center;width:110px">VLR UNITÁRIO</th>
            <th style="padding:7px 10px;border:1px solid #ccc;text-align:center;width:110px">SUBTOTAL</th>
          </tr></thead>
          <tbody>${gerarLinhasInvestimento()}</tbody>
        </table>

        <h2 style="color:#1a6b3c;font-size:13px;margin-bottom:8px;text-transform:uppercase">Mão de Obra Especializada</h2>
        <table style="width:100%;border-collapse:collapse;margin-bottom:20px;font-size:11px">
          <thead><tr style="background:#f0f0f0">
            <th style="padding:7px 10px;border:1px solid #ccc;text-align:left">DESCRIÇÃO</th>
            <th style="padding:7px 10px;border:1px solid #ccc;text-align:center;width:60px">QTD</th>
            <th style="padding:7px 10px;border:1px solid #ccc;text-align:center;width:110px">VLR UNITÁRIO</th>
            <th style="padding:7px 10px;border:1px solid #ccc;text-align:center;width:110px">SUBTOTAL</th>
          </tr></thead>
          <tbody>${gerarLinhasMaoObra()}</tbody>
        </table>

        <div style="background:#e8f5e9;padding:14px 18px;border-radius:6px;text-align:right;margin-bottom:40px;border:2px solid #1a6b3c">
          <strong style="color:#1a6b3c;font-size:14px">TOTAL FINAL: R$ ${totalFinal.value.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</strong>
        </div>

        <p style="font-size:13px;text-align:left;margin-bottom:60px;text-transform:uppercase">
          ${u(form.value.municipio_data)}, ${formatarData(form.value.data_assinatura)}
        </p>

        ${assinaturas}

        <div style="display:flex;justify-content:center">
          <div style="text-align:center;width:55%">
            <div style="border-top:1px solid #333;padding-top:8px;font-size:11px">
              <strong>RESPONSÁVEL TÉCNICO</strong><br/>
              <span style="color:#555;text-transform:uppercase">${u(form.value.entidade_elaboracao)}</span>
            </div>
          </div>
        </div>
      </div>`

    const container = document.createElement('div')
    container.style.cssText = 'position:fixed;top:0;left:-9999px;width:794px;background:white;z-index:-1'
    container.innerHTML = html
    document.body.appendChild(container)
    await new Promise(r => setTimeout(r, 300))

    const canvas = await html2canvas(container, {
      scale: 2, useCORS: true, allowTaint: true,
      backgroundColor: '#ffffff', logging: false,
      width: container.scrollWidth, height: container.scrollHeight,
    })
    document.body.removeChild(container)

    const imgData    = canvas.toDataURL('image/png')
    const pdf        = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
    const pageWidth  = pdf.internal.pageSize.getWidth()
    const pageHeight = pdf.internal.pageSize.getHeight()
    const imgHeight  = pageWidth * (canvas.height / canvas.width)

    let position   = 0
    let heightLeft = imgHeight
    pdf.addImage(imgData, 'PNG', 0, position, pageWidth, imgHeight)
    heightLeft -= pageHeight

    while (heightLeft > 0) {
      position -= pageHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, pageWidth, imgHeight)
      heightLeft -= pageHeight
    }

    const nomeArquivo = `formulario_${u(produtor.value.nome_completo).replace(/\s+/g, '_')}_${new Date().toISOString().slice(0, 10)}.pdf`
    pdf.save(nomeArquivo)
  } catch (e) {
    console.error('Erro ao gerar PDF:', e)
    alert(`Erro ao gerar PDF: ${e.message}`)
  } finally {
    gerandoPDF.value = false
  }
}

// ── Salvar ─────────────────────────────────────────────
async function salvar() {
  erro.value = ''
  if (!form.value.classe_id || !form.value.subclasse_id) {
    erro.value = 'Selecione a modalidade e a submodalidade do crédito.'
    return
  }
  if (eFomentoJovem.value && (!form.value.segundo_beneficiario_nome || !form.value.segundo_beneficiario_cpf)) {
    erro.value = 'Preencha o nome e CPF do segundo beneficiário.'
    return
  }

  salvando.value = true
  try {
    await api.post('/submissoes/', {
      fomento_id:   parseInt(fomentoId),
      produtor_id:  parseInt(produtorId),
      classe_id:    form.value.classe_id,
      subclasse_id: form.value.subclasse_id,
      ...form.value,
    })
    sucesso.value = true
    setTimeout(() => router.push('/produtores'), 2000)
  } catch (e) {
    erro.value = e?.response?.data?.detail || 'Erro ao salvar formulário.'
  } finally {
    salvando.value = false
  }
}

// ── onMounted ──────────────────────────────────────────
onMounted(async () => {
  try {
    const [dadosFormulario, hierarquiaResp] = await Promise.all([
      api.get(`/formulario/${produtorId}/${fomentoId}`),
      api.get(`/fomentos/${fomentoId}/hierarquia`),
    ])

    produtor.value   = dadosFormulario.data.produtor
    fomento.value    = dadosFormulario.data.fomento
    hierarquia.value = hierarquiaResp.data.hierarquia

    // Restaura campos de contexto salvos anteriormente (não pré-carrega seletor)
    if (dadosFormulario.data.numero_processo)
      form.value.numero_processo = dadosFormulario.data.numero_processo
    if (dadosFormulario.data.municipio_data)
      form.value.municipio_data = dadosFormulario.data.municipio_data
    if (dadosFormulario.data.data_assinatura)
      form.value.data_assinatura = dadosFormulario.data.data_assinatura

  } catch (e) {
    console.error('Erro ao carregar formulário:', e)
    erro.value = 'Erro ao carregar dados do formulário.'
  }
})
</script>