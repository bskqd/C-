<template>
  <div v-if="show" class="popapp">
    <p class="text-white">{{ text }}</p>
    <p
      @click="show = !show"
      class="text-center m-0 mb-1"
    >
      <v-btn>Закрыть</v-btn>
    </p>
    <p
      @click="hidePopover"
      class="text-center text-primary m-0"
    >
      {{ $t('dontShowAgain') }}
    </p>
  </div>
</template>

<script>
export default {
  name: 'Popover',
  props: {
    text: String
  },
  data () {
    return {
      show: true
    }
  },
  methods: {
    hidePopover () {
      const body = { is_trained: true }
      this.$api.patch('api/v1/auth/user_is_trained/', body).then(response => {
        if (response.code === 200) {
          this.$store.commit('setMainStateData', { type: 'isTrained', data: true })
        }
      })
    }
  }
}
</script>

<style scoped lang="sass">
  .popapp
    position: absolute
    top: 60px
    right: 20px
    width: 250px
    padding: 12px
    text-align: left
    border-radius: 5px
    background-color: #555
    z-index: 999
    &::after
      position: absolute
      top: -5px
      right: 35px
      content: ''
      width: 10px
      height: 10px
      background-color: #555
      transform: rotate(45deg)

</style>
