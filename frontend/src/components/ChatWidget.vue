<template>
  <div class="fixed bottom-6 right-6 z-50">
    <div v-if="open" class="bg-white w-80 sm:w-96 h-[500px] rounded-2xl shadow-2xl flex flex-col border border-gray-200 mb-4">
      <div class="bg-indigo-600 text-white px-4 py-3 rounded-t-2xl flex justify-between items-center">
        <span class="font-medium">AI智能导购</span>
        <button @click="open = false" class="text-white hover:text-gray-200">×</button>
      </div>
      <div ref="box" class="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
        <div v-for="(msg, idx) in messages" :key="idx" :class="msg.role === 'user' ? 'text-right' : 'text-left'">
          <div :class="msg.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-800 border'" class="inline-block px-4 py-2 rounded-xl text-sm max-w-[85%] whitespace-pre-wrap">
            {{ msg.content }}
          </div>
        </div>
        <div v-if="loading" class="text-left">
          <div class="bg-white text-gray-500 border inline-block px-4 py-2 rounded-xl text-sm">思考中...</div>
        </div>
      </div>
      <div class="p-3 border-t bg-white rounded-b-2xl">
        <div class="flex space-x-2">
          <input v-model="input" @keydown.enter="send" type="text" placeholder="咨询尺码、材质、售后等" class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          <button @click="send" :disabled="loading || !input.trim()" class="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-60">发送</button>
        </div>
      </div>
    </div>
    <button @click="open = !open" class="bg-indigo-600 hover:bg-indigo-700 text-white rounded-full w-14 h-14 shadow-lg flex items-center justify-center text-2xl">
      {{ open ? '×' : 'AI' }}
    </button>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'

const open = ref(false)
const input = ref('')
const loading = ref(false)
const messages = ref([{ role: 'assistant', content: '您好！我是AI智能导购，请问有什么可以帮您？' }])
const box = ref(null)
const route = useRoute()

const productId = ref(null)

onMounted(() => {
  if (route.params.id) {
    productId.value = parseInt(route.params.id)
  }
})

watch(() => route.params.id, (val) => {
  productId.value = val ? parseInt(val) : null
})

watch(messages, () => {
  nextTick(() => {
    if (box.value) box.value.scrollTop = box.value.scrollHeight
  })
}, { deep: true })

async function send() {
  const text = input.value.trim()
  if (!text || loading.value) return
  messages.value.push({ role: 'user', content: text })
  input.value = ''
  loading.value = true
  try {
    const payload = { message: text }
    if (productId.value) payload.product_id = productId.value
    const res = await api.post('/chat/ask', payload)
    messages.value.push({ role: 'assistant', content: res.data.answer })
  } catch (e) {
    messages.value.push({ role: 'assistant', content: '抱歉，服务暂时不可用，请稍后再试。' })
  } finally {
    loading.value = false
  }
}
</script>
