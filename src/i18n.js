import { createI18n } from 'vue-i18n'
import zhMessages from './locales/zh.json'
import enMessages from './locales/en.json'

// 从 localStorage 获取保存的语言，默认为中文
const savedLanguage = localStorage.getItem('language') || 'zh'

const i18n = createI18n({
  legacy: false,
  locale: savedLanguage,
  fallbackLocale: 'zh',
  messages: {
    zh: zhMessages,
    en: enMessages
  }
})

export default i18n
