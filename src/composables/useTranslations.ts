import { useI18n } from 'vue-i18n'
import { translationKeys } from '@/i18n/translations'

/**
 * 便利的翻译 composable，提供类型安全的翻译访问
 * 用法示例：
 * const { t, page } = useTranslations()
 * page.overview.title  // 返回 i18n 键值
 * t(page.overview.title)  // 返回翻译后的文本
 */
export function useTranslations() {
  const { t } = useI18n()

  return {
    t,
    keys: translationKeys,
    page: translationKeys.pages,
    menu: translationKeys.menu,
    common: translationKeys.common,
    layout: translationKeys.layout,
  }
}
