<template>
  <div class="seafarerTabs">
    <h4 class="text-left">{{ $t('report') }}</h4>
    <b-tabs fill pills>
      <TabsList
        v-if="checkAccess('sqc-report')"
        link="sqc-report"
        icon=""
        :countDocKey="null"
        labelKey="sqc"
        :tabs="[]"/>

      <TabsList
        v-if="checkAccess('cadet-report')"
        link="cadet-report"
        icon=""
        :countDocKey="null"
        labelKey="student"
        :tabs="[]"/>

      <TabsList
        v-if="checkAccess('education-report')"
        link="education-report"
        icon=""
        :countDocKey="null"
        labelKey="education"
        :tabs="[]"/>

      <TabsList
        v-if="checkAccess('qualification-report')"
        link="qualification-report"
        icon=""
        :countDocKey="null"
        labelKey="qualificationDocsTab"
        :tabs="[]"/>

      <TabsList
        v-if="checkAccess('certificates-report')"
        link="certificates-report"
        icon=""
        :countDocKey="null"
        labelKey="eti"
        :tabs="[]"/>

      <TabsList
        v-if="checkAccess('sailorPassport-report')"
        link="sailorPassport-report"
        icon=""
        :countDocKey="null"
        labelKey="sailorPassportShort"
        :tabs="[]"/>

      <TabsList
        v-if="checkAccess('financial-report')"
        link="financial-report"
        icon=""
        :countDocKey="null"
        labelKey="financial"
        :tabs="[]"/>

      <TabsList
        v-if="checkAccess('excel-report')"
        link="excel-report"
        icon=""
        :countDocKey="null"
        labelKey="exсelReports"
        :tabs="[]"/>

      <TabsList
        v-if="checkAccess('admin')"
        link="debtor-report"
        icon=""
        :countDocKey="null"
        labelKey="debtor"
        :tabs="[]"/>

      <TabsList
        v-if="checkAccess('admin')"
        link="distribution-report-group"
        icon=""
        :countDocKey="null"
        labelKey="distribution"
        :tabs="[]"/>
    </b-tabs>

    <router-view/>
  </div>
</template>

<script>
import TabsList from '@/components/atoms/TabsList.vue'
import { checkAccess } from '@/mixins/permissions'

export default {
  name: 'Report',
  components: {
    TabsList
  },
  data () {
    return {
      checkAccess,
      routePath: this.$route.name
    }
  },
  beforeCreate () {
    this.$store.commit('setActivePage', { name: 'report', access: checkAccess(this.$route.name) })
  }
}
</script>

<style lang="sass">
  @import '../../assets/sass/seafarer/main'
</style>
