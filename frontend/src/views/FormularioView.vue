<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import { ArrowLeft, FileText, UserPlus, Plus, X, Loader2, AlertCircle, CheckCircle } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const produtorId = route.params.produtorId
const fomentoId = route.params.fomentoId

const produtor = ref(null)
const fomento = ref(null)
const hierarquia = ref([])
const gerandoPDF = ref(false)
const erro = ref('')
const caracteristicaCarregada = ref(false)
const carregandoCaracteristica = ref(false)
let resetandoClasse = false

const form = ref({
  numero_processo: '',
  classe_id: null,
  subclasse_id: null,
  modalidade: '',
  justificativa: '',
  entidade_elaboracao: '',
  texto_entidade_responsavel: '',
  municipio_data: 'CANAÃ DOS CARAJÁS',
  data_assinatura: '',
  itens_investimento: [],
  itens_mao_obra: [],
  segundo_beneficiario_nome: '',
  segundo_beneficiario_cpf: '',
})

const subclassesDaClasse = computed(() => {
  if (!form.value.classe_id) return []
  const encontrado = hierarquia.value.find(h => h.classe.id === form.value.classe_id)
  console.log('[DEBUG] subclassesDaClasse:', {
    classe_id: form.value.classe_id,
    encontrou: !!encontrado,
    subclasses: encontrado?.subclasses
  })
  return encontrado?.subclasses || []
})

const eFomentoJovem = computed(() => {
  const nome = hierarquia.value.find(h => h.classe.id === form.value.classe_id)?.classe.nome ?? ''
  return nome.toLowerCase().includes('jovem') || (form.value.modalidade?.toLowerCase().includes('jovem') ?? false)
})

const totalFinal = computed(() => {
  const inv = form.value.itens_investimento.reduce((s, i) => s + (i.subtotal || 0), 0)
  const mao = form.value.itens_mao_obra.reduce((s, i) => s + (i.subtotal || 0), 0)
  return inv + mao
})

function limparCamposCaracteristica() {
  console.log('[DEBUG] Limpando campos de característica')
  form.value.justificativa = ''
  form.value.entidade_elaboracao = ''
  form.value.texto_entidade_responsavel = ''
  form.value.itens_investimento = []
  form.value.itens_mao_obra = []
  caracteristicaCarregada.value = false
}

watch(form.value.classe_id, (novaClasse, antigaClasse) => {
  console.log('[DEBUG] watch classe_id:', { antigaClasse, novaClasse })
  resetandoClasse = true
  form.value.subclasse_id = null
  limparCamposCaracteristica()
  if (novaClasse) {
    const classe = hierarquia.value.find(h => h.classe.id === novaClasse)?.classe
    form.value.modalidade = classe?.nome?.toUpperCase() || ''
    console.log('[DEBUG] Modalidade definida:', form.value.modalidade)
  } else {
    form.value.modalidade = ''
  }
  setTimeout(() => { resetandoClasse = false }, 0)
})

watch(form.value.subclasse_id, async (subclasseId, antigaSubclasse) => {
  console.log('[DEBUG] watch subclasse_id:', { 
    antigaSubclasse, 
    novaSubclasse: subclasseId,
    resetandoClasse,
    classe_id: form.value.classe_id
  })
  
  if (resetandoClasse) {
    console.log('[DEBUG] Ignorando - está resetando')
    return
  }
  
  limparCamposCaracteristica()
  erro.value = ''
  
  if (!subclasseId) {
    console.log('[DEBUG] subclasse_id é nulo/undefined')
    return
  }
  
  if (!form.value.classe_id) {
    console.log('[DEBUG] classe_id é nulo/undefined')
    return
  }

  console.log('[DEBUG] ✅ Iniciando busca de características...')
  console.log('[DEBUG] URL:', `/fomentos/caracteristicas/${form.value.classe_id}/${subclasseId}`)
  
  carregandoCaracteristica.value = true
  
  try {
    const response = await api.get(`/fomentos/caracteristicas/${form.value.classe_id}/${subclasseId}`)
    console.log('[DEBUG] ✅ Resposta da API:', response.data)
    
    form.value.justificativa = response.data.justificativa || ''
    form.value.entidade_elaboracao = response.data.entidade_elaboracao || ''
    form.value.texto_entidade_responsavel = response.data.texto_entidade_responsavel || ''
    form.value.itens_investimento = (response.data.memoria_calculo || []).map(i => ({
      discriminacao: i.discriminacao || '',
      quantidade: Number(i.quantidade ?? 0),
      valor_unitario: Number(i.valor_unitario ?? 0),
      subtotal: Number(i.subtotal ?? ((i.quantidade ?? 0) * (i.valor_unitario ?? 0))),
    }))
    form.value.itens_mao_obra = (response.data.mao_obra_especializada || []).map(i => ({
      descricao: i.descricao || '',
      visitas: Number(i.visitas ?? i.qtd ?? 0),
      valor_unitario: Number(i.valor_unitario ?? 0),
      subtotal: Number(i.subtotal ?? ((i.visitas ?? i.qtd ?? 0) * (i.valor_unitario ?? 0))),
    }))
    caracteristicaCarregada.value = true
    console.log('[DEBUG] ✅ Características carregadas com sucesso!')
  } catch (e) {
    console.error('[DEBUG] ❌ Erro na requisição:', e)
    console.error('[DEBUG] Status:', e?.response?.status)
    console.error('[DEBUG] Dados:', e?.response?.data)
    
    if (e?.response?.status !== 404) {
      erro.value = e?.response?.data?.detail || 'Erro ao carregar características.'
    }
    caracteristicaCarregada.value = false
  } finally {
    carregandoCaracteristica.value = false
  }
})

function calcularSubtotal(item) {
  item.subtotal = (item.quantidade || 0) * (item.valor_unitario || 0)
}

function calcularSubtotalMao(item) {
  item.subtotal = (item.visitas || 0) * (item.valor_unitario || 0)
}

function adicionarItem(tipo) {
  if (tipo === 'investimento') {
    form.value.itens_investimento.push({ discriminacao: '', quantidade: 0, valor_unitario: 0, subtotal: 0 })
  } else {
    form.value.itens_mao_obra.push({ descricao: '', visitas: 0, valor_unitario: 0, subtotal: 0 })
  }
}

async function emitirPDF() {
  if (gerandoPDF.value) return
  gerandoPDF.value = true
  try {
    const nomeModalidade = form.value.modalidade || hierarquia.value.find(h => h.classe.id === form.value.classe_id)?.classe.nome || ''
    const nomeBeneficiario = (produtor.value?.nome_completo || '').toUpperCase()
    const html = `<div style="font-family:Arial,sans-serif;padding:40px;background:#fff;color:#000;width:794px;box-sizing:border-box;"><div style="text-align:center;border-bottom:2px solid #1a6b3c;padding-bottom:16px;margin-bottom:24px;"><p style="color:#999;margin:0 0 4px 0;font-size:11px;text-transform:uppercase;">${produtor.value?.codigo_beneficiario}</p><h1 style="color:#1a6b3c;margin:0;font-size:18px;text-transform:uppercase;">${fomento.value?.nome}</h1><p style="color:#666;margin:4px 0 0 0;font-size:11px;">MODALIDADE: ${nomeModalidade}</p></div><h2 style="color:#1a6b3c;font-size:13px;margin-bottom:8px;text-transform:uppercase;">Dados do Beneficiário</h2><table style="width:100%;border-collapse:collapse;margin-bottom:20px;font-size:11px;"><tr><td style="padding:7px 10px;border:1px solid #ccc;width:50%;"><strong>BENEFICIÁRIO</strong> ${nomeBeneficiario}</td><td style="padding:7px 10px;border:1px solid #ccc;"><strong>CPF</strong> ${produtor.value?.cpf_beneficiario}</td></tr></table><h2 style="color:#1a6b3c;font-size:13px;margin-bottom:8px;text-transform:uppercase;">Memória de Cálculo - Investimentos</h2><table style="width:100%;border-collapse:collapse;margin-bottom:20px;font-size:11px;"><thead><tr style="background:#f0f0f0;"><th style="padding:7px 10px;border:1px solid #ccc;text-align:left;">DISCRIMINAÇÃO</th><th style="padding:7px 10px;border:1px solid #ccc;text-align:center;width:60px;">QTD</th><th style="padding:7px 10px;border:1px solid #ccc;text-align:center;width:110px;">VLR UNITÁRIO</th><th style="padding:7px 10px;border:1px solid #ccc;text-align:center;width:110px;">SUBTOTAL</th></tr></thead><tbody>${form.value.itens_investimento.map(item => `<tr><td style="padding:7px 10px;border:1px solid #ccc;text-transform:uppercase;">${item.discriminacao}</td><td style="padding:7px 10px;border:1px solid #ccc;text-align:center;">${item.quantidade}</td><td style="padding:7px 10px;border:1px solid #ccc;text-align:center;">R$ ${Number(item.valor_unitario).toLocaleString('pt-BR',{minimumFractionDigits:2})}</td><td style="padding:7px 10px;border:1px solid #ccc;text-align:center;font-weight:bold;">R$ ${Number(item.subtotal).toLocaleString('pt-BR',{minimumFractionDigits:2})}</td></tr>`).join('')}</tbody></table><div style="background:#e8f5e9;padding:14px 18px;border-radius:6px;text-align:right;margin-bottom:40px;border:2px solid #1a6b3c;"><strong style="color:#1a6b3c;font-size:14px;">TOTAL FINAL: R$ ${totalFinal.value.toLocaleString('pt-BR',{minimumFractionDigits:2})}</strong></div></div>`
    const container = document.createElement('div')
    container.style.cssText = 'position:fixed;top:0;left:-9999px;width:794px;background:#fff;z-index:-1;'
    container.innerHTML = html
    document.body.appendChild(container)
    await new Promise(r => setTimeout(r, 300))
    
    const canvas = await html2canvas(container, { scale: 2, useCORS: true, allowTaint: true, backgroundColor: '#ffffff', logging: false, width: container.scrollWidth, height: container.scrollHeight })
    document.body.removeChild(container)
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
    const pageWidth = pdf.internal.pageSize.getWidth()
    const imgHeight = (pageWidth * canvas.height) / canvas.width
    pdf.addImage(imgData, 'PNG', 0, 0, pageWidth, imgHeight)
    const nomeArquivo = `formulario_${(produtor.value?.nome_completo || 'produtor').replace(/\s+/g, '_')}_${new Date().toISOString().slice(0, 10)}.pdf`
    pdf.save(nomeArquivo)
  } catch (e) {
    console.error('Erro ao gerar PDF:', e)
    alert('Erro ao gerar PDF: ' + e.message)
  } finally {
    gerandoPDF.value = false
  }
}

onMounted(async () => {
  console.log('[DEBUG] onMounted - iniciando carregamento')
  try {
    const [dadosFormulario, hierarquiaResp] = await Promise.all([
      api.get(`/formulario/${produtorId}/${fomentoId}`),
      api.get(`/fomentos/${fomentoId}/hierarquia`),
    ])
    console.log('[DEBUG] hierarquiaResp.data:', hierarquiaResp.data)
    console.log('[DEBUG] hierarquiaResp.data.hierarquia:', hierarquiaResp.data.hierarquia)
    
    produtor.value = dadosFormulario.data.produtor
    fomento.value = dadosFormulario.data.fomento
    hierarquia.value = hierarquiaResp.data.hierarquia
    
    console.log('[DEBUG] hierarquia.value após atribuição:', hierarquia.value)
    
    if (dadosFormulario.data.numero_processo) form.value.numero_processo = dadosFormulario.data.numero_processo
    if (dadosFormulario.data.municipio_data) form.value.municipio_data = dadosFormulario.data.municipio_data
    if (dadosFormulario.data.data_assinatura) form.value.data_assinatura = dadosFormulario.data.data_assinatura
  } catch (e) {
    console.error('[DEBUG] Erro ao carregar formulário:', e)
    erro.value = 'Erro ao carregar dados.'
  }
})
</script>
