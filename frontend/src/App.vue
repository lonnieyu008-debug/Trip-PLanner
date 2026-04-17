<template>
  <div id="app">
    <a-layout style="min-height: 100vh">
      <a-layout-header style="background: #3d1f0a; padding: 0 50px; display: flex; align-items: center; justify-content: space-between;">
        <div style="color: #f5e6d3; font-size: 22px; font-weight: 700; letter-spacing: 1px;">
          🧭 旅行规划助手
        </div>
        <div style="color: #c49a6c; font-size: 13px;">
          AI 驱动 · 智能规划
        </div>
      </a-layout-header>
      <a-layout-content style="padding: 0">
        <router-view />
      </a-layout-content>
      <a-layout-footer style="text-align: center; background: #3d1f0a; color: #a0784a; font-size: 13px; padding: 16px 50px;">
        旅行规划助手 ©2026 &nbsp;·&nbsp; 由 Cityu-AIX 小组设计
      </a-layout-footer>
    </a-layout>
  </div>
</template>

<script setup lang="ts">
</script>

<style>
#app {
  font-family: 'PingFang SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    'Noto Sans', sans-serif;
}

/* 全局主色调覆盖 Ant Design 默认蓝色 */
:root {
  --primary: #e8651a;
  --primary-light: #f5a05a;
  --primary-dark: #c04e0e;
  --warm-bg: #faf6f1;
  --warm-card: #ffffff;
  --warm-text: #3d1f0a;
  --warm-sub: #a0784a;
  --warm-border: #e8d5bc;
}
</style>
