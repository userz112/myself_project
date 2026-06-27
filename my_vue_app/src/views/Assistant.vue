<script setup>
import { ref, nextTick, watch, onMounted } from 'vue'
import { sendMessageStream } from '@/api/assistant'

const messages = ref([])
const input = ref('')
const loading = ref(false)
const chatRef = ref(null)

const threadId = ref(localStorage.getItem('assistant_thread_id') || Date.now().toString())
localStorage.setItem('assistant_thread_id', threadId.value)

const scrollToBottom = async () => {
  await nextTick()
  if (chatRef.value) {
    chatRef.value.scrollTop = chatRef.value.scrollHeight
  }
}

const handleSend = async () => {
  const text = input.value.trim()
  if (!text || loading.value) return

  messages.value.push({ role: 'user', content: text })
  input.value = ''
  await scrollToBottom()

  // 插入空消息占位，流式填充
  messages.value.push({ role: 'assistant', content: '', isError: false })
  const aiIdx = messages.value.length - 1  // 用索引访问响应式数组，不用原始对象引用
  loading.value = true

  sendMessageStream(
    text,
    threadId.value,
    (token) => {
      messages.value[aiIdx].content += token
      scrollToBottom()
    },
    () => {
      loading.value = false
      scrollToBottom()
    },
    (err) => {
      messages.value[aiIdx].content = `抱歉，AI 助手暂时无法响应：${err}`
      messages.value[aiIdx].isError = true
      loading.value = false
    },
  )
}

const handleKeydown = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

const quickQuestions = [
  '广州有没有300万以内的三室一厅？',
  '北京首套房首付比例是多少？',
  '买二手房要注意什么？',
  '公积金贷款额度是多少？',
]

const handleQuick = (q) => {
  input.value = q
  handleSend()
}

const clearChat = () => {
  messages.value = []
  threadId.value = Date.now().toString()
  localStorage.setItem('assistant_thread_id', threadId.value)
}

const formatContent = (text) => {
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
    .replace(/^(\d+)\.\s/gm, '<strong>$1.</strong> ')
}

watch(messages, () => {
  localStorage.setItem('assistant_messages', JSON.stringify(messages.value.slice(-20)))
}, { deep: true })

try {
  const saved = localStorage.getItem('assistant_messages')
  if (saved) messages.value = JSON.parse(saved)
} catch {}

onMounted(() => {
  scrollToBottom()
})
</script>

<template>
  <div class="assistant-layout">
    <div class="chat-panel">
      <div class="chat-header">
        <div class="header-left">
          <span class="ai-icon">🤖</span>
          <div>
            <h2>宜居助手</h2>
            <p class="subtitle">AI 房产顾问 · 智能问答</p>
          </div>
        </div>
        <button class="clear-btn" @click="clearChat" title="新建对话">+ 新对话</button>
      </div>

      <div class="chat-messages" ref="chatRef">
        <div v-if="messages.length === 0" class="welcome">
          <div class="welcome-icon">🏠</div>
          <h3>你好，我是宜居助手</h3>
          <p>我可以帮你搜索房源、解答购房政策、提供选房建议</p>
          <div class="quick-grid">
            <button
              v-for="q in quickQuestions"
              :key="q"
              class="quick-chip"
              @click="handleQuick(q)"
            >{{ q }}</button>
          </div>
        </div>

        <div
          v-for="(msg, i) in messages"
          :key="i"
          class="msg-row"
          :class="msg.role"
        >
          <div class="msg-avatar">
            {{ msg.role === 'user' ? '👤' : '🤖' }}
          </div>
          <div class="msg-bubble" :class="{ error: msg.isError }">
            <div class="msg-text" v-html="formatContent(msg.content)"></div>
            <!-- 流式输出中的闪烁光标 -->
            <span
              v-if="loading && i === messages.length - 1 && msg.role === 'assistant'"
              class="cursor-blink"
            >▍</span>
          </div>
        </div>

        <!-- 首次加载中（还没有 assistant 消息时） -->
        <div v-if="loading && messages.length === 0" class="msg-row assistant">
          <div class="msg-avatar">🤖</div>
          <div class="msg-bubble typing">
            <span class="dot"></span><span class="dot"></span><span class="dot"></span>
          </div>
        </div>
      </div>

      <div class="chat-input">
        <textarea
          v-model="input"
          placeholder="输入你的问题，例如：广州天河区有什么好房子？"
          :disabled="loading"
          @keydown="handleKeydown"
          rows="1"
        ></textarea>
        <button class="send-btn" :disabled="!input.trim() || loading" @click="handleSend">
          <span v-if="!loading">发送</span>
          <span v-else>...</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.assistant-layout {
  max-width: 800px; margin: 24px auto; padding: 0 16px;
  height: calc(100vh - 108px); display: flex; flex-direction: column;
}
.chat-panel {
  flex: 1; display: flex; flex-direction: column;
  background: #fff; border-radius: 16px; box-shadow: 0 2px 16px rgba(0,0,0,0.06); overflow: hidden;
}

/* ── 顶部 ── */
.chat-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 24px; border-bottom: 1px solid #f0f2f5; background: #fafbfc;
}
.header-left { display: flex; align-items: center; gap: 12px; }
.ai-icon { font-size: 32px; }
.chat-header h2 { margin: 0; font-size: 18px; font-weight: 700; color: #303133; }
.subtitle { margin: 2px 0 0; font-size: 12px; color: #909399; }
.clear-btn {
  background: none; border: 1px solid #dcdfe6; border-radius: 8px;
  padding: 6px 16px; font-size: 13px; color: #606266; cursor: pointer; transition: all 0.2s;
}
.clear-btn:hover { border-color: #409eff; color: #409eff; }

/* ── 消息区 ── */
.chat-messages {
  flex: 1; overflow-y: auto; padding: 20px 24px;
  display: flex; flex-direction: column; gap: 16px; background: #fafbfc;
}

/* 欢迎页 */
.welcome { text-align: center; padding: 40px 20px; }
.welcome-icon { font-size: 56px; margin-bottom: 12px; }
.welcome h3 { margin: 0 0 8px; font-size: 20px; color: #303133; }
.welcome p { color: #909399; font-size: 14px; margin: 0 0 24px; }
.quick-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; max-width: 460px; margin: 0 auto; }
.quick-chip {
  padding: 12px 14px; background: #fff; border: 1px solid #e8eaee;
  border-radius: 10px; font-size: 13px; color: #409eff; cursor: pointer;
  text-align: left; transition: all 0.2s;
}
.quick-chip:hover { border-color: #409eff; background: #ecf5ff; }

/* 消息行 */
.msg-row { display: flex; gap: 10px; align-items: flex-start; }
.msg-row.user { flex-direction: row-reverse; padding-left: 40px; }
.msg-row.assistant { padding-right: 40px; }
.msg-avatar { font-size: 28px; flex-shrink: 0; width: 36px; text-align: center; }
.msg-bubble {
  max-width: 100%; padding: 12px 16px; border-radius: 14px;
  font-size: 14px; line-height: 1.7; word-break: break-word; position: relative;
}
.msg-row.user .msg-bubble { background: #409eff; color: #fff; border-bottom-right-radius: 4px; }
.msg-row.assistant .msg-bubble { background: #fff; color: #303133; border: 1px solid #e8eaee; border-bottom-left-radius: 4px; }
.msg-bubble.error { border-color: #fde2e2; background: #fef0f0; color: #f56c6c; }
.msg-row.assistant .msg-text :deep(strong) { color: #303133; }
.msg-row.user .msg-text :deep(strong) { color: #fff; }

/* 流式光标 */
.cursor-blink {
  display: inline; color: #409eff; font-weight: 400;
  animation: blink 1s step-end infinite;
}
@keyframes blink {
  50% { opacity: 0; }
}

/* 打字动画 */
.typing { display: flex; gap: 5px; align-items: center; padding: 16px 20px; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: #c0c4cc; animation: bounce 1.4s infinite ease-in-out both; }
.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* ── 输入区 ── */
.chat-input {
  display: flex; align-items: flex-end; gap: 10px;
  padding: 14px 24px; border-top: 1px solid #f0f2f5; background: #fff;
}
.chat-input textarea {
  flex: 1; border: 1px solid #e8eaee; border-radius: 10px;
  padding: 10px 14px; font-size: 14px; resize: none; outline: none;
  font-family: inherit; line-height: 1.5; max-height: 120px; min-height: 44px;
  transition: border-color 0.2s;
}
.chat-input textarea:focus { border-color: #409eff; }
.send-btn {
  padding: 10px 24px; border: none; border-radius: 10px;
  font-size: 14px; font-weight: 600; cursor: pointer;
  background: linear-gradient(135deg, #409eff, #6366f1);
  color: #fff; white-space: nowrap; transition: opacity 0.2s, transform 0.1s;
}
.send-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.send-btn:not(:disabled):active { transform: scale(0.96); }
.send-btn:not(:disabled):hover { opacity: 0.9; }
</style>
