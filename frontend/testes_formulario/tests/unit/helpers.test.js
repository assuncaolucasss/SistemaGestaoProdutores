import { describe, it, expect } from 'vitest'

function formatarCPF(valor) {
  const nums = valor.replace(/\D/g, '').slice(0, 11)
  return nums
    .replace(/(\d{3})(\d)/,       '$1.$2')
    .replace(/(\d{3})(\d)/,       '$1.$2')
    .replace(/(\d{3})(\d{1,2})$/, '$1-$2')
}

function formatarData(data) {
  if (!data) return '___/___/______'
  const [ano, mes, dia] = data.split('-')
  const meses = ['JANEIRO','FEVEREIRO','MARÇO','ABRIL','MAIO','JUNHO',
                 'JULHO','AGOSTO','SETEMBRO','OUTUBRO','NOVEMBRO','DEZEMBRO']
  return `${dia} DE ${meses[parseInt(mes) - 1]} DE ${ano}`
}

function calcularSubtotal(item) {
  item.subtotal = (item.quantidade || 0) * (item.valor_unitario || 0)
}

function calcularSubtotalMao(item) {
  item.subtotal = (item.qtd || 0) * (item.valor_unitario || 0)
}

const u = (v) => (v || '—').toString().toUpperCase()

describe('formatarCPF', () => {
  it('formata 11 dígitos corretamente', () =>
    expect(formatarCPF('12345678900')).toBe('123.456.789-00'))
  it('aceita entrada já formatada', () =>
    expect(formatarCPF('123.456.789-00')).toBe('123.456.789-00'))
  it('formata 6 dígitos parcialmente', () =>
    expect(formatarCPF('123456')).toBe('123.456'))
  it('remove letras e caracteres especiais', () =>
    expect(formatarCPF('abc12345678900xyz')).toBe('123.456.789-00'))
  it('retorna string vazia para entrada vazia', () =>
    expect(formatarCPF('')).toBe(''))
  it('trunca em 11 dígitos', () =>
    expect(formatarCPF('12345678900999')).toBe('123.456.789-00'))
})

describe('formatarData', () => {
  it('formata data ISO corretamente', () =>
    expect(formatarData('2024-03-15')).toBe('15 DE MARÇO DE 2024'))
  it('formata janeiro', () =>
    expect(formatarData('2025-01-01')).toBe('01 DE JANEIRO DE 2025'))
  it('formata dezembro', () =>
    expect(formatarData('2026-12-31')).toBe('31 DE DEZEMBRO DE 2026'))
  it('retorna placeholder para null', () =>
    expect(formatarData(null)).toBe('___/___/______'))
  it('retorna placeholder para string vazia', () =>
    expect(formatarData('')).toBe('___/___/______'))
  it('retorna placeholder para undefined', () =>
    expect(formatarData(undefined)).toBe('___/___/______'))
})

describe('calcularSubtotal (investimento)', () => {
  it('calcula corretamente', () => {
    const item = { quantidade: 10, valor_unitario: 50, subtotal: 0 }
    calcularSubtotal(item)
    expect(item.subtotal).toBe(500)
  })
  it('retorna 0 se quantidade for 0', () => {
    const item = { quantidade: 0, valor_unitario: 100, subtotal: 999 }
    calcularSubtotal(item)
    expect(item.subtotal).toBe(0)
  })
  it('retorna 0 se valor_unitario for undefined', () => {
    const item = { quantidade: 5, valor_unitario: undefined, subtotal: 999 }
    calcularSubtotal(item)
    expect(item.subtotal).toBe(0)
  })
  it('calcula com valores decimais', () => {
    const item = { quantidade: 3, valor_unitario: 33.33, subtotal: 0 }
    calcularSubtotal(item)
    expect(item.subtotal).toBeCloseTo(99.99)
  })
})

describe('calcularSubtotalMao (mão de obra)', () => {
  it('calcula corretamente', () => {
    const item = { qtd: 3, valor_unitario: 200, subtotal: 0 }
    calcularSubtotalMao(item)
    expect(item.subtotal).toBe(600)
  })
  it('retorna 0 para qtd null', () => {
    const item = { qtd: null, valor_unitario: 200, subtotal: 999 }
    calcularSubtotalMao(item)
    expect(item.subtotal).toBe(0)
  })
})

describe('u() — helper uppercase', () => {
  it('converte para maiúsculas', () => expect(u('maria')).toBe('MARIA'))
  it('retorna — para null',      () => expect(u(null)).toBe('—'))
  it('retorna — para undefined', () => expect(u(undefined)).toBe('—'))
  it('retorna — para vazio',     () => expect(u('')).toBe('—'))
  it('converte número',          () => expect(u(42)).toBe('42'))
})

describe('totalFinal — lógica de soma', () => {
  const soma = (inv, mao) =>
    inv.reduce((s, i) => s + (i.subtotal || 0), 0) +
    mao.reduce((s, i) => s + (i.subtotal || 0), 0)

  it('soma investimentos e mão de obra', () =>
    expect(soma([{ subtotal: 500 }, { subtotal: 400 }], [{ subtotal: 600 }])).toBe(1500))
  it('retorna 0 para tabelas vazias', () =>
    expect(soma([], [])).toBe(0))
  it('trata subtotais undefined como 0', () =>
    expect(soma([{ subtotal: undefined }, { subtotal: 300 }], [])).toBe(300))
})