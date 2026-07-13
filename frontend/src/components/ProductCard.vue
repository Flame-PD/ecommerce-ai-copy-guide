<template>
  <div class="bg-white rounded-xl shadow-sm hover:shadow-md transition overflow-hidden cursor-pointer" @click="$emit('click')">
    <div class="h-40 bg-gray-200 flex items-center justify-center overflow-hidden">
      <img v-if="product.image_url" :src="product.image_url" class="w-full h-full object-cover" />
      <span v-else class="text-gray-400">暂无图片</span>
    </div>
    <div class="p-4">
      <h3 class="font-semibold text-gray-800 truncate">{{ product.ai_title || product.name }}</h3>
      <p class="text-xs text-gray-500 mt-1 line-clamp-2">{{ product.ai_slogan || product.description }}</p>
      <div class="mt-3 flex items-center justify-between">
        <span class="text-red-500 font-bold">¥{{ product.price }}</span>
        <span class="text-xs text-gray-400">{{ product.category }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({ product: Object })
defineEmits(['click'])
</script>
