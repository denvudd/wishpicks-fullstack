export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },

  modules: [
    '@nuxt/ui',
    '@nuxtjs/i18n',
    '@nuxtjs/color-mode',
    '@pinia/nuxt',
    '@nuxt/eslint',
  ],

  css: ['~/assets/css/main.css'],
  
  ui: {
    prose: true
  },

  i18n: {
    defaultLocale: 'uk',
    langDir: 'locales',
    locales: [
      { code: 'uk', name: 'Українська', file: 'uk.json' },
      { code: 'en', name: 'English', file: 'en.json' },
    ],
    strategy: 'prefix_except_default',
    detectBrowserLanguage: false,
  },

  runtimeConfig: {
    apiBaseUrl: '', // NUXT_API_BASE_URL — internal Docker URL for SSR (e.g. http://api:8000)
    public: {
      apiBaseUrl: '', // NUXT_PUBLIC_API_BASE_URL — browser-facing URL
      cloudinaryCloudName: '',
    },
  },

  nitro: {
    preset: 'netlify',
  },

  vite: {
    server: {
      watch: {
        usePolling: true,
        interval: 300,
      },
      hmr: {
        host: 'localhost',
        protocol: 'ws',
      },
  },
  },
})
