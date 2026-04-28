<template>
  <div class="max-w-5xl mx-auto px-6 py-10">

    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-2xl font-bold text-primary-600">Gerenciamento de Usuários</h2>
        <p class="text-gray-400 text-sm mt-1">Gerencie os acessos ao sistema.</p>
      </div>
      <button @click="abrirModal(null)"
        class="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-semibold px-4 py-2 rounded-lg border-none cursor-pointer transition-colors">
        <UserPlus class="w-4 h-4" /> Novo Usuário
      </button>
    </div>

    <!-- Tabela -->
    <div class="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
      <table class="w-full text-sm border-collapse">
        <thead>
          <tr class="bg-gray-50 text-gray-500 text-xs uppercase tracking-wide">
            <th class="text-left px-5 py-3.5 border-b border-gray-200">Nome</th>
            <th class="text-left px-5 py-3.5 border-b border-gray-200">E-mail</th>
            <th class="text-center px-5 py-3.5 border-b border-gray-200">Papel</th>
            <th class="text-center px-5 py-3.5 border-b border-gray-200">Status</th>
            <th class="text-center px-5 py-3.5 border-b border-gray-200">Criado em</th>
            <th class="text-center px-5 py-3.5 border-b border-gray-200">Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="carregando">
            <td colspan="6" class="py-10 text-center text-gray-400">
              <div class="flex items-center justify-center gap-2">
                <Loader2 class="w-4 h-4 animate-spin" /> Carregando...
              </div>
            </td>
          </tr>
          <tr v-else-if="!usuarios.length">
            <td colspan="6" class="py-10 text-center text-gray-400">
              <div class="flex flex-col items-center gap-2">
                <Users class="w-8 h-8 opacity-30" />
                <span class="text-sm">Nenhum usuário cadastrado.</span>
              </div>
            </td>
          </tr>
          <tr v-for="u in usuarios" :key="u.id"
            class="border-b border-gray-100 hover:bg-gray-50 transition-colors">
            <td class="px-5 py-3.5 font-medium text-gray-700">{{ u.nome }}</td>
            <td class="px-5 py-3.5 text-gray-400">{{ u.email }}</td>
            <td class="px-5 py-3.5 text-center">
              <span v-if="u.papel === 'superusuario'"
                class="inline-flex items-center gap-1 bg-amber-50 text-amber-700 text-xs font-semibold px-2.5 py-1 rounded-full">
                <Crown class="w-3 h-3" /> Admin
              </span>
              <span v-else
                class="inline-flex items-center gap-1 bg-primary-50 text-primary-600 text-xs font-semibold px-2.5 py-1 rounded-full">
                <User class="w-3 h-3" /> Usuário
              </span>
            </td>
            <td class="px-5 py-3.5 text-center">
              <span :class="u.ativo
                ? 'bg-primary-50 text-primary-600'
                : 'bg-red-50 text-red-600'"
                class="text-xs font-semibold px-2.5 py-1 rounded-full">
                {{ u.ativo ? 'Ativo' : 'Inativo' }}
              </span>
            </td>
            <td class="px-5 py-3.5 text-center text-gray-400 text-xs">{{ formatarData(u.criado_em) }}</td>
            <td class="px-5 py-3.5 text-center">
              <div class="flex items-center justify-center gap-2">
                <button @click="abrirModal(u)"
                  class="flex items-center gap-1 bg-primary-50 hover:bg-primary-100 border border-primary-600 text-primary-600 text-xs px-3 py-1.5 rounded-lg cursor-pointer transition-colors">
                  <Pencil class="w-3 h-3" /> Editar
                </button>
                <button @click="confirmarDelete(u)" :disabled="u.id === auth.usuario?.id"
                  :class="u.id === auth.usuario?.id
                    ? 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed'
                    : 'bg-red-50 hover:bg-red-100 border-red-400 text-red-600 cursor-pointer'"
                  class="flex items-center gap-1 border text-xs px-3 py-1.5 rounded-lg transition-colors">
                  <Trash2 class="w-3 h-3" />
                  {{ u.id === auth.usuario?.id ? 'Você' : 'Remover' }}
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal criar/editar -->
    <div v-if="modalAberto" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-8">
        <div class="flex items-center gap-2 mb-6">
          <div class="bg-primary-50 p-2 rounded-full">
            <UserPlus class="w-5 h-5 text-primary-600" />
          </div>
          <h3 class="text-lg font-bold text-primary-600">
            {{ editando ? 'Editar Usuário' : 'Novo Usuário' }}
          </h3>
        </div>

        <div class="flex flex-col gap-3">
          <div>
            <label class="text-xs font-medium text-gray-600 mb-1 block">Nome *</label>
            <input v-model="formModal.nome" placeholder="Nome completo"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600" />
          </div>
          <div>
            <label class="text-xs font-medium text-gray-600 mb-1 block">E-mail *</label>
            <input v-model="formModal.email" type="email" placeholder="email@exemplo.com"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600" />
          </div>
          <div>
            <label class="text-xs font-medium text-gray-600 mb-1 block">
              {{ editando ? 'Nova Senha (deixe vazio para manter)' : 'Senha *' }}
            </label>
            <input v-model="formModal.senha" type="password" placeholder="••••••••"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs font-medium text-gray-600 mb-1 block">Papel *</label>
              <select v-model="formModal.papel"
                class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600">
                <option value="usuario">Usuário</option>
                <option value="superusuario">Admin</option>
              </select>
            </div>
            <div>
              <label class="text-xs font-medium text-gray-600 mb-1 block">Status *</label>
              <select v-model="formModal.ativo"
                class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600">
                <option :value="true">Ativo</option>
                <option :value="false">Inativo</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Erro com suporte a quebra de linha -->
        <p v-if="erroModal"
          class="flex items-start gap-1.5 text-red-600 text-xs mt-3 whitespace-pre-line leading-relaxed">
          <AlertCircle class="w-3.5 h-3.5 mt-0.5 shrink-0" />
          {{ erroModal }}
        </p>

        <div class="flex gap-3 mt-6">
          <button @click="fecharModal"
            class="flex-1 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 cursor-pointer bg-white transition-colors">
            Cancelar
          </button>
          <button @click="salvarModal" :disabled="salvandoModal"
            class="flex-1 flex items-center justify-center gap-2 py-2.5 bg-primary-600 hover:bg-primary-700 disabled:opacity-60 text-white text-sm font-semibold rounded-lg border-none cursor-pointer transition-colors">
            <Loader2 v-if="salvandoModal" class="w-4 h-4 animate-spin" />
            <Save v-else class="w-4 h-4" />
            {{ salvandoModal ? 'Salvando...' : 'Salvar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal confirmar delete -->
    <div v-if="usuarioParaDeletar" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-8 text-center">
        <div class="flex justify-center mb-4">
          <div class="bg-red-50 p-4 rounded-full">
            <Trash2 class="w-7 h-7 text-red-500" />
          </div>
        </div>
        <h3 class="text-lg font-bold text-gray-700 mb-2">Remover usuário?</h3>
        <p class="text-gray-400 text-sm mb-6">
          Tem certeza que deseja remover <strong class="text-gray-600">{{ usuarioParaDeletar.nome }}</strong>?
          Esta ação não pode ser desfeita.
        </p>
        <div class="flex gap-3">
          <button @click="usuarioParaDeletar = null"
            class="flex-1 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 cursor-pointer bg-white transition-colors">
            Cancelar
          </button>
          <button @click="deletarUsuario" :disabled="deletando"
            class="flex-1 flex items-center justify-center gap-2 py-2.5 bg-red-600 hover:bg-red-700 disabled:opacity-60 text-white text-sm font-semibold rounded-lg border-none cursor-pointer transition-colors">
            <Loader2 v-if="deletando" class="w-4 h-4 animate-spin" />
            <Trash2 v-else class="w-4 h-4" />
            {{ deletando ? 'Removendo...' : 'Remover' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'
import { UserPlus, Users, User, Crown, Pencil, Trash2, Loader2, Save, AlertCircle } from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()

const usuarios = ref([])
const carregando = ref(false)
const modalAberto = ref(false)
const editando = ref(null)
const salvandoModal = ref(false)
const erroModal = ref('')
const usuarioParaDeletar = ref(null)
const deletando = ref(false)

const formModal = ref({ nome: '', email: '', senha: '', papel: 'usuario', ativo: true })

onMounted(async () => {
  if (!auth.eSuperusuario) return router.push('/produtores')
  await carregarUsuarios()
})

async function carregarUsuarios() {
  carregando.value = true
  try {
    const res = await api.get('/usuarios/')
    usuarios.value = res.data
  } finally {
    carregando.value = false
  }
}

function abrirModal(usuario) {
  erroModal.value = ''
  if (usuario) {
    editando.value = usuario
    formModal.value = { nome: usuario.nome, email: usuario.email, senha: '', papel: usuario.papel, ativo: usuario.ativo }
  } else {
    editando.value = null
    formModal.value = { nome: '', email: '', senha: '', papel: 'usuario', ativo: true }
  }
  modalAberto.value = true
}

function fecharModal() {
  modalAberto.value = false
  editando.value = null
}

function extrairErro(e) {
  const data = e.response?.data

  if (data?.erros?.length) {
    return data.erros.map(err => {
      if (err.campo === 'senha') {
        return `${err.mensagem}\n\nRequisitos de senha:\n• Mínimo 8 caracteres\n• Pelo menos 1 letra maiúscula\n• Pelo menos 1 letra minúscula\n• Pelo menos 1 número\n• Pelo menos 1 caractere especial (!@#$%...)`
      }
      return `${err.campo}: ${err.mensagem}`
    }).join('\n')
  }

  if (typeof data?.detail === 'string') return data.detail

  return 'Erro ao salvar. Tente novamente.'
}

async function salvarModal() {
  erroModal.value = ''

  if (!formModal.value.nome || !formModal.value.email) {
    erroModal.value = 'Nome e e-mail são obrigatórios.'
    return
  }
  if (!editando.value && !formModal.value.senha) {
    erroModal.value = 'Senha é obrigatória para novo usuário.'
    return
  }

  salvandoModal.value = true
  try {
    if (editando.value) {
      const payload = { ...formModal.value }
      if (!payload.senha) delete payload.senha
      await api.patch(`/usuarios/${editando.value.id}`, payload)
    } else {
      await api.post('/usuarios/', formModal.value)
    }
    fecharModal()
    await carregarUsuarios()
  } catch (e) {
    erroModal.value = extrairErro(e)
  } finally {
    salvandoModal.value = false
  }
}

function confirmarDelete(usuario) {
  usuarioParaDeletar.value = usuario
}

async function deletarUsuario() {
  deletando.value = true
  try {
    await api.delete(`/usuarios/${usuarioParaDeletar.value.id}`)
    usuarioParaDeletar.value = null
    await carregarUsuarios()
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao remover')
  } finally {
    deletando.value = false
  }
}

function formatarData(dt) {
  return new Date(dt).toLocaleDateString('pt-BR')
}
</script>