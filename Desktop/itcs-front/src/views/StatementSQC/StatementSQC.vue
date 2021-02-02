<template>
  <div class="seafarerTabs">
    <h4 class="text-left">{{ $t('reportStatementSQC') }}</h4>
    <b-tabs fill pills>
      <TabsList
        v-if="checkAccess('tab-statementSQCApproved')"
        link="approved"
        icon=""
        :countDocKey="null"
        labelKey="approvedSQC"
        :tabs="[]"/>

      <TabsList
        v-if="checkAccess('tab-statementSQCProcess')"
        link="processing"
        icon=""
        :countDocKey="null"
        labelKey="pendingSQC"
        :tabs="[]"/>

      <TabsList
        v-if="checkAccess('tab-statementSQCFromPA')"
        link="fromPA"
        icon=""
        :countDocKey="null"
        labelKey="createdFormPA"
        :tabs="[]"/>
    </b-tabs>

    <b-card v-if="checkAccess('menuItem-statementSQC')" no-body>
      <router-view></router-view>
    </b-card>
  </div>
</template>

<script>
import TabsList from '@/components/atoms/TabsList.vue'
import { checkAccess } from '@/mixins/permissions'

export default {
  name: 'StatementSQC',
  components: {
    TabsList
  },
  data () {
    return {
      checkAccess
    }
  },
  beforeCreate () {
    this.$store.commit('setActivePage', { name: 'statementSQC', access: checkAccess('menuItem-statementSQC') })
  }
}
</script>

<style lang="sass">
  @import '../../assets/sass/seafarer/main'
</style>
