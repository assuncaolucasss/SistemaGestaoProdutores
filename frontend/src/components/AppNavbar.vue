<template>
  <nav class="bg-primary-600 sticky top-0 z-50 shadow-md">
    <div class="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">

      <router-link to="/home" class="flex items-center gap-2 no-underline">
        <Sprout class="text-white w-5 h-5" />
        <span class="text-white font-bold text-sm hidden sm:block">SGP</span>
      </router-link>

      <!-- Desktop links -->
      <div class="hidden md:flex items-center gap-1">
        <NavLink to="/home">
          <Home class="w-4 h-4" /> Home
        </NavLink>

        <NavLink v-if="auth.logado" to="/produtores">
          <Users class="w-4 h-4" /> Produtores
        </NavLink>

        <NavLink v-if="auth.eSuperusuario" to="/fomentos">
          <ClipboardList class="w-4 h-4" /> Fomentos
        </NavLink>

        <NavLink v-if="auth.eSuperusuario" to="/usuarios">
          <UserCog class="w-4 h-4" /> Usuários
        </NavLink>

        <NavLink to="/sobre">
          <Info class="w-4 h-4" /> Sobre
        </NavLink>

        <template v-if="auth.logado">
          <span class="text-white/70 text-xs ml-2 mr-1 flex items-center gap-1">
            <User class="w-3 h-3" />
            {{ auth.usuario?.nome }}
            <span v-if="auth.eSuperusuario"
              class="bg-white/20 rounded-full px-2 py-0.5 text-xs ml-1">
              Admin
            </span>
          </span>
          <button @click="sair"
            class="flex items-center gap-1.5 bg-white/15 hover:bg-white/25 text-white border border-white/30 px-3 py-1.5 rounded-md text-xs cursor-pointer transition-colors">
            <LogOut class="w-3.5 h-3.5" /> Sair
          </button>
        </template>

        <template v-else>
          <NavLink to="/login">
            <LogIn class="w-4 h-4" /> Login
          </NavLink>
        </template>
      </div>

      <!-- Mobile: botão hamburger -->
      <button @click="menuAberto = !menuAberto"
        class="md:hidden text-white p-1 rounded focus:outline-none">
        <Menu v-if="!menuAberto" class="w-6 h-6" />
        <X v-else class="w-6 h-6" />
      </button>
    </div>

    <!-- Mobile menu -->
    <div v-if="menuAberto" class="md:hidden bg-primary-700 px-4 pb-4 flex flex-col gap-1">
      <MobileNavLink to="/home" @click="menuAberto = false">
        <Home class="w-4 h-4" /> Home
      </MobileNavLink>

      <MobileNavLink v-if="auth.logado" to="/produtores" @click="menuAberto = false">
        <Users class="w-4 h-4" /> Produtores
      </MobileNavLink>

      <MobileNavLink v-if="auth.eSuperusuario" to="/fomentos" @click="menuAberto = false">
        <ClipboardList class="w-4 h-4" /> Fomentos
      </MobileNavLink>

      <MobileNavLink v-if="auth.eSuperusuario" to="/usuarios" @click="menuAberto = false">
        <UserCog class="w-4 h-4" /> Usuários
      </MobileNavLink>

      <MobileNavLink to="/sobre" @click="menuAberto = false">
        <Info class="w-4 h-4" /> Sobre
      </MobileNavLink>

      <template v-if="auth.logado">
        <div class="text-white/70 text-xs px-3 py-2 flex items-center gap-1">
          <User class="w-3 h-3" /> {{ auth.usuario?.nome }}
          <span v-if="auth.eSuperusuario"
            class="bg-white/20 rounded-full px-2 py-0.5 text-xs ml-1">Admin</span>
        </div>
        <button @click="sair"
          class="flex items-center gap-2 text-white bg-white/15 hover:bg-white/25 border border-white/30 px-3 py-2 rounded-md text-sm transition-colors w-full">
          <LogOut class="w-4 h-4" /> Sair
        </button>
      </template>

      <template v-else>
        <MobileNavLink to="/login" @click="menuAberto = false">
          <LogIn class="w-4 h-4" /> Login
        </MobileNavLink>
      </template>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import {
  Sprout, Home, Users, UserCog, ClipboardList, Info, User,
  LogIn, LogOut, Menu, X
} from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()
const menuAberto = ref(false)

function sair() {
  auth.logout()
  menuAberto.value = false
  router.push('/home')
}
</script>

<script>
import { defineComponent, h } from 'vue'
import { useLink } from 'vue-router'

export const NavLink = defineComponent({
  props: ['to'],
  setup(props, { slots }) {
    const { isActive, navigate } = useLink({ to: props.to })
    return () =>
      h('button', {
        onClick: navigate,
        class: [
          'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm text-white transition-colors cursor-pointer border-none',
          isActive.value ? 'bg-white/20' : 'bg-transparent hover:bg-white/10',
        ],
      }, slots.default?.())
  },
})

export const MobileNavLink = defineComponent({
  props: ['to'],
  emits: ['click'],
  setup(props, { slots, emit }) {
    const { isActive, navigate } = useLink({ to: props.to })
    return () =>
      h('button', {
        onClick: () => { navigate(); emit('click') },
        class: [
          'flex items-center gap-2 px-3 py-2 rounded-md text-sm text-white w-full transition-colors border-none cursor-pointer',
          isActive.value ? 'bg-white/20' : 'bg-transparent hover:bg-white/10',
        ],
      }, slots.default?.())
  },
})
</script>
