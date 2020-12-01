<template>
  <article class="markdown-body"><myMarkdown />
  </article></template>

<script>
import { mapGetters } from 'vuex'
import myMarkdown from '@/assets/README.md'
export default {
  name: 'Help',
  components: {
    myMarkdown
  },
  computed: {
    ...mapGetters([
      'name',
      'roles'
    ])
  }
}
</script>

<style lang="scss" scoped>
  .markdown-body {
    box-sizing: border-box;
    min-width: 200px;
    max-width: 980px;
    margin: 0 auto;
    padding: 45px;
  }
</style>
