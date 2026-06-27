<script setup>
import { ref, onMounted } from 'vue'
import { get, put, post } from '@/api/index'

const user = ref(null)
const loading = ref(true)
const editing = ref(false)
const msg = ref('')
const form = ref({ username: '', email: '', phone: '', gender: 'male' })

const genderMap = { male: '男', female: '女', other: '其他' }
const genderOptions = [
  { value: 'male', label: '男' },
  { value: 'female', label: '女' },
  { value: 'other', label: '其他' },
]

const fetchUser = async () => {
  try {
    const res = await get('/users/me/')
    user.value = res.data
  } finally {
    loading.value = false
  }
}

const startEdit = () => {
    form.value = {
      username: user.value.username || '',
      email: user.value.email || '',
      phone: user.value.phone || '',
      gender: user.value.gender || 'male',
    }
  editing.value = true
  msg.value = ''
}

const fileInput = ref(null)
const uploading = ref(false)

const uploadAvatar = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  uploading.value = true
  const fd = new FormData()
  fd.append('avatar', file)
  try {
    const res = await post('/users/avatar/', fd)
    user.value.avatar = res.data.avatar
  } catch (err) {
    const data = err.response?.data
    msg.value = data ? Object.values(data).flat().join('；') : '上传失败'
  } finally {
    uploading.value = false
    e.target.value = ''
  }
}

const cancelEdit = () => {
  editing.value = false
  msg.value = ''
}

const save = async () => {
  msg.value = ''
  try {
    const res = await put('/users/me/', form.value)
    msg.value = res.data.msg
    editing.value = false
    await fetchUser()
  } catch (err) {
    const data = err.response?.data
    if (typeof data === 'object') {
      msg.value = Object.values(data).flat().join('；')
    } else {
      msg.value = '更新失败'
    }
  }
}

onMounted(fetchUser)
</script>

<template>
  <div class="user-info-page">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="user" class="info-card">
      <div class="avatar-wrap" @click="$refs.fileInput.click()">
        <img :src="user.avatar || '/placeholder.jpg'" class="avatar" />
        <div v-if="!uploading" class="avatar-overlay">更换头像</div>
        <div v-else class="avatar-overlay">上传中...</div>
      </div>
      <input ref="fileInput" type="file" accept="image/jpeg,image/png" hidden @change="uploadAvatar" />
      <h2>{{ user.username }}</h2>

      <template v-if="!editing">
        <div class="info-list">
          <div class="info-item"><span class="label">用户名</span><span class="value">{{ user.username }}</span></div>
          <div class="info-item"><span class="label">邮箱</span><span class="value">{{ user.email || '未设置' }}</span></div>
          <div class="info-item"><span class="label">手机号</span><span class="value">{{ user.phone || '未设置' }}</span></div>
          <div class="info-item"><span class="label">性别</span><span class="value">{{ genderMap[user.gender] || '未设置' }}</span></div>
        </div>
        <button class="edit-btn" @click="startEdit">编辑信息</button>
      </template>

      <template v-else>
        <div class="edit-form">
          <div class="form-item">
            <label>用户名</label>
            <input v-model="form.username" placeholder="请输入用户名" />
          </div>
          <div class="form-item">
            <label>邮箱</label>
            <input v-model="form.email" type="email" placeholder="请输入邮箱" />
          </div>
          <div class="form-item">
            <label>手机号</label>
            <input v-model="form.phone" placeholder="11位手机号" />
          </div>
          <div class="form-item">
            <label>性别</label>
            <select v-model="form.gender">
              <option v-for="opt in genderOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
          </div>
          <p v-if="msg" class="msg">{{ msg }}</p>
          <div class="form-actions">
            <button class="save-btn" @click="save">保存</button>
            <button class="cancel-btn" @click="cancelEdit">取消</button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.user-info-page { max-width: 500px; margin: 60px auto; padding: 0 20px; }
.loading { text-align: center; padding: 80px 0; color: #909399; }
.info-card { background: #fff; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); padding: 40px; text-align: center; }
.avatar-wrap { width: 100px; height: 100px; margin: 0 auto 16px; border-radius: 50%; overflow: hidden; border: 3px solid #e8eaee; position: relative; cursor: pointer; }
.avatar-wrap:hover .avatar-overlay { opacity: 1; }
.avatar { width: 100%; height: 100%; object-fit: cover; }
.avatar-overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.5); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 12px; opacity: 0; transition: opacity 0.2s; }
h2 { margin: 0 0 28px; font-size: 22px; color: #303133; }
.info-list { text-align: left; margin-bottom: 24px; }
.info-item { display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #f0f2f5; }
.info-item:last-child { border-bottom: none; }
.label { font-size: 14px; color: #909399; }
.value { font-size: 14px; color: #303133; font-weight: 500; }
.edit-btn { padding: 8px 28px; background: #409eff; color: #fff; border: none; border-radius: 6px; font-size: 14px; cursor: pointer; transition: background 0.2s; }
.edit-btn:hover { background: #66b1ff; }

.edit-form { text-align: left; }
.form-item { margin-bottom: 18px; }
.form-item label { display: block; font-size: 14px; font-weight: 500; color: #606266; margin-bottom: 6px; }
.form-item input, .form-item select { width: 100%; padding: 10px 12px; border: 1px solid #dcdfe6; border-radius: 8px; font-size: 14px; outline: none; transition: border-color 0.2s; box-sizing: border-box; }
.form-item input:focus, .form-item select:focus { border-color: #409eff; box-shadow: 0 0 0 2px rgba(64,158,255,0.12); }
.msg { color: #f56c6c; font-size: 13px; margin-bottom: 12px; text-align: center; }
.form-actions { display: flex; gap: 12px; margin-top: 8px; }
.save-btn { flex: 1; padding: 10px; background: #409eff; color: #fff; border: none; border-radius: 6px; font-size: 14px; cursor: pointer; }
.save-btn:hover { background: #66b1ff; }
.cancel-btn { flex: 1; padding: 10px; background: #fff; border: 1px solid #dcdfe6; border-radius: 6px; font-size: 14px; cursor: pointer; color: #606266; }
.cancel-btn:hover { border-color: #409eff; color: #409eff; }
</style>
