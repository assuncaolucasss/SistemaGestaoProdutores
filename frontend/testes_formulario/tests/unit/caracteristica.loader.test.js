import { describe, it, expect } from 'vitest'
import { caracteristicaMock } from '../mocks/hierarquia.js'

function normalizarCaracteristica(data) {
  return {
    justificativa:              data.justificativa              || '',
    entidade_elaboracao:        data.entidade_elaboracao        || '',
    texto_entidade_responsavel: data.texto_entidade_responsavel || '',

    itens_investimento: (data.memoria_calculo || []).map(i => ({
      discriminacao:  (i.discriminacao  || '').toUpperCase(),
      quantidade:     Number(i.quantidade     ?? 0),
      valor_unitario: Number(i.valor_unitario ?? 0),
      subtotal:       Number(i.subtotal ?? (Number(i.quantidade ?? 0) * Number(i.valor_unitario ?? 0))),
    })),

    itens_mao_obra: (data.mao_obra_especializada || []).map(i => ({
      descricao:      (i.descricao      || '').toUpperCase(),
      qtd:            Number(i.visitas ?? i.qtd ?? 0),
      valor_unitario: Number(i.valor_unitario ?? 0),
      subtotal:       Number(i.subtotal ?? (Number(i.visitas ?? i.qtd ?? 0) * Number(i.valor_unitario ?? 0))),
    })),
  }
}

describe('normalizarCaracteristica — campos de texto', () => {
  it('mapeia campos de texto corretamente', () => {
    const r = normalizarCaracteristica(caracteristicaMock)
    expect(r.justificativa).toBe('TEXTO DE JUSTIFICATIVA PRÉ-DEFINIDA')
    expect(r.entidade_elaboracao).toBe('EMATER')
    expect(r.texto_entidade_responsavel).toBe('ENTIDADE RESPONSÁVEL TEXTO')
  })
  it('usa string vazia como fallback para campos ausentes', () => {
    const r = normalizarCaracteristica({})
    expect(r.justificativa).toBe('')
    expect(r.entidade_elaboracao).toBe('')
  })
})

describe('normalizarCaracteristica — memoria_calculo → itens_investimento', () => {
  it('mapeia itens com uppercase na discriminacao', () => {
    const r = normalizarCaracteristica(caracteristicaMock)
    expect(r.itens_investimento).toHaveLength(2)
    expect(r.itens_investimento[0]).toEqual({
      discriminacao: 'SEMENTE', quantidade: 10, valor_unitario: 50, subtotal: 500,
    })
  })
  it('retorna array vazio quando campo não existe', () => {
    expect(normalizarCaracteristica({}).itens_investimento).toEqual([])
  })
  it('calcula subtotal quando a API não retorna o campo', () => {
    const r = normalizarCaracteristica({
      memoria_calculo: [{ discriminacao: 'FERRAMENTA', quantidade: 4, valor_unitario: 75 }],
    })
    expect(r.itens_investimento[0].subtotal).toBe(300)
  })
  it('usa 0 para valores numéricos ausentes', () => {
    const r = normalizarCaracteristica({
      memoria_calculo: [{ discriminacao: 'SEM VALORES' }],
    })
    expect(r.itens_investimento[0].quantidade).toBe(0)
    expect(r.itens_investimento[0].subtotal).toBe(0)
  })
})

describe('normalizarCaracteristica — mao_obra_especializada → itens_mao_obra', () => {
  it('mapeia visitas → qtd (campo legado do backend)', () => {
    const r = normalizarCaracteristica(caracteristicaMock)
    expect(r.itens_mao_obra[0].qtd).toBe(3)
    expect(r.itens_mao_obra[0].subtotal).toBe(600)
  })
  it('usa qtd quando visitas não existe', () => {
    const r = normalizarCaracteristica({
      mao_obra_especializada: [{ descricao: 'X', qtd: 2, valor_unitario: 150, subtotal: 300 }],
    })
    expect(r.itens_mao_obra[0].qtd).toBe(2)
  })
  it('prioriza visitas sobre qtd quando ambos existem', () => {
    const r = normalizarCaracteristica({
      mao_obra_especializada: [{ descricao: 'X', visitas: 5, qtd: 99, valor_unitario: 100, subtotal: 500 }],
    })
    expect(r.itens_mao_obra[0].qtd).toBe(5)
  })
  it('calcula subtotal quando não vem da API', () => {
    const r = normalizarCaracteristica({
      mao_obra_especializada: [{ descricao: 'ENG', visitas: 2, valor_unitario: 500 }],
    })
    expect(r.itens_mao_obra[0].subtotal).toBe(1000)
  })
})