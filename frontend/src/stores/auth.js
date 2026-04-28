import { defineStore } from 'pinia'
import api from '../services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    usuario: JSON.parse(localStorage.getItem('usuario') || 'null'),
  }),

  getters: {
    logado: (state) => !!state.token,
    eSuperusuario: (state) => state.usuario?.papel === 'superusuario',
  },

  actions: {
    async login(email, senha) {
      const form = new URLSearchParams()
      form.append('username', email)
      form.append('password', senha)

      // 1. Busca o token — se falhar (401), lança erro SEM tocar no estado
      const { data } = await api.post('/auth/token', form, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })

      // 2. Busca o usuário — se falhar, também não toca no estado
      const me = await api.get('/auth/me', {
        headers: { Authorization: `Bearer ${data.access_token}` },
      })

      // 3. Só agora salva tudo — evita re-render parcial do navbar
      this.token = data.access_token
      this.usuario = me.data
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('usuario', JSON.stringify(me.data))
    },

    logout() {
      this.token = null
      this.usuario = null
      localStorage.removeItem('token')
      localStorage.removeItem('usuario')
    },
  },
})