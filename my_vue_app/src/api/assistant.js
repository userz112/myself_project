import { post } from './index'

export const sendMessage = (message, threadId) =>
  post('/assistant/chat/', { message, thread_id: threadId })

// 流式请求 — 返回 ReadableStream，逐 token 读取
export const sendMessageStream = async (message, threadId, onToken, onDone, onError) => {
  const token = localStorage.getItem('token')
  try {
    const response = await fetch('/api/assistant/chat/stream/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ message, thread_id: threadId }),
    })

    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      throw new Error(err.error || `HTTP ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (!line.startsWith('data: ') || line === 'data: [DONE]') continue
        try {
          const data = JSON.parse(line.slice(6))
          if (data.token) onToken(data.token)
        } catch {}
      }
    }
    onDone()
  } catch (e) {
    onError(e.message || '网络错误')
  }
}
