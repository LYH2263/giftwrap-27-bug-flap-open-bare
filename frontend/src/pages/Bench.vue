<script setup>
import { onMounted, ref, watch } from 'vue'
import { getJSON, postJSON } from '../api'
import BoxUnfold from '../components/BoxUnfold.vue'

const boxes = ref([])
const bid = ref(1)
const flap = ref(0)
const out = ref(null)
const err = ref('')
const busy = ref(false)

function currentBox() {
  return boxes.value.find((b) => b.id === bid.value)
}

onMounted(async () => {
  try {
    boxes.value = (await getJSON('/api/boxes')).items.filter((b) => b.data_quality === 'clean')
    if (boxes.value.length) {
      bid.value = boxes.value[0].id
      flap.value = boxes.value[0].default_flap_m ?? 0
    }
  } catch (e) {
    err.value = String(e.message || e)
  }
})

// 换盒时折入默认跟随该盒主数据
watch(bid, (id) => {
  const b = boxes.value.find((x) => x.id === id)
  if (b) flap.value = b.default_flap_m ?? 0
})

async function go(save) {
  err.value = ''
  const f = Number(flap.value)
  if (!Number.isFinite(f) || f < 0) {
    err.value = '盖口折入深度须为不小于 0 的米数'
    return
  }
  busy.value = true
  try {
    out.value = save
      ? await postJSON('/api/estimate', { box_id: bid.value, flap_m: f, save: true })
      : await getJSON(`/api/estimate?box_id=${bid.value}&flap_m=${encodeURIComponent(f)}`)
  } catch (e) {
    out.value = null
    err.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="page">
    <h1>算纸</h1>
    <p class="lede">先试算看面积与展开，确认后再写入用纸档。盖口折入深度按米登记，0 表示不折入。</p>
    <div class="row">
      <select v-model.number="bid">
        <option v-for="b in boxes" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
      <label class="flap-field">
        盖口折入
        <input v-model.number="flap" type="number" min="0" step="0.005" />
        <span class="unit">m</span>
      </label>
      <button :disabled="busy" @click="go(false)">试算</button>
      <button class="ribbon" :disabled="busy" @click="go(true)">写入用纸档</button>
    </div>
    <p v-if="err" class="bad">{{ err }}</p>
    <div v-if="out" class="result-board">
      <div class="figure">{{ out.paper_m2 }}<span>m²</span></div>
      <p class="stat-line">
        有效表面积 <strong>{{ out.box_surface }}</strong> m²
        ＝ 六面 {{ out.base_surface }}
        <template v-if="out.flap_m > 0"> ＋ 折入贴面 {{ out.flap_surface }}</template>
        × 折边系数 {{ out.overlap }}
      </p>
      <p class="stat-line" v-if="out.flap_m > 0">盖口折入深度 {{ out.flap_m }} m（口径自洽 2×(长+宽)）</p>
      <p class="stat-line" v-if="out.ribbon">
        十字丝带约 {{ out.ribbon.ribbon_m ?? out.ribbon }} m（按未折入前长宽高）
      </p>
      <p v-if="out.run_id" class="stat-line ok-line">已写入用纸档，编号 #{{ out.run_id }}，落库快照可回看互证。</p>
      <BoxUnfold
        :l="out.box.length"
        :w="out.box.width"
        :h="out.box.height"
        :flap-m="out.flap_m"
        :paper-m2="out.paper_m2"
      />
    </div>
  </div>
</template>

<style scoped>
.flap-field {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.95rem;
  color: var(--ink-soft);
}
.flap-field input {
  width: 110px;
  padding: 0.5rem 0.6rem;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: rgba(255, 255, 255, 0.72);
  font: inherit;
  color: var(--ink);
}
.flap-field .unit {
  color: var(--ink-soft);
}
.ok-line {
  color: var(--ok);
  font-weight: 600;
}
</style>
