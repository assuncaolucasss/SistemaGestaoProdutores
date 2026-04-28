<template>
  <div class="max-w-2xl mx-auto px-6 py-16 text-gray-700 leading-relaxed">

    <!-- Hero -->
    <div class="flex items-center gap-3 mb-6">
      <div class="bg-primary-50 p-3 rounded-full">
        <Sprout class="w-7 h-7 text-primary-600" />
      </div>
      <h2 class="text-2xl font-bold text-primary-600">Sobre o Sistema</h2>
    </div>

    <p class="text-gray-500 mb-4">
      O Sistema de Gestão de Assentamentos foi desenvolvido para facilitar o cadastro,
      consulta e acompanhamento de produtores rurais beneficiários de programas de fomento
      nos assentamentos do sul e sudeste do Pará.
    </p>
    <p class="text-gray-500 mb-10">
      Por meio da plataforma, técnicos e gestores podem acessar dados atualizados de cada
      produtor, gerar formulários e registrar informações sobre programas como DAP/CAF,
      homologações e atividades produtivas.
    </p>

    <hr class="border-gray-100 mb-8" />

    <!-- Assentamentos -->
    <h3 class="text-base font-semibold text-primary-600 uppercase tracking-widest mb-4">
      Assentamentos Atendidos
    </h3>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-10">
      <div v-for="a in assentamentos" :key="a"
        class="flex items-center gap-3 bg-white border border-gray-200 rounded-xl px-4 py-3">
        <div class="bg-primary-50 p-1.5 rounded-full">
          <MapPin class="w-3.5 h-3.5 text-primary-600" />
        </div>
        <span class="text-sm text-gray-600 font-medium">{{ a }}</span>
      </div>
    </div>

    <hr class="border-gray-100 mb-8" />

    <!-- Desenvolvimento -->
    <h3 class="text-base font-semibold text-primary-600 uppercase tracking-widest mb-3">
      Desenvolvimento
    </h3>
    <div class="flex items-center gap-3 bg-primary-50 border border-primary-100 rounded-xl px-5 py-4">
      <Code2 class="w-5 h-5 text-primary-600 shrink-0" />
      <p class="text-sm text-gray-600">
        Sistema desenvolvido por <strong class="text-primary-600">ABLtech</strong>.
        Todos os direitos reservados.
      </p>
    </div>

  </div>
</template>

<script setup>
import { Sprout, MapPin, Code2 } from 'lucide-vue-next'

const assentamentos = [
  'PA Brasília',
  'PA Maria De Lourdes Rodrigues',
  'PA Montepío',
  'PA União Ameirco Santana',
]
</script>
