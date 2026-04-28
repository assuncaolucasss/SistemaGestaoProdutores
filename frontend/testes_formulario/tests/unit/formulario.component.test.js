/**
 * TESTES DE COMPONENTE — FormularioView.vue
 * Adaptado ao template real: sem data-testid, com setTimeout na flag _resetandoClasse
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { nextTick } from 'vue'

import {
  hierarquiaMock,
  produtorMock,
  fomentoMock,
  caracteristicaMock,
} from '../mocks/hierarquia.js'

import api from '@/services/api'
import FormularioView from '@/views/FormularioView.vue'

// Helper: aguarda setTimeout + promessas (necessário por causa do _resetandoClasse)
const flush = async () => {
  await flushPromises()
  await new Promise(r => setTimeout(r, 10))
  await flushPromises()
}

function setupApiMocks({ erro404 = false } = {}) {
  api.get.mockImplementation((url) => {
    if (url.includes('/formulario/')) {
      return Promise.resolve({
        data: {
          produtor:        produtorMock,
          fomento:         fomentoMock,
          municipio_data:  'CANAÃ DOS CARAJÁS',
          data_assinatura: '',
          numero_processo: '',
        },
      })
    }
    if (url.includes('/hierarquia')) {
      return Promise.resolve({ data: { hierarquia: hierarquiaMock } })
    }
    if (url.includes('/fomentos/caracteristicas/')) {
      if (erro404) return Promise.reject({ response: { status: 404 } })
      return Promise.resolve({ data: caracteristicaMock })
    }
    return Promise.reject(new Error(`URL não mockada: ${url}`))
  })
}

const mountFormulario = () =>
  mount(FormularioView, {
    global: { stubs: { teleport: true } },
  })

// ── Montagem ───────────────────────────────────────────────────────────────
describe('FormularioView — montagem', () => {
  beforeEach(() => setupApiMocks())
  afterEach(() => vi.clearAllMocks())

  it('exibe nome do produtor e do fomento', async () => {
    const w = mountFormulario()
    await flush()
    expect(w.text()).toContain('MARIA DA SILVA')
    expect(w.text()).toContain('CRÉDITO INSTALAÇÃO INCRA')
  })

  it('carrega opções de modalidade da hierarquia', async () => {
    const w = mountFormulario()
    await flush()
    expect(w.text()).toContain('FOMENTO MULHER')
    expect(w.text()).toContain('FOMENTO JOVEM')
  })

  it('select de submodalidade começa desabilitado', async () => {
    const w = mountFormulario()
    await flush()
    // O select de submodalidade tem :disabled="!form.classe_id"
    const sub = w.findAll('select').at(1)
    expect(sub.attributes('disabled')).toBeDefined()
  })
})

// ── Watcher: classe_id ─────────────────────────────────────────────────────
describe('FormularioView — watcher classe_id', () => {
  beforeEach(() => setupApiMocks())
  afterEach(() => vi.clearAllMocks())

  it('habilita select de submodalidade ao selecionar classe', async () => {
    const w = mountFormulario()
    await flush()
    await w.findAll('select').at(0).setValue(10)
    await flush()
    expect(w.findAll('select').at(1).attributes('disabled')).toBeUndefined()
  })

  it('popula submodalidades corretas para FOMENTO MULHER', async () => {
    const w = mountFormulario()
    await flush()
    await w.findAll('select').at(0).setValue(10)
    await flush()
    const nomes = w.findAll('select').at(1).findAll('option').map(o => o.text())
    expect(nomes.some(n => n.includes('AÇAÍ'))).toBe(true)
    expect(nomes.some(n => n.includes('CACAU'))).toBe(true)
  })

  it('limpa subclasse_id ao trocar de classe', async () => {
    const w = mountFormulario()
    await flush()
    await w.findAll('select').at(0).setValue(10)
    await flush()
    w.vm.form.subclasse_id = 101
    await flush()
    await w.findAll('select').at(0).setValue(30)
    await flush()
    expect(w.vm.form.subclasse_id).toBeNull()
  })

  it('exibe bloco de segundo beneficiário apenas para FOMENTO JOVEM (id 20)', async () => {
    const w = mountFormulario()
    await flush()

    // Antes de selecionar: eFomentoJovem = false → bloco não renderiza
    expect(w.vm.eFomentoJovem).toBe(false)

    // Seleciona FOMENTO JOVEM
    await w.findAll('select').at(0).setValue(20)
    await flush()

    // eFomentoJovem deve ser true — computed verifica se nome contém 'jovem'
    expect(w.vm.eFomentoJovem).toBe(true)

    // O bloco com "Segundo Beneficiário" deve estar no DOM
    expect(w.text()).toContain('Segundo Beneficiário')
  })

  it('limpa campos de características ao trocar de classe', async () => {
    const w = mountFormulario()
    await flush()

    // Seleciona FOMENTO MULHER → AÇAÍ (carrega características)
    await w.findAll('select').at(0).setValue(10)
    await flush()
    w.vm.form.subclasse_id = 101
    w.vm.$options // força reatividade
    await flush()

    // Simula o que o watcher faria (carrega diretamente no vm para o teste)
    w.vm.form.justificativa = 'TEXTO DE JUSTIFICATIVA PRÉ-DEFINIDA'
    w.vm.caracteristicaCarregada = true
    await nextTick()

    expect(w.vm.form.justificativa).not.toBe('')

    // Troca de classe → watcher limpa tudo
    await w.findAll('select').at(0).setValue(30)
    await flush()

    expect(w.vm.form.justificativa).toBe('')
    expect(w.vm.form.itens_investimento).toHaveLength(0)
    expect(w.vm.form.itens_mao_obra).toHaveLength(0)
    expect(w.vm.caracteristicaCarregada).toBe(false)
  })
})

// ── Watcher: subclasse_id / carregamento de características ───────────────
describe('FormularioView — carregamento de características', () => {
  afterEach(() => vi.clearAllMocks())

  // Helper: monta, aguarda onMounted, seleciona classe e subclasse via setValue
  async function montarESelecionar({ erro404 = false } = {}) {
    setupApiMocks({ erro404 })
    const w = mountFormulario()
    await flush()

    // Seleciona FOMENTO MULHER (id=10) via select — dispara watcher de classe_id
    await w.findAll('select').at(0).setValue(10)
    await flush() // aguarda setTimeout(_resetandoClasse = false)

    // Seleciona subclasse AÇAÍ (id=101) via select — dispara watcher de subclasse_id
    await w.findAll('select').at(1).setValue(101)
    await flush() // aguarda chamada async da API
    return w
  }

  it('chama endpoint correto ao selecionar subclasse', async () => {
    const w = await montarESelecionar()
    expect(api.get).toHaveBeenCalledWith('/fomentos/caracteristicas/10/101')
  })

  it('preenche justificativa e entidade_elaboracao', async () => {
    const w = await montarESelecionar()
    expect(w.vm.form.justificativa).toBe('TEXTO DE JUSTIFICATIVA PRÉ-DEFINIDA')
    expect(w.vm.form.entidade_elaboracao).toBe('EMATER')
  })

  it('popula itens_investimento a partir de memoria_calculo', async () => {
    const w = await montarESelecionar()
    expect(w.vm.form.itens_investimento).toHaveLength(2)
    expect(w.vm.form.itens_investimento[0].discriminacao).toBe('SEMENTE')
    expect(w.vm.form.itens_investimento[0].subtotal).toBe(500)
  })

  it('converte visitas → qtd na mão de obra', async () => {
    const w = await montarESelecionar()
    expect(w.vm.form.itens_mao_obra[0].qtd).toBe(3)
    expect(w.vm.form.itens_mao_obra[0].subtotal).toBe(600)
  })

  it('marca caracteristicaCarregada = true após carregar', async () => {
    const w = await montarESelecionar()
    expect(w.vm.caracteristicaCarregada).toBe(true)
  })

  it('404 não exibe erro e mantém formulário em branco', async () => {
    const w = await montarESelecionar({ erro404: true })
    expect(w.vm.caracteristicaCarregada).toBe(false)
    expect(w.vm.form.justificativa).toBe('')
    expect(w.vm.form.itens_investimento).toHaveLength(0)
    expect(w.vm.erro).toBe('')
  })

  it('não chama características ao resetar subclasse por troca de classe', async () => {
    setupApiMocks()
    const w = mountFormulario()
    await flush()
    await w.findAll('select').at(0).setValue(10)
    await flush()
    await w.findAll('select').at(0).setValue(30)
    await flush()
    const chamouCaract = api.get.mock.calls
      .some(([url]) => url.includes('/fomentos/caracteristicas/'))
    expect(chamouCaract).toBe(false)
  })
})

// ── Validação ao salvar ────────────────────────────────────────────────────
describe('FormularioView — validação ao salvar', () => {
  beforeEach(() => {
    setupApiMocks()
    api.post.mockResolvedValue({ data: { id: 99 } })
  })
  afterEach(() => vi.clearAllMocks())

  it('exibe erro ao salvar sem modalidade — chamando salvar() diretamente', async () => {
    const w = mountFormulario()
    await flush()
    await w.vm.salvar()
    await nextTick()
    expect(w.vm.erro).toContain('modalidade')
  })

  it('exibe erro para FOMENTO JOVEM sem segundo beneficiário', async () => {
    const w = mountFormulario()
    await flush()

    // Seleciona FOMENTO JOVEM (id=20) via select — hierarquia já carregada
    await w.findAll('select').at(0).setValue(20)
    await flush()
    // Seleciona qualquer subclasse do JOVEM (id=201)
    await w.findAll('select').at(1).setValue(201)
    await flush()

    // Confirma que eFomentoJovem está ativo
    expect(w.vm.eFomentoJovem).toBe(true)

    // Tenta salvar sem preencher segundo beneficiário
    await w.vm.salvar()
    await nextTick()
    expect(w.vm.erro).toContain('segundo beneficiário')
  })

  it('chama api.post com payload correto ao salvar', async () => {
    const w = mountFormulario()
    await flush()

    await w.findAll('select').at(0).setValue(10)
    await flush()
    await w.findAll('select').at(1).setValue(101)
    await flush()

    await w.vm.salvar()
    await flush()

    expect(api.post).toHaveBeenCalledWith(
      '/submissoes/',
      expect.objectContaining({
        fomento_id:   2,
        produtor_id:  1,
        classe_id:    10,
        subclasse_id: 101,
      })
    )
  })

  it('botão salvar está no DOM com texto correto', async () => {
    const w = mountFormulario()
    await flush()
    const btn = w.findAll('button').find(b => b.text().includes('Salvar Formulário'))
    expect(btn).toBeDefined()
    expect(btn.exists()).toBe(true)
  })
})