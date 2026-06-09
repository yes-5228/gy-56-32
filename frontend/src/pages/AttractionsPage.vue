<template>
  <section class="table-panel">
    <div class="panel-head">
      <div>
        <p class="eyebrow">Attraction Library</p>
        <h3>景点路线设计素材</h3>
      </div>
      <span>{{ attractions.length }} 个景点</span>
    </div>
    <div class="attraction-list">
      <article v-for="item in attractions" :key="item.id">
        <div>
          <h4>{{ item.name }}</h4>
          <p>{{ item.highlight }}</p>
        </div>
        <span>{{ item.city }}</span>
        <span>{{ item.category_label }}</span>
        <strong>{{ item.duration_hours }}h · ¥{{ item.ticket_price }}</strong>
      </article>
    </div>
  </section>
</template>

<script setup>
defineProps({
  attractions: { type: Array, required: true },
});
</script>
