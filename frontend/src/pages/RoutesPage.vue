<template>
  <section class="page-stack">
    <div class="metrics-row">
      <MetricCard label="线路数量" :value="routes.length" hint="覆盖多目的地线路" />
      <MetricCard label="成团中" :value="formingCount" hint="持续收客线路" />
      <MetricCard label="平均预算" :value="averageBudget" hint="按线路预计总价" />
    </div>
    <div class="route-grid">
      <RouteCard v-for="route in routes" :key="route.id" :route="route" />
    </div>
  </section>
</template>

<script setup>
import { computed } from "vue";
import MetricCard from "../components/MetricCard.vue";
import RouteCard from "../components/RouteCard.vue";

const props = defineProps({
  routes: { type: Array, required: true },
});

const formingCount = computed(() => props.routes.filter((route) => route.status === "forming").length);
const averageBudget = computed(() => {
  if (!props.routes.length) return "¥0";
  const total = props.routes.reduce((sum, route) => sum + Number(route.estimated_cost), 0);
  return `¥${Math.round(total / props.routes.length)}`;
});
</script>
