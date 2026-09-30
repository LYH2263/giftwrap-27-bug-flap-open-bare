<script setup>
import { computed } from 'vue'

const props = defineProps({
  l: { type: Number, default: 0 },
  w: { type: Number, default: 0 },
  h: { type: Number, default: 0 },
  flapM: { type: Number, default: 0 },
  paperM2: { type: Number, default: null },
})

// 盖口四周折入贴面：口径自洽 2(L+W) × 折入深度
const flapSurface = computed(() => 2 * (Number(props.l) + Number(props.w)) * Number(props.flapM || 0))
// 折入条带厚度（示意比例，夹在 3~14px）
const t = computed(() => Math.min(14, Math.max(3, Number(props.flapM || 0) * 220)))
const showFlap = computed(() => Number(props.flapM || 0) > 0)
</script>

<template>
  <div class="unfold">
    <p class="unfold-title">盒体展开示意{{ showFlap ? '（含盖口折入贴面）' : '' }}</p>
    <svg class="unfold-svg" viewBox="0 0 280 180" aria-hidden="true">
      <rect class="panel" x="95" y="18" width="90" height="42" rx="2" />
      <rect class="panel top" x="95" y="68" width="90" height="52" rx="2" />
      <rect class="panel" x="20" y="68" width="68" height="52" rx="2" />
      <rect class="panel" x="192" y="68" width="68" height="52" rx="2" />
      <rect class="panel" x="95" y="128" width="90" height="38" rx="2" />
      <!-- 盖口折入：沿口径四周向内贴合的四条纸带 -->
      <template v-if="showFlap">
        <rect class="flap-strip" :x="95" :y="18" width="90" :height="t" />
        <rect class="flap-strip" :x="95" :y="60 - t" width="90" :height="t" />
        <rect class="flap-strip" :x="95" :y="18 + t" :width="t" :height="42 - 2 * t" />
        <rect class="flap-strip" :x="185 - t" :y="18 + t" :width="t" :height="42 - 2 * t" />
      </template>
      <text x="140" y="44" text-anchor="middle">顶 {{ Number(l).toFixed(2) }}×{{ Number(w).toFixed(2) }}</text>
      <text x="140" y="98" text-anchor="middle">正面</text>
      <text x="54" y="98" text-anchor="middle">侧</text>
      <text x="226" y="98" text-anchor="middle">侧</text>
      <text x="140" y="152" text-anchor="middle">h≈{{ Number(h).toFixed(2) }}</text>
    </svg>
    <p v-if="showFlap" class="stat-line flap-line">
      盖口折入 <strong>{{ Number(flapM).toFixed(3) }}</strong> m
      → 贴合面 +<strong>{{ flapSurface.toFixed(4) }}</strong> m²（口径 2×({{ Number(l).toFixed(2) }}+{{ Number(w).toFixed(2) }})）
    </p>
    <p v-if="paperM2 != null" class="stat-line">
      估算用纸 <strong>{{ Number(paperM2).toFixed(4) }}</strong> m²（含折边系数）
    </p>
    <p v-else class="stat-line">
      外形 {{ Number(l).toFixed(2) }} × {{ Number(w).toFixed(2) }} × {{ Number(h).toFixed(2) }} m
    </p>
  </div>
</template>

<style scoped>
.flap-strip {
  fill: rgba(214, 75, 106, 0.28);
  stroke: var(--ribbon);
  stroke-width: 1;
  stroke-dasharray: 3 2;
  animation: panelIn 0.5s ease both;
}
.flap-line strong {
  color: var(--ribbon);
}
</style>
