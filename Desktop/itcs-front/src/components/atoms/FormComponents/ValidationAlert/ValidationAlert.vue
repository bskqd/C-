<template>
  <div class="text-invalid">
    <div class="text-invalid--text">
      <span>{{ text }}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ValidationAlert',
  props: {
    text: String
  }
}
</script>

<style scoped></style>
