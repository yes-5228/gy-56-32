<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div>
        <p class="eyebrow">TravelOps</p>
        <h1>旅游线路规划系统</h1>
      </div>
      <nav>
        <button
          v-for="item in navItems"
          :key="item.key"
          :class="{ active: activePage === item.key }"
          type="button"
          @click="activePage = item.key"
        >
          <span>{{ item.icon }}</span>
          {{ item.label }}
        </button>
      </nav>
    </aside>

    <main>
      <header class="topbar">
        <div>
          <p class="eyebrow">线路运营工作台</p>
          <h2>{{ pageTitle }}</h2>
        </div>
        <button type="button" class="primary-action" @click="loadData">刷新数据</button>
      </header>

      <div v-if="loading" class="state">数据加载中...</div>
      <div v-else-if="error" class="state error">{{ error }}</div>
      <component
        v-else
        :is="activeComponent"
        :attractions="attractions"
        :routes="routes"
        :bookings="bookings"
        :notices="notices"
        @booking-created="handleBookingCreated"
      />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { travelApi } from "./api/travel";
import AttractionsPage from "./pages/AttractionsPage.vue";
import RoutesPage from "./pages/RoutesPage.vue";
import BookingsPage from "./pages/BookingsPage.vue";
import NoticesPage from "./pages/NoticesPage.vue";

const navItems = [
  { key: "routes", label: "线路设计", icon: "路" },
  { key: "attractions", label: "景点库", icon: "景" },
  { key: "bookings", label: "报名成团", icon: "团" },
  { key: "notices", label: "出行通知", icon: "知" },
];

const pageMap = {
  routes: RoutesPage,
  attractions: AttractionsPage,
  bookings: BookingsPage,
  notices: NoticesPage,
};

const activePage = ref("routes");
const loading = ref(true);
const error = ref("");
const attractions = ref([]);
const routes = ref([]);
const bookings = ref([]);
const notices = ref([]);

const activeComponent = computed(() => pageMap[activePage.value]);
const pageTitle = computed(() => navItems.find((item) => item.key === activePage.value)?.label);

async function loadData() {
  loading.value = true;
  error.value = "";
  try {
    const [attractionData, routeData, bookingData, noticeData] = await Promise.all([
      travelApi.getAttractions(),
      travelApi.getRoutes(),
      travelApi.getBookings(),
      travelApi.getNotices(),
    ]);
    attractions.value = attractionData;
    routes.value = routeData;
    bookings.value = bookingData;
    notices.value = noticeData;
  } catch (err) {
    error.value = `加载失败：${err.message}`;
  } finally {
    loading.value = false;
  }
}

async function handleBookingCreated(payload) {
  await travelApi.createBooking(payload);
  await loadData();
}

onMounted(loadData);
</script>
