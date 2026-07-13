<template>
  <div class="bg-white rounded-xl shadow-sm p-6">
    <h2 class="text-xl font-bold text-gray-800 mb-4">购物车</h2>
    <div v-if="cart.length === 0" class="text-center py-20 text-gray-500">购物车是空的</div>
    <div v-else>
      <div v-for="(item, idx) in cart" :key="idx" class="flex items-center justify-between border-b py-4">
        <div class="flex items-center space-x-4">
          <div class="w-16 h-16 bg-gray-200 rounded-lg flex items-center justify-center overflow-hidden">
            <img v-if="item.image_url" :src="item.image_url" class="w-full h-full object-cover" />
          </div>
          <div>
            <h3 class="font-medium text-gray-800">{{ item.name }}</h3>
            <p class="text-sm text-gray-500">规格：{{ item.spec || '默认' }}</p>
            <p class="text-red-500 font-semibold">¥{{ item.price }}</p>
          </div>
        </div>
        <div class="flex items-center space-x-4">
          <div class="flex items-center border rounded-lg">
            <button @click="changeQty(idx, -1)" class="px-3 py-1">-</button>
            <span class="px-3">{{ item.quantity }}</span>
            <button @click="changeQty(idx, 1)" class="px-3 py-1">+</button>
          </div>
          <button @click="remove(idx)" class="text-red-500 hover:text-red-700 text-sm">删除</button>
        </div>
      </div>
      <div class="mt-6 flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-600">收货地址</p>
          <input v-model="address" type="text" class="border border-gray-300 rounded-lg px-3 py-2 mt-1 w-80" placeholder="请输入收货地址" />
        </div>
        <div class="text-right">
          <p class="text-xl font-bold text-red-500">合计：¥{{ total }}</p>
          <button @click="checkout" :disabled="submitting" class="mt-2 bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-60">去结算</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api/axios'

const router = useRouter()
const cart = ref([])
const address = ref('')
const submitting = ref(false)

const total = computed(() => cart.value.reduce((sum, i) => sum + i.price * i.quantity, 0).toFixed(2))

function loadCart() {
  cart.value = JSON.parse(localStorage.getItem('cart') || '[]')
}

function changeQty(idx, delta) {
  cart.value[idx].quantity += delta
  if (cart.value[idx].quantity <= 0) cart.value.splice(idx, 1)
  saveCart()
}

function remove(idx) {
  cart.value.splice(idx, 1)
  saveCart()
}

function saveCart() {
  localStorage.setItem('cart', JSON.stringify(cart.value))
}

async function checkout() {
  if (cart.value.length === 0) return
  submitting.value = true
  try {
    const items = cart.value.map(i => ({ product_id: i.product_id, quantity: i.quantity, spec: i.spec }))
    await api.post('/orders/checkout', { items, address: address.value })
    localStorage.removeItem('cart')
    alert('下单成功')
    router.push('/orders')
  } catch (e) {
    alert(e.response?.data?.detail || '下单失败')
  } finally {
    submitting.value = false
  }
}

onMounted(loadCart)
</script>
