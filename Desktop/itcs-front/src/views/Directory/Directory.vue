<template>
  <div class="seafarerTabs">
    <h4 class="text-left">{{ $t('directory') }}</h4>
    <b-tabs fill pills>
      <TabsList
        v-if="checkAccess('admin')"
        link="directory-address"
        :countDocKey="null"
        icon=""
        labelKey="address"
        :tabs="[]"/>
    </b-tabs>

    <b-card v-if="checkAccess('admin')" no-body>
      <router-view></router-view>
    </b-card>
  </div>
</template>

<script>
import TabsList from '@/components/atoms/TabsList.vue'
import { checkAccess } from '@/mixins/permissions'

export default {
  name: 'directory',
  components: {
    TabsList
  },
  data () {
    return {
      checkAccess
    }
  },
  beforeCreate () {
    this.$store.commit('setActivePage', { name: 'directory', access: checkAccess('admin') })
  }
}
</script>

<style lang="sass">
  @import '../../assets/sass/seafarer/main'
</style>
