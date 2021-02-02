<template>
  <div class="seafarerTabs">
    <h4 class="text-left">{{ $t('backOffice') }}</h4>
    <b-tabs fill pills>
      <TabsList
        v-if="checkAccess('menuItem-etiRatio')"
        link="coefficients-backoffice"
        :countDocKey="null"
        icon=""
        labelKey="ntzCoefficient"
        :tabs="[]"/>

      <TabsList
        v-if="checkAccess('menuItem-etiCourse')"
        link="courses-backoffice"
        :countDocKey="null"
        icon=""
        labelKey="coursesETI"
        :tabs="[]"/>

      <TabsList
        v-if="checkAccess('menuItem-etiInstitution')"
        link="list-eti-backoffice"
        :countDocKey="null"
        icon=""
        labelKey="listETI"
        :tabs="[]"/>

      <TabsList
        v-if="checkAccess('menuItem-priceEtiCourse')"
        link="price-course-backoffice"
        :countDocKey="null"
        icon=""
        labelKey="coursePriceETI"
        :tabs="[]"/>

      <TabsList
        v-if="checkAccess('menuItem-pricePacket')"
        link="prices-eti-backoffice"
        :countDocKey="null"
        icon=""
        labelKey="priceETI"
        :tabs="[]"/>

      <TabsList
        v-if="checkAccess('menuItem-etiDealing')"
        link="dealing-backoffice"
        :countDocKey="null"
        icon=""
        labelKey="dealingETI"
        :tabs="[]"/>

      <TabsList
        v-if="checkAccess('menuItem-agents')"
        link="agent-groups-backoffice"
        :countDocKey="null"
        icon=""
        labelKey="agentGroups"
        :tabs="[]"/>
    </b-tabs>

    <b-card v-if="checkAccess('menuItem-backOffice')" no-body>
      <router-view></router-view>
    </b-card>
  </div>
</template>

<script>
import TabsList from '@/components/atoms/TabsList.vue'
import { checkAccess } from '@/mixins/permissions'

export default {
  name: 'BackOffice',
  components: {
    TabsList
  },
  data () {
    return {
      checkAccess
    }
  },
  beforeCreate () {
    this.$store.commit('setActivePage', { name: 'backOffice', access: checkAccess('menuItem-backOffice') })
  }
}
</script>

<style lang="sass">
  @import '../../assets/sass/seafarer/main'
</style>
