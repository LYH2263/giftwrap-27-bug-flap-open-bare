<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'

const items = ref([])
const err = ref('')

onMounted(async () => {
  try {
    items.value = (await getJSON('/api/runs')).items
  } catch (e) {
    err.value = String(e.message || e)
  }
})
</script>

<template>
  <div class="page">
    <h1>用纸档</h1>
    <p class="hint">列表与详情均钉写入时固化值（flap_m / 有效面 / paper_m2），不随盒主数据默认折入回刷。</p>
    <p class="lede">算纸页「写入用纸档」后的落库结果，按次保留盒名、折入深度与面积；点开编号看快照详情。</p>
    <p v-if="err" class="bad">{{ err }}</p>
    <p v-else-if="!items.length" class="empty">还没有写入过。先去算纸试一单。</p>
    <ul v-else class="item-list">
      <li v-for="r in items" :key="r.id">
        <router-link :to="`/history/${r.id}`">#{{ r.id }} {{ r.box_name }}</router-link>
        <span class="meta">
          折入 {{ r.result?.flap_m ?? 0 }} m ·
          {{ r.result?.paper_m2 ?? '—' }} m²
        </span>
      </li>
    </ul>
  </div>
</template>
