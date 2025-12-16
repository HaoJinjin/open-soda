<template>
  <div class="main-layout">
    <Aside  />
    <router-view></router-view>
  </div>
</template>
<script setup lang="ts">
import { ref } from "vue";
import Aside from "@/components/layout/aside-layout.vue";
import { useRouter } from "vue-router";
const router = useRouter();
const pageChange = (page) => {
  console.log(page);
  router.push({ name: 'showBoard'});
};
</script>
<style scoped>
.main-layout {
  display: flex;
  flex-direction: row;
  width: 100%;
}
</style>