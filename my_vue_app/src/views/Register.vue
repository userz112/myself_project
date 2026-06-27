<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { registerApi } from '@/api/auth'

const router = useRouter()
const form = ref({
  username: '',
  email: '',
  password: '',
  confirm_password: '',
  phone: '',
  gender: 'male',
})
const msg = ref('')

const submit = async () => {
  msg.value = ''
  if (form.value.password !== form.value.confirm_password) {
    msg.value = '两次密码不一致'
    return
  }
  try {
    const res = await registerApi(form.value)
    msg.value = res.data.msg
    setTimeout(() => router.push('/login'), 1500)
  } catch (err) {
    const data = err.response?.data
    if (typeof data === 'object') {
      msg.value = Object.values(data).flat().join('；')
    } else {
      msg.value = data?.msg || '注册失败'
    }
  }
}
</script>

<template>
  <div class="register">
    <h2>用户注册</h2>
    <form @submit.prevent="submit">
      <div class="form-item">
        <label>用户名</label>
        <input v-model="form.username" placeholder="请输入用户名" required />
      </div>
      <div class="form-item">
        <label>邮箱</label>
        <input v-model="form.email" type="email" placeholder="请输入邮箱" required />
      </div>
      <div class="form-item">
        <label>手机号</label>
        <input v-model="form.phone" placeholder="11位手机号" required />
      </div>
      <div class="form-item">
        <label>密码</label>
        <input v-model="form.password" type="password" placeholder="至少8位密码" required />
      </div>
      <div class="form-item">
        <label>确认密码</label>
        <input v-model="form.confirm_password" type="password" placeholder="再次输入密码" required />
      </div>
      <div class="form-item">
        <label>性别</label>
        <select v-model="form.gender">
          <option value="male">男</option>
          <option value="female">女</option>
          <option value="other">其他</option>
        </select>
      </div>
      <p v-if="msg" :class="msg.includes('成功') ? 'success-msg' : 'msg'">{{ msg }}</p>
      <button class="submit-btn" type="submit">注册</button>
      <p class="footer">已有账号？<router-link to="/login">去登录</router-link></p>
    </form>
  </div>
</template>

<style scoped>
.register { max-width: 440px; margin: 40px auto; padding: 36px 32px; background: #fff; border-radius: 12px; box-shadow: 0 4px 24px rgba(0,0,0,0.06); }
h2 { text-align: center; margin-bottom: 28px; font-size: 24px; font-weight: 600; color: #303133; }
.form-item { margin-bottom: 18px; }
label { display: block; font-size: 14px; font-weight: 500; color: #606266; margin-bottom: 6px; }
input, select { width: 100%; padding: 10px 12px; border: 1px solid #dcdfe6; border-radius: 8px; font-size: 14px; transition: border-color 0.2s; outline: none; }
input:focus, select:focus { border-color: #409eff; box-shadow: 0 0 0 2px rgba(64,158,255,0.15); }
.msg { color: #f56c6c; font-size: 13px; margin-bottom: 12px; text-align: center; }
.success-msg { color: #67c23a; font-size: 13px; margin-bottom: 12px; text-align: center; }
.submit-btn { width: 100%; padding: 11px; background: #409eff; color: #fff; border: none; border-radius: 8px; font-size: 15px; cursor: pointer; transition: background 0.2s; margin-top: 4px; }
.submit-btn:hover { background: #66b1ff; }
.footer { text-align: center; margin-top: 20px; font-size: 14px; color: #909399; }
</style>
