export default defineNuxtPlugin(async () => {
  const { initialize } = useAuth()
  await initialize()
})
