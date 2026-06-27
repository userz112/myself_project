<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { loginApi } from '@/api/auth'

const router = useRouter()
const form = ref({
  username: '',
  password: '',
})
const remember = ref(false)
const msg = ref('')

onMounted(() => {
  const saved = localStorage.getItem('remembered')
  if (saved) {
    const data = JSON.parse(saved)
    form.value.username = data.username
    form.value.password = data.password
    remember.value = true
  }
})

const submit = async () => {
  msg.value = ''
  try {
    const res = await loginApi(form.value)
    localStorage.setItem('token', res.data.token.access)
    localStorage.setItem('username', res.data.username)
    if (remember.value) {
      localStorage.setItem('remembered', JSON.stringify({ username: form.value.username, password: form.value.password }))
    } else {
      localStorage.removeItem('remembered')
    }
    msg.value = res.data.msg
    setTimeout(() => router.push('/'), 1500)
  } catch (err) {
    const data = err.response?.data
    if (typeof data === 'object') {
      msg.value = Object.values(data).flat().join('；')
    } else {
      msg.value = data?.msg || '登录失败'
    }
  }
}
</script>

<template>
  <div class="login">
    <h2>用户登录</h2>
    <form @submit.prevent="submit">
      <div class="form-item">
        <label>用户名</label>
        <input v-model="form.username" placeholder="请输入用户名" required />
      </div>
      <div class="form-item">
        <label>密码</label>
        <input v-model="form.password" type="password" placeholder="请输入密码" required />
      </div>
      <label class="remember-label">
        <input v-model="remember" type="checkbox" />
        记住密码
      </label>
      <p v-if="msg" :class="msg.includes('成功') ? 'success-msg' : 'msg'">{{ msg }}</p>
      <button class="submit-btn" type="submit">登录</button>
      <p class="footer">没有账号？<router-link to="/register">去注册</router-link></p>
    </form>
  </div>
</template>

<style scoped>
.login { max-width: 400px; margin: 80px auto; padding: 40px 36px; background: #fff; border-radius: 12px; box-shadow: 0 4px 24px rgba(0,0,0,0.06); }
h2 { text-align: center; margin-bottom: 32px; font-size: 24px; font-weight: 600; color: #303133; }
.form-item { margin-bottom: 20px; }
label { display: block; font-size: 14px; font-weight: 500; color: #606266; margin-bottom: 6px; }
input { width: 100%; padding: 10px 12px; border: 1px solid #dcdfe6; border-radius: 8px; font-size: 14px; transition: border-color 0.2s; outline: none; }
input:focus { border-color: #409eff; box-shadow: 0 0 0 2px rgba(64,158,255,0.15); }
.msg { color: #f56c6c; font-size: 13px; margin-bottom: 12px; text-align: center; }
.success-msg { color: #67c23a; font-size: 13px; margin-bottom: 12px; text-align: center; }
.remember-label { display: flex; align-items: center; gap: 8px; font-size: 14px; margin-bottom: 20px; cursor: pointer; color: #606266; }
.remember-label input { width: auto; accent-color: #409eff; }
.submit-btn { width: 100%; padding: 11px; background: #409eff; color: #fff; border: none; border-radius: 8px; font-size: 15px; cursor: pointer; transition: background 0.2s; }
.submit-btn:hover { background: #66b1ff; }
.footer { text-align: center; margin-top: 20px; font-size: 14px; color: #909399; }
</style>
