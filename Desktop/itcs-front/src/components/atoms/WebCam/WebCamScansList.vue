<template>
  <div>
    <span :key="scan.name" v-for="scan in scans" class="mr-1">
      {{ scan.name }};
    </span>
  </div>
</template>

<script>
export default {
  name: 'ScansList',
  props: {
    scans: Array
  }
}
</script>

<style scoped>

</style>
