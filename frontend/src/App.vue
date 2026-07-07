<script setup lang="ts">
import { onMounted, ref } from 'vue'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const apiStatus = ref<'checking' | 'online' | 'offline'>('checking')
const generatedCopy = ref({
  title: '云感护腰办公椅｜为久坐办公人群打造的专业可信之选',
  ad_slogan: '把护腰支撑带回家，从今天开始升级体验。',
  selling_points: ['护腰支撑：让购买理由更清晰可感知', '透气坐垫：让购买理由更清晰可感知'],
})

const featureCards = [
  ['商品文案生成', '标题、卖点、详情页文案和广告语，支撑商品上架与营销素材。'],
  ['智能导购推荐', '根据用户预算、场景和偏好，生成可解释的推荐理由。'],
  ['评论情感分析', '提取好评词、差评痛点和可落地的商品优化建议。'],
  ['直播脚本生成', '按直播节奏输出开场、讲解、互动和转化话术。'],
]

const milestones = ['项目初始化', 'Mock API 骨架', '前端演示页', '数据库与 AI 接入', '展示材料沉淀']

async function refreshDemo() {
  try {
    const response = await fetch(`${apiBaseUrl}/api/copy/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        product_name: '云感护腰办公椅',
        audience: '久坐办公人群',
        tone: '专业可信',
        selling_points: ['护腰支撑', '透气坐垫', '稳固耐用'],
      }),
    })

    if (!response.ok) {
      throw new Error(`API returned ${response.status}`)
    }

    generatedCopy.value = await response.json()
    apiStatus.value = 'online'
  } catch {
    apiStatus.value = 'offline'
  }
}

onMounted(refreshDemo)
</script>

<template>
  <main class="shell">
    <section class="hero">
      <div class="hero__content">
        <p class="eyebrow">Course Project · AI Commerce Assistant</p>
        <h1>电商 AI 商品文案生成与智能导购助手</h1>
        <p class="lead">
          面向商品运营和课程展示的初始化版本：先用稳定的 Mock API
          跑通文案、导购、评论分析和直播脚本四条主线。
        </p>
        <div class="actions">
          <a class="button button--primary" href="#demo">查看演示</a>
          <a class="button button--ghost" href="#architecture">项目结构</a>
        </div>
      </div>
      <aside class="status-card" aria-label="Backend status">
        <span :class="['status-dot', `status-dot--${apiStatus}`]"></span>
        <p>Backend API</p>
        <strong>{{ apiStatus === 'online' ? '已连接' : apiStatus === 'checking' ? '检测中' : '静态演示' }}</strong>
        <small>{{ apiBaseUrl }}</small>
      </aside>
    </section>

    <section class="feature-grid" aria-label="Project features">
      <article v-for="[title, desc] in featureCards" :key="title" class="feature-card">
        <span>{{ title.slice(0, 2) }}</span>
        <h2>{{ title }}</h2>
        <p>{{ desc }}</p>
      </article>
    </section>

    <section id="demo" class="panel demo-panel">
      <div>
        <p class="eyebrow">Mock Generation</p>
        <h2>示例商品生成结果</h2>
        <p>当前前端会优先请求 Flask Mock API；后端未启动时保留静态结果，方便汇报展示不中断。</p>
      </div>
      <div class="copy-result">
        <p class="copy-result__label">推荐标题</p>
        <h3>{{ generatedCopy.title }}</h3>
        <ul>
          <li v-for="point in generatedCopy.selling_points" :key="point">{{ point }}</li>
        </ul>
        <blockquote>{{ generatedCopy.ad_slogan }}</blockquote>
        <button type="button" @click="refreshDemo">重新请求 API</button>
      </div>
    </section>

    <section id="architecture" class="panel split-panel">
      <div>
        <p class="eyebrow">Architecture</p>
        <h2>初始化边界</h2>
        <p>
          本阶段重点是让项目“成形”：文档、API 契约、前端展示和测试先闭环，真实模型、数据库和爬虫在下一阶段接入。
        </p>
      </div>
      <ol class="timeline">
        <li v-for="item in milestones" :key="item">{{ item }}</li>
      </ol>
    </section>
  </main>
</template>
