<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON, putJSON } from '../api'
import BoxUnfold from '../components/BoxUnfold.vue'

const props = defineProps({ id: String })
const box = ref(null)
const flap = ref(0)
const out = ref(null)
const err = ref('')
const savedMsg = ref('')
const busy = ref(false)

onMounted(async () => {
  try {
    box.value = await getJSON(`/api/boxes/${props.id}`)
    flap.value = box.value.default_flap_m ?? 0
  } catch (e) {
    err.value = String(e.message || e)
  }
})

function readFlap() {
  const f = Number(flap.value)
  if (!Number.isFinite(f) || f < 0) {
    err.value = '盖口折入深度须为不小于 0 的米数'
    return null
  }
  return f
}

async function saveDefault() {
  err.value = ''
  savedMsg.value = ''
  const f = readFlap()
  if (f === null) return
  try {
    box.value = await putJSON(`/api/boxes/${props.id}`, { default_flap_m: f })
    savedMsg.value = `默认折入深度 ${f} m 已写入盒主数据。`
  } catch (e) {
    err.value = String(e.message || e)
  }
}

async function go(save) {
  err.value = ''
  savedMsg.value = ''
  const f = readFlap()
  if (f === null) return
  busy.value = true
  try {
    out.value = await postJSON(`/api/estimate`, { box_id: Number(props.id), flap_m: f, save })
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
    <p v-if="err" class="bad">{{ err }}</p>
    <template v-else-if="box">
      <h1>{{ box.name }}</h1>
      <p class="lede">
        {{ box.length }} × {{ box.width }} × {{ box.height }} m
        <span class="pill" :class="{ warn: box.data_quality === 'dirty' }">
          {{ box.data_quality === 'dirty' ? '脏数据' : '可用' }}
        </span>
      </p>
      <p v-if="box.data_quality === 'dirty'" class="bad">{{ box.note }}</p>

      <div class="row">
        <label class="flap-field">
          盖口折入深度
          <input v-model.number="flap" type="number" min="0" step="0.005" :disabled="box.data_quality === 'dirty'" />
          <span class="unit">m</span>
        </label>
        <button class="ghost" :disabled="box.data_quality === 'dirty'" @click="saveDefault">存为默认折入</button>
        <button :disabled="busy || box.data_quality === 'dirty'" @click="go(false)">试算</button>
        <button class="ribbon" :disabled="busy || box.data_quality === 'dirty'" @click="go(true)">写入用纸档</button>
      </div>
      <p v-if="savedMsg" class="stat-line ok-line">{{ savedMsg }}</p>

      <div v-if="out" class="result-board">
        <div class="figure">{{ out.paper_m2 }}<span>m²</span></div>
        <p class="stat-line">
          有效表面积 <strong>{{ out.box_surface }}</strong> m²
          ＝ 六面 {{ out.base_surface }}
          <template v-if="out.flap_m > 0"> ＋ 折入贴面 {{ out.flap_surface }}</template>
          × 折边系数 {{ out.overlap }}
        </p>
        <p class="stat-line" v-if="out.ribbon">
          十字丝带约 {{ out.ribbon.ribbon_m ?? out.ribbon }} m（按未折入前长宽高）
        </p>
        <p v-if="out.run_id" class="stat-line ok-line">已写入用纸档，编号 #{{ out.run_id }}。</p>
      </div>

      <BoxUnfold
        :l="box.length"
        :w="box.width"
        :h="box.height"
        :flap-m="out ? out.flap_m : (box.default_flap_m ?? 0)"
        :paper-m2="out ? out.paper_m2 : null"
      />
      <div class="row" style="margin-top: 1.25rem">
        <router-link class="btn" to="/bench">去算纸台</router-link>
        <router-link class="btn ghost" to="/boxes">返回清单</router-link>
      </div>
    </template>
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
  width: 120px;
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
