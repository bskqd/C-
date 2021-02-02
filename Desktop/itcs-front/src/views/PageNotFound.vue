<template>
  <div class="d-flex mt-5 pt-5 justify-content-center">
    <div class="card p-5">
      <div class="notFound">
        404
      </div>
      <div class="text-center">
        {{ $t('pageNotFound') }}
      </div>
      <router-link to="/" className="text-center mt-2 main-color-blue">
        {{ $t('toMainPage') }}
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PageNotFound'
}
</script>

<style scoped>
  .notFound {
    font-size: 20rem;
  }
</style>
