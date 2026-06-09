<template>
  <article class="route-card">
    <div class="route-head">
      <div>
        <p class="eyebrow">{{ route.city }} · {{ route.days }} 天</p>
        <h3>{{ route.title }}</h3>
      </div>
      <span class="tag">{{ route.status_label }}</span>
    </div>
    <p class="description">{{ route.description }}</p>
    <div class="budget-grid">
      <span>基础费用 <b>¥{{ route.base_cost }}</b></span>
      <span>门票合计 <b>¥{{ route.ticket_total }}</b></span>
      <span>预计总价 <b>¥{{ route.estimated_cost }}</b></span>
    </div>
    <div class="progress-row">
      <span>已报名 {{ route.enrolled_count }}/{{ route.min_group_size }}</span>
      <div class="progress-track">
        <i :style="{ width: `${route.group_progress}%` }"></i>
      </div>
    </div>
    <ol class="stop-list">
      <li v-for="stop in route.stops" :key="stop.id">
        <span>D{{ stop.day }}-{{ stop.order }}</span>
        <div>
          <b>{{ stop.attraction.name }}</b>
          <p>{{ stop.note }}</p>
        </div>
      </li>
    </ol>
  </article>
</template>

<script setup>
defineProps({
  route: { type: Object, required: true },
});
</script>
