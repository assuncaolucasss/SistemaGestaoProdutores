<template>
  <div class="text-gray-800">

    <!-- Hero -->
    <div class="bg-gradient-to-br from-primary-600 to-green-500 text-white py-20 px-6 text-center">
      <h1 class="text-3xl sm:text-4xl font-bold mb-4">Sistema de Gestão de Produtores</h1>
      <p class="text-base sm:text-lg opacity-90 max-w-xl mx-auto mb-8">
        Plataforma de cadastro e acompanhamento de produtores rurais dos assentamentos do sul e sudeste do Pará.
      </p>
      <router-link v-if="!auth.logado" to="/login">
        <button class="bg-white text-primary-600 font-bold px-8 py-3 rounded-lg text-base hover:bg-gray-100 transition-colors cursor-pointer border-none">
          Acessar o Sistema
        </button>
      </router-link>
      <router-link v-else to="/produtores">
        <button class="bg-white text-primary-600 font-bold px-8 py-3 rounded-lg text-base hover:bg-gray-100 transition-colors cursor-pointer border-none">
          Ver Produtores
        </button>
      </router-link>
    </div>

    <!-- Assentamentos -->
    <div class="max-w-5xl mx-auto px-6 py-16">
      <h2 class="text-2xl font-bold text-primary-600 text-center mb-2">Assentamentos Cadastrados</h2>
      <p class="text-center text-gray-500 text-sm mb-10">
        Acompanhe os dados dos assentamentos atendidos pela plataforma.
      </p>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div v-for="a in assentamentos" :key="a.nome"
          class="bg-white border border-gray-200 rounded-xl p-6 text-center shadow-sm hover:shadow-md transition-shadow">
          <div class="flex justify-center mb-3">
            <div class="bg-primary-50 p-3 rounded-full">
              <Sprout class="w-6 h-6 text-primary-600" />
            </div>
          </div>
          <strong class="text-primary-600 block mb-1 text-sm">{{ a.nome }}</strong>
          <div class="text-gray-400 text-xs mb-3">{{ a.municipio }}</div>
          <span class="bg-primary-50 text-primary-600 text-xs px-3 py-1 rounded-full inline-flex items-center gap-1">
            <Users class="w-3 h-3" /> {{ a.produtores }} produtores
          </span>
        </div>
      </div>
    </div>

    <!-- Sobre -->
    <div class="bg-gray-50 py-16 px-6">
      <div class="max-w-2xl mx-auto text-center">
        <h2 class="text-2xl font-bold text-primary-600 mb-4">Sobre o Sistema</h2>
        <p class="text-gray-500 leading-relaxed text-sm sm:text-base">
          Este sistema foi desenvolvido para facilitar o cadastro, consulta e gestão dos produtores rurais
          beneficiários de programas de fomento nos assentamentos da região. Por meio da plataforma, é possível
          acessar dados atualizados, gerar formulários e acompanhar o histórico de cada produtor.
        </p>
      </div>
    </div>

    <!-- Acesso Rápido -->
    <div class="max-w-5xl mx-auto px-6 py-16">
      <h2 class="text-2xl font-bold text-primary-600 text-center mb-10">Acesso Rápido</h2>
      <div class="grid gap-5"
        :class="auth.logado ? 'grid-cols-1 sm:grid-cols-2' : 'grid-cols-1 sm:grid-cols-3'">

        <router-link to="/produtores" class="no-underline">
          <div class="bg-white border border-gray-200 rounded-xl p-8 text-center hover:shadow-lg transition-shadow cursor-pointer">
            <div class="flex justify-center mb-4">
              <div class="bg-primary-50 p-4 rounded-full">
                <Users class="w-7 h-7 text-primary-600" />
              </div>
            </div>
            <strong class="text-primary-600 block mb-1">Produtores</strong>
            <p class="text-gray-400 text-xs mt-1">Consultar cadastros</p>
          </div>
        </router-link>

        <router-link to="/fomentos" class="no-underline">
          <div class="bg-white border border-gray-200 rounded-xl p-8 text-center hover:shadow-lg transition-shadow cursor-pointer">
            <div class="flex justify-center mb-4">
              <div class="bg-primary-50 p-4 rounded-full">
                <ClipboardList class="w-7 h-7 text-primary-600" />
              </div>
            </div>
            <strong class="text-primary-600 block mb-1">Fomentos</strong>
            <p class="text-gray-400 text-xs mt-1">Programas disponíveis</p>
          </div>
        </router-link>

        <!-- Card login — só aparece se não estiver logado -->
        <router-link v-if="!auth.logado" to="/login" class="no-underline">
          <div class="bg-primary-600 rounded-xl p-8 text-center hover:bg-primary-700 transition-colors cursor-pointer">
            <div class="flex justify-center mb-4">
              <div class="bg-white/20 p-4 rounded-full">
                <LogIn class="w-7 h-7 text-white" />
              </div>
            </div>
            <strong class="text-white block mb-1">Login</strong>
            <p class="text-white/70 text-xs mt-1">Entrar no sistema</p>
          </div>
        </router-link>

      </div>
    </div>

  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import { Sprout, Users, ClipboardList, LogIn } from 'lucide-vue-next'

const auth = useAuthStore()

const assentamentos = [
  { nome: 'PA Brasília',                   municipio: 'Pará', produtores: 82  },
  { nome: 'PA Maria De Lourdes Rodrigues', municipio: 'Pará', produtores: 74  },
  { nome: 'PA Montepío',                   municipio: 'Pará', produtores: 149 },
  { nome: 'PA União Ameirco Santana',      municipio: 'Pará', produtores: 49  },
]
</script>
