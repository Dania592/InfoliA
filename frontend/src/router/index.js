import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import RegisterView from '../views/RegisterView.vue'
import ConnexionView from '../views/ConnexionView.vue'

const routes = [
  { path: '/', component: HomeView },
  { path: '/register', component: RegisterView },
  { path: '/login', component: ConnexionView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
