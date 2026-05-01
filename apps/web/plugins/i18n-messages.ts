import en from '~/locales/en.json'
import uk from '~/locales/uk.json'

export default defineNuxtPlugin((nuxtApp) => {
  const i18n = nuxtApp.$i18n as { setLocaleMessage: (locale: string, messages: object) => void }
  i18n.setLocaleMessage('uk', uk)
  i18n.setLocaleMessage('en', en)
})
