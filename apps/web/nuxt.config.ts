export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },

  modules: [
    '@nuxt/ui',
    '@nuxtjs/i18n',
    '@pinia/nuxt',
    '@nuxt/eslint',
  ],

  css: ['~/assets/css/main.css'],

  ui: {
    // @ts-expect-error Nuxt UI types are not updated yet
    prose: true
  },

  i18n: {
    defaultLocale: 'uk',
    locales: [
      { code: 'uk', name: 'Українська' },
      { code: 'en', name: 'English' },
    ],
    strategy: 'prefix_except_default',
    detectBrowserLanguage: false,
  },

  runtimeConfig: {
    public: {
      apiBaseUrl: '',
      cloudinaryCloudName: '',
    },
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
