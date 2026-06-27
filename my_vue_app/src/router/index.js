import { createRouter, createWebHistory } from 'vue-router'
import Register from '@/views/Register.vue'
import Login from '@/views/Login.vue'
import Home from '@/views/Home.vue'
import Favorites from '@/views/Favorites.vue'
import UserInfo from '@/views/UserInfo.vue'
import Assistant from '@/views/Assistant.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/register', name: 'register', component: Register },
    { path: '/login', name: 'login', component: Login },
    { path: '/', name: 'home', component: Home },
    { path: '/favorites', name: 'favorites', component: Favorites },
    { path: '/user-info', name: 'userInfo', component: UserInfo },
    { path: '/assistant', name: 'assistant', component: Assistant },
  ],
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && to.path !== '/register' && to.path !== '/logout' && to.path !== '/assistant' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
