<script setup>
import AppHeader from '@/components/AppHeader.vue'
</script>

<template>
  <AppHeader />
  <router-view />
</template>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif; background: #f5f6fa; color: #2c3e50; line-height: 1.6; }
a { color: #409eff; text-decoration: none; }
a:hover { color: #66b1ff; }
</style>
