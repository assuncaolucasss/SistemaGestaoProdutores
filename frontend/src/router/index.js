import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import HomeView from '../views/HomeView.vue'
import SobreView from '../views/SobreView.vue'
import ProdutoresView from '../views/ProdutoresView.vue'
import ProdutorDetalheView from '../views/ProdutorDetalheView.vue'
import FormularioView from '../views/FormularioView.vue'

const routes = [
  { path: '/', redirect: '/home' },
  { path: '/home', component: HomeView },
  { path: '/sobre', component: SobreView },
  { path: '/login', component: LoginView },
  { path: '/produtores', component: ProdutoresView, meta: { requiresAuth: true } },
  { path: '/produtores/:id', component: ProdutorDetalheView, meta: { requiresAuth: true } },
  { path: '/formulario/:produtorId/:fomentoId', component: FormularioView, meta: { requiresAuth: true } },
  {
    path: '/fomentos',
    component: () => import('../views/FomentosView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/usuarios',
    component: () => import('../views/UsuariosView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/recuperar-senha',
    name: 'recuperar-senha',
    component: () => import('../views/RecuperarSenhaView.vue'),
    meta: { publico: true }
  },
  {
    path: '/verificar-codigo',
    name: 'verificar-codigo',
    component: () => import('../views/VerificarCodigoView.vue'),
    meta: { publico: true }
  },
  {
    path: '/nova-senha',
    name: 'nova-senha',
    component: () => import('../views/NovaSenhaView.vue'),
    meta: { publico: true }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _, next) => {
  const usuario = JSON.parse(localStorage.getItem('usuario') || 'null')
  const token = localStorage.getItem('token')

  if (to.meta.requiresAuth && !token) return next('/login')

  // ✅ Só redireciona para /produtores se o token E o usuário existirem
  // Evita redirect enquanto o login ainda está sendo processado
  if (to.path === '/login' && token && usuario) return next('/produtores')

  if (to.meta.requiresAdmin) {
    if (!usuario || usuario.papel !== 'superusuario') return next('/produtores')
  }

  next()
})

export default router