<template>
  <div class="language-switcher">
    <button
      @click="toggleLanguage"
      class="lang-button"
      :title="$t('common.language')"
    >
      <span class="lang-text">{{ currentLang }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()

const currentLang = computed(() => locale.value === 'zh' ? '中文' : 'English')

const toggleLanguage = () => {
  const newLocale = locale.value === 'zh' ? 'en' : 'zh'
  locale.value = newLocale
  localStorage.setItem('language', newLocale)
}
</script>

<style scoped>
.language-switcher {
  padding: 10px 20px;
  display: flex;
  justify-content: center;
}

.lang-button {
  padding: 8px 16px;
  background: rgba(0, 242, 254, 0.1);
  color: #00f2fe;
  border: 1px solid rgba(0, 242, 254, 0.4);
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 1px;
  transition: all 0.3s ease;
  box-shadow: 0 0 10px rgba(0, 242, 254, 0.2);
}

.lang-button:hover {
  background: rgba(0, 242, 254, 0.2);
  box-shadow: 0 0 15px rgba(0, 242, 254, 0.4);
  transform: translateY(-2px);
}

.lang-button:active {
  transform: translateY(0);
}

.lang-text {
  display: inline-block;
}
</style>
