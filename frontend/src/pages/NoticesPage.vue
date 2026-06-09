<template>
  <section class="notice-board">
    <article v-for="notice in notices" :key="notice.id" class="notice-item">
      <div class="notice-type">{{ notice.notice_type_label }}</div>
      <div>
        <h3>{{ notice.title }}</h3>
        <p>{{ notice.content }}</p>
        <span>{{ notice.route_title }} · {{ formatDate(notice.publish_at) }}</span>
      </div>
      <strong :class="{ sent: notice.is_sent }">{{ notice.is_sent ? "已发送" : "待发送" }}</strong>
    </article>
  </section>
</template>

<script setup>
defineProps({
  notices: { type: Array, required: true },
});

function formatDate(value) {
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}
</script>
