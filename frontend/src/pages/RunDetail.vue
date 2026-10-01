<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
import BoxUnfold from '../components/BoxUnfold.vue'

const props = defineProps({ id: String })
const run = ref(null)
const err = ref('')

onMounted(async () => {
  try {
    run.value = await getJSON(`/api/runs/${props.id}`)
  } catch (e) {
    err.value = String(e.message || e)
  }
})
</script>

<template>
  <div class="page">
    <p v-if="err" class="bad">{{ err }}</p>
    <template v-else-if="run">
      <h1>用纸档 #{{ run.id }}</h1>
      <p class="lede">
        {{ run.box_name }} · 折边系数 {{ run.overlap }}
        <span class="pill">写入时快照：折入深度、有效表面积与用纸量一并固化</span>
      </p>
      <div class="result-board">
        <div class="figure">{{ run.result.paper_m2 }}<span>m²</span></div>
        <p class="stat-line">
          有效表面积 <strong>{{ run.result.box_surface }}</strong> m²
          ＝ 六面 {{ run.result.base_surface ?? '—' }}
          <template v-if="run.result.flap_m > 0"> ＋ 折入贴面 {{ run.result.flap_surface }}</template>
          × 折边系数 {{ run.overlap }}
        </p>
        <p class="stat-line">
          盖口折入深度 <strong>{{ run.result.flap_m ?? 0 }}</strong> m
        </p>
        <p class="stat-line" v-if="run.result.ribbon">
          丝带约 {{ run.result.ribbon.ribbon_m ?? '—' }} m（按未折入前长宽高）
        </p>
        <p class="stat-line snap-note">
          以上均取自本次写入时固化的 result_json，不随后续盒主数据默认折入变化而回刷。
        </p>
      </div>
      <BoxUnfold
        :l="run.box_length ?? run.result.box_length"
        :w="run.box_width ?? run.result.box_width"
        :h="run.box_height ?? run.result.box_height"
        :flap-m="run.result.flap_m ?? 0"
        :paper-m2="run.result.paper_m2"
      />
      <div class="row" style="margin-top: 1.25rem">
        <router-link class="btn" to="/history">返回用纸档</router-link>
      </div>
    </template>
  </div>
</template>

<style scoped>
.snap-note {
  font-size: 0.85rem;
  color: var(--foil);
}
</style>
