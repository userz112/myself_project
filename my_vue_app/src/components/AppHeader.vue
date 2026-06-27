<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const username = ref(localStorage.getItem('username') || '')
const isLoggedIn = ref(!!localStorage.getItem('token'))
const showDropdown = ref(false)

watch(() => route.path, () => {
  username.value = localStorage.getItem('username') || ''
  isLoggedIn.value = !!localStorage.getItem('token')
  showDropdown.value = false
})

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
}

const closeDropdown = () => {
  showDropdown.value = false
}

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  username.value = ''
  showDropdown.value = false
  router.push('/login')
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <header class="app-header">
    <div class="header-inner">
      <div class="nav-left">
        <h2 class="logo">🏠 二手房交易平台</h2>
        <router-link to="/" class="nav-link">首页</router-link>
        <router-link to="/favorites" class="nav-link">我的收藏</router-link>
        <router-link to="/assistant" class="nav-link ai-nav">🤖 AI 助手</router-link>
      </div>
      <div class="user-area">
        <template v-if="isLoggedIn">
          <div class="user-dropdown" @click.stop="toggleDropdown">
            <span class="username-trigger">欢迎，{{ username || '用户' }} ▾</span>
            <div v-if="showDropdown" class="dropdown-menu" @click.stop>
              <div class="dropdown-item" @click="closeDropdown">
                <router-link to="/user-info" class="dropdown-link">👤 用户信息</router-link>
              </div>
              <div class="dropdown-divider"></div>
              <div class="dropdown-item logout-item" @click="logout">🚪 安全退出</div>
            </div>
          </div>
          <div v-if="showDropdown" class="dropdown-overlay" @click="closeDropdown"></div>
        </template>
        <template v-else>
          <span class="login-trigger" @click="goToLogin">登录</span>
        </template>
      </div>
    </div>
  </header>
</template>

<style scoped>
.app-header { background: #fff; border-bottom: 1px solid #e8eaee; padding: 0 24px; position: sticky; top: 0; z-index: 100; }
.header-inner { max-width: 1400px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; height: 60px; }
.logo { margin: 0; font-size: 22px; font-weight: 700; background: linear-gradient(135deg, #409eff, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.nav-left { display: flex; align-items: center; gap: 28px; }
.nav-link { font-size: 14px; color: #606266; text-decoration: none; transition: color 0.2s; }
.nav-link:hover { color: #409eff; }
.nav-link.router-link-active { color: #409eff; font-weight: 500; }
.ai-nav { background: linear-gradient(135deg, #409eff, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 600; }
.user-area { display: flex; align-items: center; gap: 20px; position: relative; }

/* 登录状态 */
.user-dropdown { position: relative; cursor: pointer; }
.username-trigger { font-size: 14px; color: #606266; padding: 6px 12px; border-radius: 6px; transition: background 0.2s; user-select: none; }
.username-trigger:hover { background: #f0f2f5; }
.dropdown-overlay { position: fixed; inset: 0; z-index: 99; background: transparent; }
.dropdown-menu { position: absolute; top: calc(100% + 6px); right: 0; min-width: 150px; background: #fff; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.12); z-index: 100; overflow: hidden; }
.dropdown-item { padding: 10px 16px; font-size: 14px; color: #303133; cursor: pointer; transition: background 0.15s; }
.dropdown-item:hover { background: #f5f7fa; }
.dropdown-link { color: #303133; text-decoration: none; display: block; }
.logout-item { color: #f56c6c; }
.logout-item:hover { background: #fef0f0; }
.dropdown-divider { height: 1px; background: #f0f2f5; margin: 0; }

/* 未登录 */
.login-trigger { font-size: 14px; color: #409eff; cursor: pointer; padding: 6px 16px; border: 1px solid #409eff; border-radius: 6px; transition: all 0.2s; }
.login-trigger:hover { background: #409eff; color: #fff; }
</style>
