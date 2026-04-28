<template>
  <div class="max-w-4xl mx-auto px-6 py-10">

    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-2xl font-bold text-primary-600">Programas de Fomento</h2>
        <p class="text-gray-400 text-sm mt-1">Programas disponíveis para os produtores cadastrados.</p>
      </div>
      <button v-if="isAdmin" @click="abrirModalNovo"
        class="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-semibold px-4 py-2 rounded-lg border-none cursor-pointer transition-colors">
        <Plus class="w-4 h-4" /> Novo Fomento
      </button>
    </div>

    <!-- Loading -->
    <div v-if="carregando" class="flex items-center justify-center gap-2 text-gray-400 py-16">
      <Loader2 class="w-5 h-5 animate-spin" /> Carregando...
    </div>

    <!-- Lista de fomentos -->
    <div v-else>
      <div v-for="f in fomentos" :key="f.id"
        class="bg-white border border-gray-200 rounded-xl mb-4 hover:shadow-md transition-shadow overflow-hidden">

        <!-- Cabeçalho do card -->
        <div class="flex items-start justify-between gap-4 px-6 py-5">
          <div class="flex items-start gap-4 flex-1">
            <div class="bg-primary-50 p-3 rounded-full mt-0.5">
              <ClipboardList class="w-5 h-5 text-primary-600" />
            </div>
            <div class="flex-1">
              <h3 class="font-semibold text-primary-600">{{ f.nome }}</h3>
              <p class="text-gray-400 text-sm mt-1">{{ f.descricao || 'Sem descrição.' }}</p>
            </div>
          </div>
          <div class="flex items-center gap-2 shrink-0">
            <button @click="toggleHierarquia(f)"
              class="flex items-center gap-1 bg-primary-50 hover:bg-primary-100 text-primary-600 text-xs px-3 py-1.5 rounded-lg border-none cursor-pointer transition-colors">
              <Layers class="w-3.5 h-3.5" />
              {{ hierarquiaAberta === f.id ? 'Fechar' : 'Modalidades' }}
            </button>
            <button v-if="isAdmin" @click="abrirModalEditar(f)"
              class="flex items-center gap-1 bg-gray-50 hover:bg-gray-100 text-gray-600 text-xs px-3 py-1.5 rounded-lg border-none cursor-pointer transition-colors">
              <Pencil class="w-3.5 h-3.5" /> Editar
            </button>
            <button v-if="isAdmin" @click="confirmarRemocao(f)"
              class="flex items-center gap-1 bg-red-50 hover:bg-red-100 text-red-700 text-xs px-3 py-1.5 rounded-lg border-none cursor-pointer transition-colors">
              <Trash2 class="w-3.5 h-3.5" /> Remover
            </button>
          </div>
        </div>

        <!-- Painel de hierarquia -->
        <div v-if="hierarquiaAberta === f.id" class="border-t border-gray-100 bg-gray-50 px-6 py-5">
          <div v-if="carregandoHierarquia" class="flex items-center gap-2 text-gray-400 text-sm py-4">
            <Loader2 class="w-4 h-4 animate-spin" /> Carregando hierarquia...
          </div>
          <div v-else>

            <!-- Seção 8K -->
            <div class="mb-6">
              <div class="flex items-center justify-between mb-3">
                <span class="text-xs font-bold text-gray-500 uppercase tracking-widest">Modalidades R$8.000,00</span>
                <button v-if="isAdmin" @click="abrirModalClasse(f.id, '8k')"
                  class="flex items-center gap-1 bg-white border border-primary-600 text-primary-600 text-xs px-2.5 py-1 rounded-lg cursor-pointer hover:bg-primary-50 transition-colors">
                  <Plus class="w-3 h-3" /> Nova Modalidade
                </button>
              </div>

              <div v-for="classe in classes8k(f.id)" :key="classe.id"
                class="bg-white border border-gray-200 rounded-lg mb-2 overflow-hidden">
                <div class="flex items-center justify-between px-4 py-3">
                  <span class="text-sm font-medium text-gray-700">{{ classe.nome }}</span>
                  <div class="flex items-center gap-2">
                    <button v-if="isAdmin" @click="abrirModalEditarClasse(classe)"
                      class="text-gray-400 hover:text-primary-600 bg-transparent border-none cursor-pointer p-1">
                      <Pencil class="w-3.5 h-3.5" />
                    </button>
                    <button v-if="isAdmin" @click="confirmarRemocaoClasse(classe)"
                      class="text-gray-400 hover:text-red-500 bg-transparent border-none cursor-pointer p-1">
                      <Trash2 class="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>

              <div class="mt-3">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-xs text-gray-400 italic">Submodalidades compartilhadas (todas as modalidades R$8.000,00)</span>
                  <button v-if="isAdmin" @click="abrirModalSubclasse(f.id, '8k')"
                    class="flex items-center gap-1 bg-white border border-gray-300 text-gray-600 text-xs px-2.5 py-1 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors">
                    <Plus class="w-3 h-3" /> Nova Submodalidade
                  </button>
                </div>
                <div class="flex flex-wrap gap-2">
                  <div v-for="sub in subclasses8k(f.id)" :key="sub.id"
                    class="flex items-center gap-1.5 bg-green-50 border border-green-200 text-green-700 text-xs px-3 py-1 rounded-full">
                    {{ sub.nome }}
                    <button v-if="isAdmin" @click="confirmarRemocaoSubclasse(sub)"
                      class="bg-transparent border-none cursor-pointer text-green-400 hover:text-red-500 p-0 leading-none">
                      <X class="w-3 h-3" />
                    </button>
                  </div>
                  <span v-if="!subclasses8k(f.id).length" class="text-xs text-gray-400 italic">Nenhuma submodalidade cadastrada.</span>
                </div>
              </div>
            </div>

            <hr class="border-gray-200 mb-6" />

            <!-- Seção 16K -->
            <div>
              <div class="flex items-center justify-between mb-3">
                <span class="text-xs font-bold text-gray-500 uppercase tracking-widest">Modalidades R$16.000,00</span>
                <button v-if="isAdmin" @click="abrirModalClasse(f.id, '16k')"
                  class="flex items-center gap-1 bg-white border border-primary-600 text-primary-600 text-xs px-2.5 py-1 rounded-lg cursor-pointer hover:bg-primary-50 transition-colors">
                  <Plus class="w-3 h-3" /> Nova Modalidade
                </button>
              </div>

              <div v-for="classe in classes16k(f.id)" :key="classe.id"
                class="bg-white border border-gray-200 rounded-lg mb-2 overflow-hidden">
                <div class="flex items-center justify-between px-4 py-3">
                  <span class="text-sm font-medium text-gray-700">{{ classe.nome }}</span>
                  <div class="flex items-center gap-2">
                    <button v-if="isAdmin" @click="abrirModalEditarClasse(classe)"
                      class="text-gray-400 hover:text-primary-600 bg-transparent border-none cursor-pointer p-1">
                      <Pencil class="w-3.5 h-3.5" />
                    </button>
                    <button v-if="isAdmin" @click="confirmarRemocaoClasse(classe)"
                      class="text-gray-400 hover:text-red-500 bg-transparent border-none cursor-pointer p-1">
                      <Trash2 class="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                <div class="px-4 pb-3">
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-xs text-gray-400 italic">Submodalidades desta modalidade</span>
                    <button v-if="isAdmin" @click="abrirModalSubclasse(f.id, '16k', classe.id)"
                      class="flex items-center gap-1 bg-white border border-gray-300 text-gray-600 text-xs px-2 py-0.5 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors">
                      <Plus class="w-3 h-3" /> Submodalidade
                    </button>
                  </div>
                  <div class="flex flex-wrap gap-2">
                    <div v-for="sub in subclasses16kDaClasse(f.id, classe.id)" :key="sub.id"
                      class="flex items-center gap-1.5 bg-blue-50 border border-blue-200 text-blue-700 text-xs px-3 py-1 rounded-full">
                      {{ sub.nome }}
                      <button v-if="isAdmin" @click="confirmarRemocaoSubclasse(sub)"
                        class="bg-transparent border-none cursor-pointer text-blue-400 hover:text-red-500 p-0 leading-none">
                        <X class="w-3 h-3" />
                      </button>
                    </div>
                    <span v-if="!subclasses16kDaClasse(f.id, classe.id).length" class="text-xs text-gray-400 italic">Nenhuma submodalidade.</span>
                  </div>
                </div>
              </div>

              <div v-if="!classes16k(f.id).length" class="text-xs text-gray-400 italic">
                Nenhuma modalidade R$16.000,00 cadastrada.
              </div>
            </div>

            <!-- Características (admin) -->
            <div v-if="isAdmin" class="mt-6 pt-4 border-t border-gray-200">
              <div class="flex items-center justify-between mb-3">
                <span class="text-xs font-bold text-gray-500 uppercase tracking-widest">Características por Combinação</span>
                <button @click="abrirModalCaracteristica(f.id)"
                  class="flex items-center gap-1 bg-white border border-primary-600 text-primary-600 text-xs px-2.5 py-1 rounded-lg cursor-pointer hover:bg-primary-50 transition-colors">
                  <Plus class="w-3 h-3" /> Definir Características
                </button>
              </div>
              <p class="text-xs text-gray-400">
                Se a combinação já existir, os dados serão carregados para edição automaticamente.
              </p>
            </div>

          </div>
        </div>
      </div>

      <div v-if="fomentos.length === 0" class="flex flex-col items-center justify-center text-gray-400 py-16 gap-2">
        <ClipboardList class="w-10 h-10 opacity-30" />
        <p class="text-sm">Nenhum programa de fomento cadastrado.</p>
      </div>
    </div>

    <!-- ── MODAL NOVO FOMENTO ─────────────────────────────── -->
    <div v-if="modalAberto" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg p-8">
        <div class="flex items-center gap-2 mb-6">
          <div class="bg-primary-50 p-2 rounded-full"><Plus class="w-5 h-5 text-primary-600" /></div>
          <h3 class="text-lg font-bold text-primary-600">Novo Fomento</h3>
        </div>
        <div class="flex flex-col gap-3 mb-5">
          <div>
            <label class="text-xs font-medium text-gray-600 mb-1 block">Nome *</label>
            <input v-model="form.nome" @input="form.nome = form.nome.toUpperCase()"
              placeholder="EX: CRÉDITO INSTALAÇÃO INCRA"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600 uppercase" />
          </div>
          <div>
            <label class="text-xs font-medium text-gray-600 mb-1 block">Descrição</label>
            <textarea v-model="form.descricao" @input="form.descricao = form.descricao.toUpperCase()" rows="3"
              placeholder="DESCRIÇÃO OPCIONAL DO PROGRAMA..."
              class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600 resize-none uppercase" />
          </div>
        </div>
        <div class="flex items-start gap-2 bg-primary-50 border border-primary-200 rounded-lg px-4 py-3 mb-5">
          <Layers class="w-4 h-4 text-primary-600 mt-0.5 shrink-0" />
          <p class="text-xs text-primary-700">
            Após criar o fomento, adicione as <strong>modalidades</strong> e
            <strong>submodalidades</strong> pelo painel <em>Modalidades</em> no card do fomento.
          </p>
        </div>
        <p v-if="erroModal" class="flex items-center gap-1.5 text-red-600 text-xs mb-3">
          <AlertCircle class="w-3.5 h-3.5" /> {{ erroModal }}
        </p>
        <div class="flex gap-3 justify-end">
          <button @click="modalAberto = false"
            class="px-5 py-2 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 cursor-pointer bg-white transition-colors">
            Cancelar
          </button>
          <button @click="salvar" :disabled="salvando"
            class="flex items-center gap-2 px-5 py-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-60 text-white text-sm font-semibold rounded-lg border-none cursor-pointer transition-colors">
            <Loader2 v-if="salvando" class="w-4 h-4 animate-spin" />
            <Save v-else class="w-4 h-4" />
            {{ salvando ? 'Salvando...' : 'Salvar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── MODAL EDITAR FOMENTO ───────────────────────────── -->
    <div v-if="modalEditar.aberto" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto p-8">
        <div class="flex items-center gap-2 mb-6">
          <div class="bg-primary-50 p-2 rounded-full"><Pencil class="w-5 h-5 text-primary-600" /></div>
          <h3 class="text-lg font-bold text-primary-600">Editar Fomento</h3>
        </div>
        <div class="flex flex-col gap-3 mb-5">
          <div>
            <label class="text-xs font-medium text-gray-600 mb-1 block">Nome *</label>
            <input v-model="modalEditar.nome" @input="modalEditar.nome = modalEditar.nome.toUpperCase()"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600 uppercase" />
          </div>
          <div>
            <label class="text-xs font-medium text-gray-600 mb-1 block">Descrição</label>
            <textarea v-model="modalEditar.descricao" @input="modalEditar.descricao = modalEditar.descricao.toUpperCase()" rows="3"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600 resize-none uppercase" />
          </div>
          <div>
            <label class="text-xs font-medium text-gray-600 mb-1 block">Entidade Responsável</label>
            <input v-model="modalEditar.entidade_nome" @input="modalEditar.entidade_nome = modalEditar.entidade_nome.toUpperCase()"
              placeholder="EX: ANEAP"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600 uppercase" />
          </div>
          <div>
            <label class="text-xs font-medium text-gray-600 mb-1 block">Edital</label>
            <input v-model="modalEditar.entidade_edital" @input="modalEditar.entidade_edital = modalEditar.entidade_edital.toUpperCase()"
              placeholder="EX: EDITAL 721/2024"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600 uppercase" />
          </div>
          <hr class="border-gray-100" />
          <p class="text-xs font-semibold text-gray-500 uppercase tracking-widest">Técnico Responsável</p>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="text-xs font-medium text-gray-600 mb-1 block">Nome</label>
              <input v-model="modalEditar.tecnico_nome" @input="modalEditar.tecnico_nome = modalEditar.tecnico_nome.toUpperCase()"
                placeholder="NOME DO TÉCNICO"
                class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600 uppercase" />
            </div>
            <div>
              <label class="text-xs font-medium text-gray-600 mb-1 block">CFTA</label>
              <input v-model="modalEditar.tecnico_cfta" @input="modalEditar.tecnico_cfta = modalEditar.tecnico_cfta.toUpperCase()"
                placeholder="EX: 12345"
                class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600 uppercase" />
            </div>
            <div class="sm:col-span-2">
              <label class="text-xs font-medium text-gray-600 mb-1 block">Telefone</label>
              <input v-model="modalEditar.tecnico_telefone"
                placeholder="(94) 99999-0000"
                class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600" />
            </div>
          </div>
        </div>
        <p v-if="modalEditar.erro" class="flex items-center gap-1.5 text-red-600 text-xs mb-3">
          <AlertCircle class="w-3.5 h-3.5" /> {{ modalEditar.erro }}
        </p>
        <div class="flex gap-3 justify-end">
          <button @click="modalEditar.aberto = false"
            class="px-5 py-2 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 cursor-pointer bg-white transition-colors">
            Cancelar
          </button>
          <button @click="salvarEdicaoFomento" :disabled="modalEditar.salvando"
            class="flex items-center gap-2 px-5 py-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-60 text-white text-sm font-semibold rounded-lg border-none cursor-pointer transition-colors">
            <Loader2 v-if="modalEditar.salvando" class="w-4 h-4 animate-spin" />
            <Save v-else class="w-4 h-4" />
            {{ modalEditar.salvando ? 'Salvando...' : 'Salvar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── MODAL NOVA/EDITAR CLASSE ───────────────────────── -->
    <div v-if="modalClasse.aberto" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-8">
        <h3 class="text-lg font-bold text-primary-600 mb-6">
          {{ modalClasse.editando ? 'Editar Modalidade' : `Nova Modalidade ${modalClasse.escopo.toUpperCase()}` }}
        </h3>
        <div class="mb-4">
          <label class="text-xs font-medium text-gray-600 mb-1 block">Nome da Modalidade</label>
          <input v-model="modalClasse.nome" @input="modalClasse.nome = modalClasse.nome.toUpperCase()"
            placeholder="EX: FOMENTO MULHER"
            class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600 uppercase" />
        </div>
        <p v-if="modalClasse.erro" class="text-red-600 text-xs mb-3 flex items-center gap-1">
          <AlertCircle class="w-3.5 h-3.5" /> {{ modalClasse.erro }}
        </p>
        <div class="flex gap-3 justify-end">
          <button @click="modalClasse.aberto = false"
            class="px-5 py-2 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 cursor-pointer bg-white">
            Cancelar
          </button>
          <button @click="salvarClasse" :disabled="modalClasse.salvando"
            class="flex items-center gap-2 px-5 py-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-60 text-white text-sm font-semibold rounded-lg border-none cursor-pointer">
            <Loader2 v-if="modalClasse.salvando" class="w-4 h-4 animate-spin" />
            <Save v-else class="w-4 h-4" />
            {{ modalClasse.salvando ? 'Salvando...' : 'Salvar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── MODAL NOVA SUBCLASSE ───────────────────────────── -->
    <div v-if="modalSubclasse.aberto" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-8">
        <h3 class="text-lg font-bold text-primary-600 mb-6">
          Nova Submodalidade {{ modalSubclasse.escopo.toUpperCase() }}
        </h3>
        <div class="mb-4">
          <label class="text-xs font-medium text-gray-600 mb-1 block">Nome da Submodalidade</label>
          <input v-model="modalSubclasse.nome" @input="modalSubclasse.nome = modalSubclasse.nome.toUpperCase()"
            placeholder="EX: AÇAÍ"
            class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600 uppercase" />
        </div>
        <p v-if="modalSubclasse.erro" class="text-red-600 text-xs mb-3 flex items-center gap-1">
          <AlertCircle class="w-3.5 h-3.5" /> {{ modalSubclasse.erro }}
        </p>
        <div class="flex gap-3 justify-end">
          <button @click="modalSubclasse.aberto = false"
            class="px-5 py-2 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 cursor-pointer bg-white">
            Cancelar
          </button>
          <button @click="salvarSubclasse" :disabled="modalSubclasse.salvando"
            class="flex items-center gap-2 px-5 py-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-60 text-white text-sm font-semibold rounded-lg border-none cursor-pointer">
            <Loader2 v-if="modalSubclasse.salvando" class="w-4 h-4 animate-spin" />
            <Save v-else class="w-4 h-4" />
            {{ modalSubclasse.salvando ? 'Salvando...' : 'Salvar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── MODAL CARACTERÍSTICAS ──────────────────────────── -->
    <div v-if="modalCaract.aberto" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-3xl max-h-[90vh] overflow-y-auto p-8">
        <div class="flex items-start justify-between gap-4 mb-2">
          <div>
            <h3 class="text-lg font-bold text-primary-600">
              {{ modalCaract.idExistente ? 'Editar Características' : 'Definir Características' }}
            </h3>
            <p class="text-xs text-gray-400 mt-1">
              Selecione a combinação e defina os textos e tabelas pré-preenchidas no formulário.
            </p>
          </div>
          <span v-if="modalCaract.carregandoExistente" class="text-xs text-gray-400 flex items-center gap-1.5">
            <Loader2 class="w-3.5 h-3.5 animate-spin" /> Carregando combinação...
          </span>
        </div>

        <!-- Classe + Subclasse — sem @change, o watch cuida do carregamento -->
        <div class="grid grid-cols-2 gap-3 mb-5">
          <div>
            <label class="text-xs font-medium text-gray-600 mb-1 block">Modalidade</label>
            <select v-model="modalCaract.classeId"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600">
              <option :value="null">Selecione...</option>
              <option v-for="c in todasClasses(modalCaract.fomentoId)" :key="c.id" :value="c.id">
                {{ c.nome }} ({{ c.escopo }})
              </option>
            </select>
          </div>
          <div>
            <label class="text-xs font-medium text-gray-600 mb-1 block">Submodalidade</label>
            <select v-model="modalCaract.subclasseId"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600">
              <option :value="null">Selecione...</option>
              <option v-for="s in subclassesParaClasse(modalCaract.classeId, modalCaract.fomentoId)" :key="s.id" :value="s.id">
                {{ s.nome }}
              </option>
            </select>
          </div>
        </div>

        <div v-if="modalCaract.idExistente"
          class="mb-5 flex items-center gap-2 text-xs text-blue-700 bg-blue-50 border border-blue-200 rounded-lg px-3 py-2">
          <CheckCircle class="w-3.5 h-3.5" />
          Esta combinação já possui características cadastradas. Você pode editar e salvar novamente.
        </div>

        <div>
          <label class="text-xs font-medium text-gray-600 mb-1 block">Entidade Responsável pela Elaboração do Projeto</label>
          <input v-model="modalCaract.entidade_elaboracao"
            @input="modalCaract.entidade_elaboracao = modalCaract.entidade_elaboracao.toUpperCase()"
            placeholder="EX: EMATER, SINDICATO RURAL, INCRA..."
            class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm uppercase focus:outline-none focus:ring-2 focus:ring-primary-600" />
        </div>
        <div class="mt-3 mb-5">
          <textarea v-model="modalCaract.texto_entidade_responsavel"
            @input="modalCaract.texto_entidade_responsavel = modalCaract.texto_entidade_responsavel.toUpperCase()"
            rows="3" placeholder="TEXTO ADICIONAL SOBRE A ENTIDADE RESPONSÁVEL..."
            class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm uppercase focus:outline-none focus:ring-2 focus:ring-primary-600 resize-y" />
        </div>

        <div class="mb-5">
          <label class="text-xs font-medium text-gray-600 mb-1 block">Justificativa</label>
          <textarea v-model="modalCaract.justificativa"
            @input="modalCaract.justificativa = modalCaract.justificativa.toUpperCase()"
            rows="4" placeholder="TEXTO PRÉ-PREENCHIDO NA JUSTIFICATIVA..."
            class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600 resize-y uppercase" />
        </div>

        <div class="mb-6">
          <h4 class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">Memória de Cálculo — Investimentos</h4>
          <div class="overflow-x-auto mb-3">
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
                <tr v-for="(item, i) in modalCaract.itensMemoria" :key="i">
                  <td class="border border-gray-200 p-1">
                    <input v-model="item.discriminacao" @input="item.discriminacao = item.discriminacao.toUpperCase()"
                      class="w-full px-2 py-1.5 text-sm border-none outline-none uppercase" />
                  </td>
                  <td class="border border-gray-200 p-1">
                    <input v-model.number="item.quantidade" type="number" @input="calcularSubtotalMemoria(item)"
                      class="w-full px-2 py-1.5 text-sm border-none outline-none text-center" />
                  </td>
                  <td class="border border-gray-200 p-1">
                    <input v-model.number="item.valor_unitario" type="number" @input="calcularSubtotalMemoria(item)"
                      class="w-full px-2 py-1.5 text-sm border-none outline-none text-center" />
                  </td>
                  <td class="border border-gray-200 p-1 text-center text-primary-600 font-semibold text-xs">
                    R$ {{ (item.subtotal || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}
                  </td>
                  <td class="border-none p-1 text-center">
                    <button @click="modalCaract.itensMemoria.splice(i, 1)"
                      class="text-red-400 hover:text-red-600 bg-transparent border-none cursor-pointer p-1">
                      <X class="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
                <tr v-if="!modalCaract.itensMemoria.length">
                  <td colspan="5" class="text-center text-gray-400 text-xs py-4 border border-dashed border-gray-200">Nenhum item adicionado.</td>
                </tr>
              </tbody>
            </table>
          </div>
          <button @click="modalCaract.itensMemoria.push(itemMemoriaVazio())"
            class="flex items-center gap-1.5 bg-primary-50 hover:bg-primary-100 border border-primary-600 text-primary-600 text-xs px-3 py-2 rounded-lg cursor-pointer transition-colors">
            <Plus class="w-3.5 h-3.5" /> Adicionar item
          </button>
        </div>

        <div class="mb-5">
          <h4 class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">Mão de Obra Especializada</h4>
          <div class="overflow-x-auto mb-3">
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
                <tr v-for="(item, i) in modalCaract.itensMaoObra" :key="i">
                  <td class="border border-gray-200 p-1">
                    <input v-model="item.descricao" @input="item.descricao = item.descricao.toUpperCase()"
                      class="w-full px-2 py-1.5 text-sm border-none outline-none uppercase" />
                  </td>
                  <td class="border border-gray-200 p-1">
                    <input v-model.number="item.visitas" type="number" @input="calcularSubtotalMao(item)"
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
                    <button @click="modalCaract.itensMaoObra.splice(i, 1)"
                      class="text-red-400 hover:text-red-600 bg-transparent border-none cursor-pointer p-1">
                      <X class="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
                <tr v-if="!modalCaract.itensMaoObra.length">
                  <td colspan="5" class="text-center text-gray-400 text-xs py-4 border border-dashed border-gray-200">Nenhum item adicionado.</td>
                </tr>
              </tbody>
            </table>
          </div>
          <button @click="modalCaract.itensMaoObra.push(itemMaoObraVazio())"
            class="flex items-center gap-1.5 bg-primary-50 hover:bg-primary-100 border border-primary-600 text-primary-600 text-xs px-3 py-2 rounded-lg cursor-pointer transition-colors">
            <Plus class="w-3.5 h-3.5" /> Adicionar item
          </button>
        </div>

        <p v-if="modalCaract.erro" class="text-red-600 text-xs mb-3 flex items-center gap-1">
          <AlertCircle class="w-3.5 h-3.5" /> {{ modalCaract.erro }}
        </p>
        <div class="flex gap-3 justify-end">
          <button @click="modalCaract.aberto = false"
            class="px-5 py-2 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 cursor-pointer bg-white">
            Cancelar
          </button>
          <button @click="salvarCaracteristica" :disabled="modalCaract.salvando || modalCaract.carregandoExistente"
            class="flex items-center gap-2 px-5 py-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-60 text-white text-sm font-semibold rounded-lg border-none cursor-pointer">
            <Loader2 v-if="modalCaract.salvando" class="w-4 h-4 animate-spin" />
            <Save v-else class="w-4 h-4" />
            {{ modalCaract.salvando ? 'Salvando...' : (modalCaract.idExistente ? 'Salvar Alterações' : 'Salvar') }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── MODAL CONFIRMAR REMOÇÃO FOMENTO ───────────────── -->
    <div v-if="fomentoParaRemover" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-8 text-center">
        <div class="flex justify-center mb-4">
          <div class="bg-red-50 p-4 rounded-full"><Trash2 class="w-7 h-7 text-red-500" /></div>
        </div>
        <h3 class="text-lg font-bold text-gray-700 mb-2">Remover fomento?</h3>
        <p class="text-gray-400 text-sm mb-6">
          Tem certeza que deseja remover <strong class="text-gray-600">{{ fomentoParaRemover.nome }}</strong>?
        </p>
        <div class="flex gap-3">
          <button @click="fomentoParaRemover = null"
            class="flex-1 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 cursor-pointer bg-white">
            Cancelar
          </button>
          <button @click="executarRemocao" :disabled="removendo"
            class="flex-1 flex items-center justify-center gap-2 py-2.5 bg-red-600 hover:bg-red-700 disabled:opacity-60 text-white text-sm font-semibold rounded-lg border-none cursor-pointer">
            <Loader2 v-if="removendo" class="w-4 h-4 animate-spin" />
            <Trash2 v-else class="w-4 h-4" />
            {{ removendo ? 'Removendo...' : 'Remover' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── MODAL CONFIRMAR REMOÇÃO CLASSE ────────────────── -->
    <div v-if="classeParaRemover" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-8 text-center">
        <div class="flex justify-center mb-4">
          <div class="bg-red-50 p-4 rounded-full"><Trash2 class="w-7 h-7 text-red-500" /></div>
        </div>
        <h3 class="text-lg font-bold text-gray-700 mb-2">Remover modalidade?</h3>
        <p class="text-gray-400 text-sm mb-6">
          Tem certeza que deseja remover a modalidade <strong class="text-gray-600">{{ classeParaRemover.nome }}</strong>?
        </p>
        <div class="flex gap-3">
          <button @click="classeParaRemover = null"
            class="flex-1 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 cursor-pointer bg-white">
            Cancelar
          </button>
          <button @click="executarRemocaoClasse" :disabled="removendoClasse"
            class="flex-1 flex items-center justify-center gap-2 py-2.5 bg-red-600 hover:bg-red-700 disabled:opacity-60 text-white text-sm font-semibold rounded-lg border-none cursor-pointer">
            <Loader2 v-if="removendoClasse" class="w-4 h-4 animate-spin" />
            <Trash2 v-else class="w-4 h-4" />
            {{ removendoClasse ? 'Removendo...' : 'Remover' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── MODAL CONFIRMAR REMOÇÃO SUBCLASSE ─────────────── -->
    <div v-if="subclasseParaRemover" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-8 text-center">
        <div class="flex justify-center mb-4">
          <div class="bg-red-50 p-4 rounded-full"><Trash2 class="w-7 h-7 text-red-500" /></div>
        </div>
        <h3 class="text-lg font-bold text-gray-700 mb-2">Remover submodalidade?</h3>
        <p class="text-gray-400 text-sm mb-6">
          Tem certeza que deseja remover a submodalidade <strong class="text-gray-600">{{ subclasseParaRemover.nome }}</strong>?
        </p>
        <div class="flex gap-3">
          <button @click="subclasseParaRemover = null"
            class="flex-1 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 cursor-pointer bg-white">
            Cancelar
          </button>
          <button @click="executarRemocaoSubclasse" :disabled="removendoSubclasse"
            class="flex-1 flex items-center justify-center gap-2 py-2.5 bg-red-600 hover:bg-red-700 disabled:opacity-60 text-white text-sm font-semibold rounded-lg border-none cursor-pointer">
            <Loader2 v-if="removendoSubclasse" class="w-4 h-4 animate-spin" />
            <Trash2 v-else class="w-4 h-4" />
            {{ removendoSubclasse ? 'Removendo...' : 'Remover' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'
import {
  ClipboardList, Plus, Trash2, Loader2, Save,
  AlertCircle, X, Layers, Pencil, CheckCircle
} from 'lucide-vue-next'

const auth    = useAuthStore()
const isAdmin = computed(() => auth.eSuperusuario)

const fomentos             = ref([])
const carregando           = ref(true)
const modalAberto          = ref(false)
const salvando             = ref(false)
const erroModal            = ref('')
const fomentoParaRemover   = ref(null)
const removendo            = ref(false)
const classeParaRemover    = ref(null)
const removendoClasse      = ref(false)
const subclasseParaRemover = ref(null)
const removendoSubclasse   = ref(false)
const hierarquiaAberta     = ref(null)
const carregandoHierarquia = ref(false)
const hierarquiaCache      = ref({})

const formVazio = () => ({ nome: '', descricao: '' })
const form = ref(formVazio())

const modalClasse = ref({
  aberto: false, fomentoId: null, escopo: '8k',
  nome: '', editando: null, salvando: false, erro: ''
})

const modalSubclasse = ref({
  aberto: false, fomentoId: null, escopo: '8k',
  classeId16k: null, nome: '', salvando: false, erro: ''
})

const modalCaract = ref({
  aberto: false, fomentoId: null, classeId: null, subclasseId: null,
  justificativa: '', entidade_elaboracao: '', texto_entidade_responsavel: '',
  itensMemoria: [], itensMaoObra: [],
  idExistente: null, carregandoExistente: false, salvando: false, erro: ''
})

const modalEditar = ref({
  aberto: false, id: null, nome: '', descricao: '',
  entidade_nome: '', entidade_edital: '',
  tecnico_nome: '', tecnico_cfta: '', tecnico_telefone: '',
  salvando: false, erro: ''
})

// ── Helpers tabelas ────────────────────────────────────
function itemMemoriaVazio() {
  return { discriminacao: '', quantidade: 0, valor_unitario: 0, subtotal: 0 }
}
function itemMaoObraVazio() {
  return { descricao: '', visitas: 0, valor_unitario: 0, subtotal: 0 }
}
function calcularSubtotalMemoria(item) {
  item.subtotal = (item.quantidade || 0) * (item.valor_unitario || 0)
}
function calcularSubtotalMao(item) {
  item.subtotal = (item.visitas || 0) * (item.valor_unitario || 0)
}

function limparCamposCaracteristica() {
  modalCaract.value.justificativa = ''
  modalCaract.value.entidade_elaboracao = ''
  modalCaract.value.texto_entidade_responsavel = ''
  modalCaract.value.itensMemoria = []
  modalCaract.value.itensMaoObra = []
  modalCaract.value.idExistente = null
  modalCaract.value.erro = ''
}

// ── Watches do modal de características ───────────────
// Ao trocar a CLASSE: limpa subclasse e campos
watch(() => modalCaract.value.classeId, (novaClasse, velhaClasse) => {
  if (!modalCaract.value.aberto) return
  // Evita disparar ao abrir o modal (quando ambos eram null)
  if (velhaClasse === undefined) return
  modalCaract.value.subclasseId = null
  limparCamposCaracteristica()
})

// Ao trocar a SUBCLASSE: carrega características existentes
watch(() => modalCaract.value.subclasseId, async (novaSubclasse) => {
  if (!modalCaract.value.aberto) return
  limparCamposCaracteristica()

  if (!novaSubclasse || !modalCaract.value.classeId) return

  modalCaract.value.carregandoExistente = true
  try {
    const { data } = await api.get(
      `/fomentos/caracteristicas/${modalCaract.value.classeId}/${novaSubclasse}`
    )
    modalCaract.value.idExistente = data.id ?? null
    modalCaract.value.justificativa = data.justificativa || ''
    modalCaract.value.entidade_elaboracao = data.entidade_elaboracao || ''
    modalCaract.value.texto_entidade_responsavel = data.texto_entidade_responsavel || ''
    modalCaract.value.itensMemoria = (data.memoria_calculo || []).map(i => ({
      discriminacao: i.discriminacao || '',
      quantidade: Number(i.quantidade || 0),
      valor_unitario: Number(i.valor_unitario || 0),
      subtotal: Number(i.subtotal ?? ((i.quantidade || 0) * (i.valor_unitario || 0)))
    }))
    modalCaract.value.itensMaoObra = (data.mao_obra_especializada || []).map(i => ({
      descricao: i.descricao || '',
      visitas: Number(i.visitas ?? i.qtd ?? 0),
      valor_unitario: Number(i.valor_unitario || 0),
      subtotal: Number(i.subtotal ?? ((i.visitas ?? i.qtd ?? 0) * (i.valor_unitario || 0)))
    }))
  } catch (err) {
    // 404 = combinação nova, sem pré-carregamento — é esperado
    if (err?.response?.status && err.response.status !== 404) {
      modalCaract.value.erro = err.response?.data?.detail || 'Erro ao carregar características.'
    }
  } finally {
    modalCaract.value.carregandoExistente = false
  }
})

// ── Helpers cache ──────────────────────────────────────
function classes8k(fomentoId) {
  return (hierarquiaCache.value[fomentoId]?.classes || []).filter(c => c.escopo === '8k')
}
function classes16k(fomentoId) {
  return (hierarquiaCache.value[fomentoId]?.classes || []).filter(c => c.escopo === '16k')
}
function todasClasses(fomentoId) {
  return hierarquiaCache.value[fomentoId]?.classes || []
}
function subclasses8k(fomentoId) {
  return (hierarquiaCache.value[fomentoId]?.subclasses || []).filter(s => s.escopo === '8k')
}
function subclasses16kDaClasse(fomentoId, classeId) {
  return (hierarquiaCache.value[fomentoId]?.subclasses || []).filter(
    s => s.escopo === '16k' && s.classe_id_ref === classeId
  )
}
function subclassesParaClasse(classeId, fomentoId) {
  if (!classeId || !fomentoId) return []
  const classe = (hierarquiaCache.value[fomentoId]?.classes || []).find(c => c.id === classeId)
  if (!classe) return []
  if (classe.escopo === '8k') return subclasses8k(fomentoId)
  return subclasses16kDaClasse(fomentoId, classeId)
}

// ── Carregar hierarquia ────────────────────────────────
async function carregarHierarquia(fomentoId) {
  carregandoHierarquia.value = true
  try {
    const { data } = await api.get(`/fomentos/${fomentoId}/hierarquia`)
    const classes    = []
    const subclasses = []
    const classIds   = new Set()
    const sub8kIds   = new Set()           // dedup global para 8k (sem classe_id_ref)
    const sub16kKeys = new Set()           // dedup para 16k com chave id+classeId

    for (const item of data.hierarquia) {
      // Dedup de classes
      if (!classIds.has(item.classe.id)) {
        classIds.add(item.classe.id)
        classes.push(item.classe)
      }

      for (const si of item.subclasses) {
        const sub = si.subclasse

        if (sub.escopo === '8k') {
          // Subclasses 8k são compartilhadas entre todas as classes — inserir só uma vez
          if (!sub8kIds.has(sub.id)) {
            sub8kIds.add(sub.id)
            subclasses.push({ ...sub, classe_id_ref: null })
          }
        } else {
          // Subclasses 16k pertencem a uma classe específica
          const chave = `${sub.id}-${item.classe.id}`
          if (!sub16kKeys.has(chave)) {
            sub16kKeys.add(chave)
            subclasses.push({ ...sub, classe_id_ref: item.classe.id })
          }
        }
      }
    }

    hierarquiaCache.value[fomentoId] = { classes, subclasses }
  } catch (err) {
    console.error(err)
  } finally {
    carregandoHierarquia.value = false
  }
}

async function toggleHierarquia(f) {
  if (hierarquiaAberta.value === f.id) {
    hierarquiaAberta.value = null
    return
  }
  hierarquiaAberta.value = f.id
  if (!hierarquiaCache.value[f.id]) {
    await carregarHierarquia(f.id)
  }
}

function invalidarCache(fomentoId) {
  delete hierarquiaCache.value[fomentoId]
}

async function recarregarHierarquiaAberta(fomentoId) {
  invalidarCache(fomentoId)
  await carregarHierarquia(fomentoId)
}

// ── FOMENTO CRUD ───────────────────────────────────────
async function carregar() {
  carregando.value = true
  try {
    const { data } = await api.get('/fomentos/')
    fomentos.value = data
  } catch (err) {
    console.error(err)
  } finally {
    carregando.value = false
  }
}

function abrirModalNovo() {
  form.value = formVazio()
  erroModal.value = ''
  modalAberto.value = true
}

async function salvar() {
  if (!form.value.nome.trim()) { erroModal.value = 'O nome do fomento é obrigatório.'; return }
  salvando.value = true
  erroModal.value = ''
  try {
    await api.post('/fomentos/', {
      nome: form.value.nome.trim().toUpperCase(),
      descricao: form.value.descricao ? form.value.descricao.toUpperCase() : null,
    })
    modalAberto.value = false
    await carregar()
  } catch (err) {
    erroModal.value = err.response?.data?.detail || 'Erro ao salvar fomento.'
  } finally {
    salvando.value = false
  }
}

function confirmarRemocao(f) { fomentoParaRemover.value = f }

async function executarRemocao() {
  removendo.value = true
  try {
    await api.delete(`/fomentos/${fomentoParaRemover.value.id}`)
    fomentos.value = fomentos.value.filter(x => x.id !== fomentoParaRemover.value.id)
    fomentoParaRemover.value = null
  } catch (err) {
    alert(err.response?.data?.detail || 'Erro ao remover fomento.')
  } finally {
    removendo.value = false
  }
}

function abrirModalEditar(f) {
  modalEditar.value = {
    aberto: true, id: f.id,
    nome: f.nome || '', descricao: f.descricao || '',
    entidade_nome: f.entidade_nome || '', entidade_edital: f.entidade_edital || '',
    tecnico_nome: f.tecnico_nome || '', tecnico_cfta: f.tecnico_cfta || '',
    tecnico_telefone: f.tecnico_telefone || '',
    salvando: false, erro: ''
  }
}

async function salvarEdicaoFomento() {
  if (!modalEditar.value.nome.trim()) { modalEditar.value.erro = 'O nome é obrigatório.'; return }
  modalEditar.value.salvando = true
  modalEditar.value.erro = ''
  try {
    await api.patch(`/fomentos/${modalEditar.value.id}`, {
      nome: modalEditar.value.nome.toUpperCase(),
      descricao: modalEditar.value.descricao ? modalEditar.value.descricao.toUpperCase() : null,
      entidade_nome: modalEditar.value.entidade_nome ? modalEditar.value.entidade_nome.toUpperCase() : null,
      entidade_edital: modalEditar.value.entidade_edital ? modalEditar.value.entidade_edital.toUpperCase() : null,
      tecnico_nome: modalEditar.value.tecnico_nome ? modalEditar.value.tecnico_nome.toUpperCase() : null,
      tecnico_cfta: modalEditar.value.tecnico_cfta ? modalEditar.value.tecnico_cfta.toUpperCase() : null,
      tecnico_telefone: modalEditar.value.tecnico_telefone || null,
    })
    modalEditar.value.aberto = false
    await carregar()
  } catch (err) {
    modalEditar.value.erro = err.response?.data?.detail || 'Erro ao salvar.'
  } finally {
    modalEditar.value.salvando = false
  }
}

// ── CLASSES ────────────────────────────────────────────
function abrirModalClasse(fomentoId, escopo) {
  modalClasse.value = { aberto: true, fomentoId, escopo, nome: '', editando: null, salvando: false, erro: '' }
}
function abrirModalEditarClasse(classe) {
  modalClasse.value = {
    aberto: true, fomentoId: classe.fomento_id, escopo: classe.escopo,
    nome: classe.nome, editando: classe, salvando: false, erro: ''
  }
}

async function salvarClasse() {
  if (!modalClasse.value.nome) { modalClasse.value.erro = 'Nome é obrigatório.'; return }
  modalClasse.value.salvando = true
  modalClasse.value.erro = ''
  const fomentoId = modalClasse.value.fomentoId
  try {
    const nomeUpper = modalClasse.value.nome.toUpperCase()
    if (modalClasse.value.editando) {
      await api.patch(`/fomentos/classes/${modalClasse.value.editando.id}`, { nome: nomeUpper })
    } else {
      await api.post(`/fomentos/${fomentoId}/classes`, {
        fomento_id: fomentoId, nome: nomeUpper, escopo: modalClasse.value.escopo,
      })
    }
    modalClasse.value.aberto = false
    await recarregarHierarquiaAberta(fomentoId)
  } catch (err) {
    modalClasse.value.erro = err.response?.data?.detail || 'Erro ao salvar.'
  } finally {
    modalClasse.value.salvando = false
  }
}

function confirmarRemocaoClasse(classe) { classeParaRemover.value = classe }

async function executarRemocaoClasse() {
  removendoClasse.value = true
  try {
    await api.delete(`/fomentos/classes/${classeParaRemover.value.id}`)
    const fomentoId = classeParaRemover.value.fomento_id
    classeParaRemover.value = null
    await recarregarHierarquiaAberta(fomentoId)
  } catch (err) {
    alert(err.response?.data?.detail || 'Erro ao remover modalidade.')
    classeParaRemover.value = null
  } finally {
    removendoClasse.value = false
  }
}

// ── SUBCLASSES ─────────────────────────────────────────
function abrirModalSubclasse(fomentoId, escopo, classeId16k = null) {
  modalSubclasse.value = { aberto: true, fomentoId, escopo, classeId16k, nome: '', salvando: false, erro: '' }
}

async function salvarSubclasse() {
  if (!modalSubclasse.value.nome) { modalSubclasse.value.erro = 'Nome é obrigatório.'; return }
  modalSubclasse.value.salvando = true
  modalSubclasse.value.erro = ''
  const fomentoId = modalSubclasse.value.fomentoId
  try {
    await api.post(`/fomentos/${fomentoId}/subclasses`, {
      fomento_id: fomentoId,
      nome: modalSubclasse.value.nome.toUpperCase(),
      escopo: modalSubclasse.value.escopo,
      classe_id: modalSubclasse.value.escopo === '16k' ? modalSubclasse.value.classeId16k : null,
    })
    modalSubclasse.value.aberto = false
    await recarregarHierarquiaAberta(fomentoId)
  } catch (err) {
    modalSubclasse.value.erro = err.response?.data?.detail || 'Erro ao salvar.'
  } finally {
    modalSubclasse.value.salvando = false
  }
}

function confirmarRemocaoSubclasse(sub) { subclasseParaRemover.value = sub }

async function executarRemocaoSubclasse() {
  removendoSubclasse.value = true
  try {
    await api.delete(`/fomentos/subclasses/${subclasseParaRemover.value.id}`)
    const fomentoId = subclasseParaRemover.value.fomento_id
    subclasseParaRemover.value = null
    await recarregarHierarquiaAberta(fomentoId)
  } catch (err) {
    alert(err.response?.data?.detail || 'Erro ao remover submodalidade.')
    subclasseParaRemover.value = null
  } finally {
    removendoSubclasse.value = false
  }
}

// ── CARACTERÍSTICAS ────────────────────────────────────
function abrirModalCaracteristica(fomentoId) {
  // Seta aberto=false antes para garantir que os watches não disparem
  // durante a reinicialização dos valores
  modalCaract.value.aberto = false
  modalCaract.value = {
    aberto: false, fomentoId,
    classeId: null, subclasseId: null,
    justificativa: '', entidade_elaboracao: '', texto_entidade_responsavel: '',
    itensMemoria: [], itensMaoObra: [],
    idExistente: null, carregandoExistente: false, salvando: false, erro: ''
  }
  // Abre depois de limpar para não disparar os watches antes da hora
  modalCaract.value.aberto = true
}

async function salvarCaracteristica() {
  if (!modalCaract.value.classeId || !modalCaract.value.subclasseId) {
    modalCaract.value.erro = 'Selecione a modalidade e a submodalidade.'
    return
  }
  modalCaract.value.salvando = true
  modalCaract.value.erro = ''

  const payload = {
    classe_id: modalCaract.value.classeId,
    subclasse_id: modalCaract.value.subclasseId,
    justificativa: modalCaract.value.justificativa
      ? modalCaract.value.justificativa.toUpperCase() : null,
    entidade_elaboracao: modalCaract.value.entidade_elaboracao
      ? modalCaract.value.entidade_elaboracao.toUpperCase() : null,
    texto_entidade_responsavel: modalCaract.value.texto_entidade_responsavel
      ? modalCaract.value.texto_entidade_responsavel.toUpperCase() : null,
    memoria_calculo: modalCaract.value.itensMemoria.map(i => ({
      ...i,
      discriminacao: i.discriminacao ? i.discriminacao.toUpperCase() : i.discriminacao
    })),
    mao_obra_especializada: modalCaract.value.itensMaoObra.map(i => ({
      ...i,
      descricao: i.descricao ? i.descricao.toUpperCase() : i.descricao
    })),
  }

  try {
    if (modalCaract.value.idExistente) {
      await api.patch(`/fomentos/caracteristicas/${modalCaract.value.idExistente}`, payload)
    } else {
      const { data } = await api.post('/fomentos/caracteristicas', payload)
      modalCaract.value.idExistente = data?.id ?? null
    }
    modalCaract.value.aberto = false
  } catch (err) {
    modalCaract.value.erro = err.response?.data?.detail || 'Erro ao salvar características.'
  } finally {
    modalCaract.value.salvando = false
  }
}

onMounted(carregar)
</script>