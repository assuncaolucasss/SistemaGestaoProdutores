<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <FileText class="w-5 h-5 text-primary-600" />
        <h3 class="text-base font-bold text-primary-600">Rascunhos Salvos</h3>
      </div>
      <button v-if="selecionados.length > 0" @click.stop="baixarZip" :disabled="gerandoZip"
        class="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-60 text-white text-xs font-semibold px-4 py-2 rounded-lg border-none cursor-pointer transition-colors">
        <Loader2 v-if="gerandoZip" class="w-3.5 h-3.5 animate-spin" />
        <Download v-else class="w-3.5 h-3.5" />
        {{ gerandoZip ? 'Gerando ZIP...' : `Baixar ZIP (${selecionados.length})` }}
      </button>
    </div>

    <div v-if="carregando" class="flex items-center gap-2 text-gray-400 text-sm py-6">
      <Loader2 class="w-4 h-4 animate-spin" /> Carregando rascunhos...
    </div>

    <div v-else-if="!submissoes.length"
      class="flex flex-col items-center justify-center text-gray-400 py-10 gap-2 border border-dashed border-gray-200 rounded-xl">
      <FileText class="w-8 h-8 opacity-30" />
      <p class="text-sm">Nenhum formulário salvo ainda.</p>
    </div>

    <div v-else class="flex flex-col gap-3">
      <div class="flex items-center gap-2 text-xs text-gray-500 px-1">
        <input type="checkbox" :checked="todosSelec" @change.stop="toggleTodos"
          class="w-3.5 h-3.5 accent-primary-600 cursor-pointer" />
        <span>Selecionar todos</span>
      </div>

      <div v-for="s in submissoes" :key="s.id"
        class="bg-white border rounded-xl px-5 py-4 transition-all"
        :class="selecionados.includes(s.id) ? 'border-primary-600 bg-primary-50/40' : 'border-gray-200'">
        <div class="flex items-start gap-3">
          <input type="checkbox" :value="s.id" v-model="selecionados"
            @click.stop
            class="mt-1 w-4 h-4 accent-primary-600 cursor-pointer shrink-0" />
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="font-semibold text-gray-700 text-sm">{{ s.modalidade || 'Sem modalidade' }}</span>
              <span class="bg-primary-50 text-primary-600 text-xs px-2 py-0.5 rounded-full">
                {{ fomentoNome(s.fomento_id) }}
              </span>
            </div>
            <p class="text-gray-400 text-xs mt-1">
              Processo: {{ s.numero_processo || '—' }} ·
              Salvo em: {{ formatarData(s.criado_em) }}
            </p>
            <p v-if="s.atualizado_em && s.atualizado_em !== s.criado_em"
              class="text-amber-500 text-xs mt-0.5">
              Editado em: {{ formatarData(s.atualizado_em) }}
            </p>
          </div>
          <div class="flex items-center gap-2 shrink-0">
            <button @click.stop="abrirEdicao(s)"
              class="flex items-center gap-1 bg-gray-100 hover:bg-gray-200 text-gray-600 text-xs px-3 py-1.5 rounded-lg border-none cursor-pointer transition-colors">
              <Pencil class="w-3 h-3" /> Editar
            </button>
            <button @click.stop="baixarIndividual(s)" :disabled="gerandoIndividual === s.id"
              class="flex items-center gap-1 bg-primary-50 hover:bg-primary-100 border border-primary-600 text-primary-600 text-xs px-3 py-1.5 rounded-lg cursor-pointer transition-colors">
              <Loader2 v-if="gerandoIndividual === s.id" class="w-3 h-3 animate-spin" />
              <Download v-else class="w-3 h-3" />
              PDF
            </button>
            <button @click.stop="confirmarRemocao(s)"
              class="flex items-center gap-1 bg-red-50 hover:bg-red-100 text-red-600 text-xs px-3 py-1.5 rounded-lg border-none cursor-pointer transition-colors">
              <Trash2 class="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal edição -->
    <div v-if="editando" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto p-8">
        <div class="flex items-center gap-2 mb-6">
          <div class="bg-primary-50 p-2 rounded-full">
            <Pencil class="w-5 h-5 text-primary-600" />
          </div>
          <h3 class="text-lg font-bold text-primary-600">Editar Rascunho</h3>
        </div>
        <div class="flex flex-col gap-3">
          <div>
            <label class="text-xs font-medium text-gray-600 mb-1 block">Número do Processo</label>
            <input v-model="formEdicao.numero_processo"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600" />
          </div>
          <div>
            <label class="text-xs font-medium text-gray-600 mb-1 block">Modalidade</label>
            <input v-model="formEdicao.modalidade"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600" />
          </div>
          <div>
            <label class="text-xs font-medium text-gray-600 mb-1 block">Entidade de Elaboração</label>
            <input v-model="formEdicao.entidade_elaboracao"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600" />
          </div>
          <div>
            <label class="text-xs font-medium text-gray-600 mb-1 block">Justificativa</label>
            <textarea v-model="formEdicao.justificativa" rows="4"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600 resize-y" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs font-medium text-gray-600 mb-1 block">Município</label>
              <input v-model="formEdicao.municipio_data"
                class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600" />
            </div>
            <div>
              <label class="text-xs font-medium text-gray-600 mb-1 block">Data</label>
              <input v-model="formEdicao.data_assinatura" type="date"
                class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600" />
            </div>
          </div>
        </div>
        <div class="flex gap-3 mt-6">
          <button @click.stop="editando = null"
            class="flex-1 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 cursor-pointer bg-white transition-colors">
            Cancelar
          </button>
          <button @click.stop="salvarEdicao" :disabled="salvandoEdicao"
            class="flex-1 flex items-center justify-center gap-2 py-2.5 bg-primary-600 hover:bg-primary-700 disabled:opacity-60 text-white text-sm font-semibold rounded-lg border-none cursor-pointer transition-colors">
            <Loader2 v-if="salvandoEdicao" class="w-4 h-4 animate-spin" />
            <Save v-else class="w-4 h-4" />
            {{ salvandoEdicao ? 'Salvando...' : 'Salvar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal confirmar remoção -->
    <div v-if="submissaoParaRemover" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-8 text-center">
        <div class="flex justify-center mb-4">
          <div class="bg-red-50 p-4 rounded-full">
            <Trash2 class="w-7 h-7 text-red-500" />
          </div>
        </div>
        <h3 class="text-lg font-bold text-gray-700 mb-2">Remover rascunho?</h3>
        <p class="text-gray-400 text-sm mb-6">Esta ação não pode ser desfeita.</p>
        <div class="flex gap-3">
          <button @click.stop="submissaoParaRemover = null"
            class="flex-1 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 cursor-pointer bg-white transition-colors">
            Cancelar
          </button>
          <button @click.stop="executarRemocao" :disabled="removendo"
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
import { ref, computed, onMounted, watch } from 'vue'
import { FileText, Download, Pencil, Trash2, Loader2, Save } from 'lucide-vue-next'
import JSZip from 'jszip'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import api from '../services/api'

const props = defineProps({
  produtorId:         { type: [Number, String], required: true },
  produtor:           { type: Object, required: true },
  fomentos:           { type: Array, default: () => [] },
  submissoesIniciais: { type: Array, default: null },
})

const submissoes           = ref([])
const carregando           = ref(false)
const selecionados         = ref([])
const gerandoZip           = ref(false)
const gerandoIndividual    = ref(null)
const editando             = ref(null)
const formEdicao           = ref({})
const salvandoEdicao       = ref(false)
const submissaoParaRemover = ref(null)
const removendo            = ref(false)

const todosSelec = computed(() =>
  submissoes.value.length > 0 && selecionados.value.length === submissoes.value.length
)

function toggleTodos() {
  selecionados.value = todosSelec.value ? [] : submissoes.value.map(s => s.id)
}

async function carregar() {
  carregando.value = true
  try {
    const { data } = await api.get('/submissoes/', { params: { produtor_id: props.produtorId } })
    submissoes.value = data
  } finally {
    carregando.value = false
  }
}

onMounted(() => {
  if (props.submissoesIniciais !== null) {
    submissoes.value = props.submissoesIniciais
  } else {
    carregar()
  }
})

watch(() => props.submissoesIniciais, (val) => {
  if (val !== null) submissoes.value = val
})

function formatarData(dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleDateString('pt-BR')
}

function formatarDataExtenso(data) {
  if (!data) return '___/___/______'
  const [ano, mes, dia] = data.split('-')
  const meses = ['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro']
  return `${dia} de ${meses[parseInt(mes) - 1]} de ${ano}`
}

function fomentoNome(fomentoId) {
  return props.fomentos.find(f => f.id === fomentoId)?.nome || `Fomento #${fomentoId}`
}

function gerarHTML(s) {
  const p = props.produtor
  const inv = (s.itens_investimento || []).map(item => `
    <tr>
      <td style="padding:7px 10px;border:1px solid #ccc">${item.discriminacao}</td>
      <td style="padding:7px 10px;border:1px solid #ccc;text-align:center">${item.quantidade}</td>
      <td style="padding:7px 10px;border:1px solid #ccc;text-align:center">R$ ${Number(item.valor_unitario).toLocaleString('pt-BR',{minimumFractionDigits:2})}</td>
      <td style="padding:7px 10px;border:1px solid #ccc;text-align:center;font-weight:bold">R$ ${Number(item.subtotal).toLocaleString('pt-BR',{minimumFractionDigits:2})}</td>
    </tr>`).join('') || `<tr><td colspan="4" style="padding:7px 10px;border:1px solid #ccc;text-align:center;color:#999">Nenhum item</td></tr>`

  const mao = (s.itens_mao_obra || []).map(item => `
    <tr>
      <td style="padding:7px 10px;border:1px solid #ccc">${item.descricao}</td>
      <td style="padding:7px 10px;border:1px solid #ccc;text-align:center">${item.visitas}</td>
      <td style="padding:7px 10px;border:1px solid #ccc;text-align:center">R$ ${Number(item.valor_unitario).toLocaleString('pt-BR',{minimumFractionDigits:2})}</td>
      <td style="padding:7px 10px;border:1px solid #ccc;text-align:center;font-weight:bold">R$ ${Number(item.subtotal).toLocaleString('pt-BR',{minimumFractionDigits:2})}</td>
    </tr>`).join('') || `<tr><td colspan="4" style="padding:7px 10px;border:1px solid #ccc;text-align:center;color:#999">Nenhum item</td></tr>`

  const totalInv = (s.itens_investimento || []).reduce((a, i) => a + (i.subtotal || 0), 0)
  const totalMao = (s.itens_mao_obra || []).reduce((a, i) => a + (i.subtotal || 0), 0)
  const total = totalInv + totalMao

  return `
    <div style="font-family:Arial,sans-serif;padding:40px;background:white;color:#000;width:794px;box-sizing:border-box">
      <div style="text-align:center;border-bottom:2px solid #1a6b3c;padding-bottom:16px;margin-bottom:24px">
        <h1 style="color:#1a6b3c;margin:0;font-size:18px">${fomentoNome(s.fomento_id)}</h1>
        <p style="color:#666;margin:6px 0;font-size:12px">${s.entidade_elaboracao || ''}</p>
        <p style="color:#666;margin:0;font-size:11px">Processo nº ${s.numero_processo || '—'} | Modalidade: ${s.modalidade || '—'}</p>
      </div>
      <h2 style="color:#1a6b3c;font-size:13px;margin-bottom:8px;text-transform:uppercase">Dados do Beneficiário</h2>
      <table style="width:100%;border-collapse:collapse;margin-bottom:20px;font-size:11px">
        <tr>
          <td style="padding:7px 10px;border:1px solid #ccc"><strong>Beneficiário:</strong> ${p.nome_completo}</td>
          <td style="padding:7px 10px;border:1px solid #ccc"><strong>CPF:</strong> ${p.cpf_beneficiario}</td>
        </tr>
        <tr>
          <td style="padding:7px 10px;border:1px solid #ccc"><strong>Cônjuge:</strong> ${p.conjuge_nome || '—'}</td>
          <td style="padding:7px 10px;border:1px solid #ccc"><strong>CPF Cônjuge:</strong> ${p.cpf_conjuge || '—'}</td>
        </tr>
        <tr>
          <td style="padding:7px 10px;border:1px solid #ccc"><strong>Assentamento:</strong> ${p.assentamento}</td>
          <td style="padding:7px 10px;border:1px solid #ccc"><strong>Lote:</strong> ${p.lote}</td>
        </tr>
      </table>
      ${s.justificativa ? `
        <h2 style="color:#1a6b3c;font-size:13px;margin-bottom:8px;text-transform:uppercase">Justificativa</h2>
        <p style="font-size:11px;line-height:1.7;padding:10px;border:1px solid #ccc;border-radius:4px;margin-bottom:20px;white-space:pre-wrap">${s.justificativa}</p>` : ''}
      <h2 style="color:#1a6b3c;font-size:13px;margin-bottom:8px;text-transform:uppercase">Memória de Cálculo — Investimentos</h2>
      <table style="width:100%;border-collapse:collapse;margin-bottom:20px;font-size:11px">
        <thead><tr style="background:#f0f0f0">
          <th style="padding:7px 10px;border:1px solid #ccc;text-align:left">Discriminação</th>
          <th style="padding:7px 10px;border:1px solid #ccc;text-align:center;width:60px">Qtd</th>
          <th style="padding:7px 10px;border:1px solid #ccc;text-align:center;width:110px">Vlr Unitário</th>
          <th style="padding:7px 10px;border:1px solid #ccc;text-align:center;width:110px">Subtotal</th>
        </tr></thead>
        <tbody>${inv}</tbody>
      </table>
      <h2 style="color:#1a6b3c;font-size:13px;margin-bottom:8px;text-transform:uppercase">Mão de Obra Especializada</h2>
      <table style="width:100%;border-collapse:collapse;margin-bottom:20px;font-size:11px">
        <thead><tr style="background:#f0f0f0">
          <th style="padding:7px 10px;border:1px solid #ccc;text-align:left">Descrição</th>
          <th style="padding:7px 10px;border:1px solid #ccc;text-align:center;width:60px">Visitas</th>
          <th style="padding:7px 10px;border:1px solid #ccc;text-align:center;width:110px">Vlr Unitário</th>
          <th style="padding:7px 10px;border:1px solid #ccc;text-align:center;width:110px">Subtotal</th>
        </tr></thead>
        <tbody>${mao}</tbody>
      </table>
      <div style="background:#e8f5e9;padding:14px 18px;border-radius:6px;text-align:right;margin-bottom:40px;border:2px solid #1a6b3c">
        <strong style="color:#1a6b3c;font-size:14px">TOTAL FINAL: R$ ${total.toLocaleString('pt-BR',{minimumFractionDigits:2})}</strong>
      </div>
      <p style="font-size:13px;margin-bottom:60px">${s.municipio_data || ''}, ${formatarDataExtenso(s.data_assinatura)}</p>
      <div style="display:flex;justify-content:center;gap:60px;margin-bottom:40px">
        <div style="text-align:center;width:40%">
          <div style="border-top:1px solid #333;padding-top:8px;font-size:11px">
            <strong>${p.nome_completo}</strong><br/>
            <span style="color:#555">Beneficiário — CPF: ${p.cpf_beneficiario}</span>
          </div>
        </div>
        ${p.conjuge_nome ? `
        <div style="text-align:center;width:40%">
          <div style="border-top:1px solid #333;padding-top:8px;font-size:11px">
            <strong>${p.conjuge_nome}</strong><br/>
            <span style="color:#555">Cônjuge — CPF: ${p.cpf_conjuge || '—'}</span>
          </div>
        </div>` : ''}
      </div>
      <div style="display:flex;justify-content:center">
        <div style="text-align:center;width:55%">
          <div style="border-top:1px solid #333;padding-top:8px;font-size:11px">
            <strong>Responsável Técnico</strong><br/>
            <span style="color:#555">${s.entidade_elaboracao || ''}</span>
          </div>
        </div>
      </div>
    </div>`
}

async function htmlParaPdfBlob(s) {
  const container = document.createElement('div')
  container.style.cssText = 'position:fixed;top:0;left:-9999px;width:794px;background:white;z-index:-1'
  container.innerHTML = gerarHTML(s)
  document.body.appendChild(container)
  await new Promise(r => setTimeout(r, 300))
  const canvas = await html2canvas(container, {
    scale: 2, useCORS: true, backgroundColor: '#ffffff', logging: false,
    width: container.scrollWidth, height: container.scrollHeight,
  })
  document.body.removeChild(container)
  const imgData = canvas.toDataURL('image/png')
  const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
  const pw = pdf.internal.pageSize.getWidth()
  const ph = pdf.internal.pageSize.getHeight()
  const imgH = pw / (canvas.width / canvas.height)
  let left = imgH
  let pos = 0
  pdf.addImage(imgData, 'PNG', 0, pos, pw, imgH)
  left -= ph
  while (left > 0) {
    pos -= ph
    pdf.addPage()
    pdf.addImage(imgData, 'PNG', 0, pos, pw, imgH)
    left -= ph
  }
  return pdf.output('blob')
}

async function baixarIndividual(s) {
  gerandoIndividual.value = s.id
  try {
    const blob = await htmlParaPdfBlob(s)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `formulario_${props.produtor.nome_completo.replace(/\s+/g,'_')}_${s.modalidade || s.id}.pdf`
    a.click()
    URL.revokeObjectURL(url)
  } finally {
    gerandoIndividual.value = null
  }
}

async function baixarZip() {
  gerandoZip.value = true
  try {
    const zip = new JSZip()
    const alvo = submissoes.value.filter(s => selecionados.value.includes(s.id))
    for (const s of alvo) {
      const blob = await htmlParaPdfBlob(s)
      zip.file(`formulario_${s.modalidade || s.id}_${s.numero_processo || s.id}.pdf`, blob)
    }
    const zipBlob = await zip.generateAsync({ type: 'blob' })
    const url = URL.createObjectURL(zipBlob)
    const a = document.createElement('a')
    a.href = url
    a.download = `formularios_${props.produtor.nome_completo.replace(/\s+/g,'_')}.zip`
    a.click()
    URL.revokeObjectURL(url)
    selecionados.value = []
  } finally {
    gerandoZip.value = false
  }
}

function abrirEdicao(s) {
  editando.value = s
  formEdicao.value = {
    numero_processo:     s.numero_processo,
    modalidade:          s.modalidade,
    entidade_elaboracao: s.entidade_elaboracao,
    justificativa:       s.justificativa,
    municipio_data:      s.municipio_data,
    data_assinatura:     s.data_assinatura,
  }
}

async function salvarEdicao() {
  salvandoEdicao.value = true
  try {
    const { data } = await api.patch(`/submissoes/${editando.value.id}`, formEdicao.value)
    const idx = submissoes.value.findIndex(s => s.id === editando.value.id)
    if (idx !== -1) submissoes.value[idx] = data
    editando.value = null
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao salvar edição.')
  } finally {
    salvandoEdicao.value = false
  }
}

function confirmarRemocao(s) {
  submissaoParaRemover.value = s
}

async function executarRemocao() {
  removendo.value = true
  try {
    await api.delete(`/submissoes/${submissaoParaRemover.value.id}`)
    submissoes.value = submissoes.value.filter(s => s.id !== submissaoParaRemover.value.id)
    selecionados.value = selecionados.value.filter(id => id !== submissaoParaRemover.value.id)
    submissaoParaRemover.value = null
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao remover.')
  } finally {
    removendo.value = false
  }
}
</script>