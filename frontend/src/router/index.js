import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import RegisterView from '../views/RegisterView.vue'
import ConnexionView from '../views/ConnexionView.vue'
import ChatView from '../views/ChatView.vue'
import AboutView from '../views/AboutView.vue'

const routes = [
  { path: '/', component: HomeView },
  { path: '/home', component: HomeView }, 
  { path: '/register', component: RegisterView },
  { path: '/login', component: ConnexionView },
  { path: '/chat', component: ChatView },
  { path: '/about', component: AboutView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard pour protéger la route /chat
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('pseudo')
  
  if (to.path === '/chat' && !isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router