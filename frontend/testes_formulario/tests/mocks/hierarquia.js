export const hierarquiaMock = [
  {
    classe: { id: 10, nome: 'FOMENTO MULHER', escopo: '8k' },
    subclasses: [
      { subclasse: { id: 101, nome: 'AÇAÍ',  escopo: '8k' } },
      { subclasse: { id: 102, nome: 'CACAU', escopo: '8k' } },
    ],
  },
  {
    classe: { id: 20, nome: 'FOMENTO JOVEM', escopo: '16k' },
    subclasses: [
      { subclasse: { id: 201, nome: 'PISCICULTURA', escopo: '16k' } },
    ],
  },
  {
    classe: { id: 30, nome: 'FOMENTO STANDARD', escopo: '16k' },
    subclasses: [
      { subclasse: { id: 301, nome: 'HORTICULTURA', escopo: '16k' } },
    ],
  },
]

export const produtorMock = {
  id: 1,
  codigo_beneficiario: 'PA-001',
  nome_completo:      'MARIA DA SILVA',
  cpf_beneficiario:   '123.456.789-00',
  conjuge_nome:       'JOÃO DA SILVA',
  cpf_conjuge:        '987.654.321-00',
  assentamento:       'PALMARES II',
  lote:               'LOTE 24',
}

export const fomentoMock = {
  id: 2,
  nome:      'CRÉDITO INSTALAÇÃO INCRA',
  descricao: 'Programa de apoio aos produtores',
}

export const caracteristicaMock = {
  id: 55,
  classe_id: 10,
  subclasse_id: 101,
  justificativa:              'TEXTO DE JUSTIFICATIVA PRÉ-DEFINIDA',
  entidade_elaboracao:        'EMATER',
  texto_entidade_responsavel: 'ENTIDADE RESPONSÁVEL TEXTO',
  memoria_calculo: [
    { discriminacao: 'SEMENTE', quantidade: 10, valor_unitario:  50, subtotal:  500 },
    { discriminacao: 'ADUBO',   quantidade:  5, valor_unitario:  80, subtotal:  400 },
  ],
  mao_obra_especializada: [
    { descricao: 'TÉCNICO AGRÍCOLA', visitas: 3, valor_unitario: 200, subtotal: 600 },
  ],
}