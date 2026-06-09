<template>
  <section class="booking-layout">
    <form class="booking-form" @submit.prevent="submit">
      <div>
        <p class="eyebrow">Registration</p>
        <h3>新增报名</h3>
      </div>
      <label>
        选择线路
        <select v-model.number="form.route" required>
          <option disabled value="">请选择</option>
          <option v-for="route in routes" :key="route.id" :value="route.id">{{ route.title }}</option>
        </select>
      </label>
      <label>
        联系人
        <input v-model="form.contact_name" required />
      </label>
      <label>
        手机号
        <input v-model="form.phone" required />
      </label>
      <div class="form-row">
        <label>
          人数
          <input v-model.number="form.party_size" min="1" type="number" required />
        </label>
        <label>
          出行日期
          <input v-model="form.travel_date" type="date" required />
        </label>
      </div>
      <label>
        备注
        <textarea v-model="form.remark" rows="3"></textarea>
      </label>
      <button class="primary-action" type="submit">提交报名</button>
    </form>

    <section class="table-panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">Group Status</p>
          <h3>报名与成团状态</h3>
        </div>
        <span>{{ bookings.length }} 条报名</span>
      </div>
      <div class="booking-list">
        <article v-for="booking in bookings" :key="booking.id">
          <div>
            <h4>{{ booking.contact_name }} · {{ booking.party_size }} 人</h4>
            <p>{{ booking.route_title }} / {{ booking.travel_date }}</p>
          </div>
          <span class="tag">{{ booking.status_label }}</span>
          <strong>{{ booking.group_enrolled }}/{{ booking.min_group_size }}</strong>
        </article>
      </div>
    </section>
  </section>
</template>

<script setup>
import { reactive } from "vue";

defineProps({
  routes: { type: Array, required: true },
  bookings: { type: Array, required: true },
});

const emit = defineEmits(["booking-created"]);

const form = reactive({
  route: "",
  contact_name: "",
  phone: "",
  party_size: 1,
  travel_date: "",
  status: "pending",
  remark: "",
});

function submit() {
  emit("booking-created", { ...form });
  form.contact_name = "";
  form.phone = "";
  form.party_size = 1;
  form.travel_date = "";
  form.remark = "";
}
</script>
