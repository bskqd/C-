<template>
  <v-app v-if="loaded" id="app">
    <title>{{ selfHost ? $t('autonomousSystem') : $t('morrichservice') }}</title>
    <div v-if="activePage.access" class="layout--main main-vertical navbar-sticky footer-static">
      <div class="vs-content-sidebar v-nav-menu items-no-padding" style="touch-action: none; user-select: none; -webkit-user-drag: none; -webkit-tap-highlight-color: rgba(0, 0, 0, 0);">
        <div class="vs-sidebar vs-sidebar-primary vs-sidebar-parent vs-sidebar-reduceNotRebound">
          <Menu :active="activePage.name"/>
        </div>
      </div>
      <div class="content-area-reduced" id="content-area">
        <div id="content-overlay"></div>
        <div class="relative">
          <TopBar :active="activePage.name" />
        </div>
        <div class="content-wrapper">
          <div class="router-view">
            <router-view/>
          </div>
        </div>
      </div>
    </div>
    <div v-else-if="activePage.name === 'authorization'">
      <router-view/>
    </div>
    <div
      v-else
      class="no-permission"
    >
      <div>{{ $t('noPermission') }}</div>
      <b-button @click="goBack">{{ $t('back') }}</b-button>
    </div>
    <notifications group="notify" />
  </v-app>
</template>

<script>
import Menu from '@/components/molecules/Menu/Menu.vue'
import TopBar from '@/components/molecules/TopBar/TopBar.vue'
import { setPermissions, setRoles, checkAccess } from '@/mixins/permissions'
import { goBack } from '@/mixins/main'
import { mapState } from 'vuex'

export default {
  name: 'App',
  data () {
    return {
      loadedPermissions: false,
      loadedRole: false,
      goBack,
      checkAccess
    }
  },
  components: {
    Menu,
    TopBar
  },
  beforeCreate () {
    this.$store.dispatch('getUserPermissions')
      .then(() => {
        setPermissions()
        this.getBackOfficeDocuments()
        this.loadedPermissions = true
      })
      .catch(() => {
        this.loadedPermissions = true
      })
    this.$store.dispatch('getUserInfo')
      .then(() => {
        setRoles()
        this.loadedRole = true
      })
      .catch(() => {
        this.loadedRole = true
      })
  },
  computed: {
    ...mapState({
      selfHost: state => state.main.selfHost,
      activePage: state => state.main.activePage
    }),
    loaded () {
      return this.loadedPermissions && this.loadedRole
    }
  },
  mounted () {
    if (typeof window.u2f === 'undefined') {
      this.u2f = false
    }
    this.$store.commit('setHostName')
    // this.$store.dispatch('getUserInfo')
    this.$store.dispatch('getVersion')

    this.$store.dispatch('getSex')
    this.$store.dispatch('getCountry')
    this.$store.dispatch('getRegion')
    // this.$store.dispatch('getCity')
    this.$store.dispatch('getAffiliate')
    this.$store.dispatch('getTypeDoc')
    this.$store.dispatch('getStatusDocs')
    this.$store.dispatch('getRanks')
    this.$store.dispatch('getPositions')
    this.$store.dispatch('getAgents')
    // this.$store.dispatch('getAgentsList')
    this.$store.dispatch('getPorts')
    this.$store.dispatch('getSolutions')
    this.$store.dispatch('getPositionsFunctions')
    this.$store.dispatch('getPositionsLimitations')
    this.$store.dispatch('getExtent')
    this.$store.dispatch('getNameInstitution')
    this.$store.dispatch('getProfession')
    this.$store.dispatch('getQualification')
    this.$store.dispatch('getSpecialization')
    this.$store.dispatch('getFaculties')
    this.$store.dispatch('getEducationForm')
    this.$store.dispatch('getCourses')
    this.$store.dispatch('getETI')
    this.$store.dispatch('getPositionForMedical')
    this.$store.dispatch('getMedicalInstitution')
    this.$store.dispatch('getDoctors')
    this.$store.dispatch('getCommissioners')
    // this.$store.dispatch('getAllCommissioners')
    this.$store.dispatch('getTypeDocQual')
    this.$store.dispatch('getTypeShip')
    this.$store.dispatch('getModeShipping')
    this.$store.dispatch('getTypeGEU')
    this.$store.dispatch('getResponsibility')
    this.$store.dispatch('getResponsibilityWorkBook')
    this.$store.dispatch('getPositionsOnShip')
    this.$store.dispatch('getDeliveryCity')
    this.$store.dispatch('getAllAccrualTypeDoc')
    this.$store.dispatch('getUserPermissionReport')
    this.$store.dispatch('getAllUsers')
    this.$store.dispatch('getRegistrationPermissions')
    // Get agent documents
    this.$store.dispatch('getBecomingAgentStatements')
  },
  methods: {
    getBackOfficeDocuments () {
      if (checkAccess('menuItem-etiRatio')) this.$store.dispatch('getBackOfficeCoefficients')
      if (checkAccess('menuItem-etiInstitution')) this.$store.dispatch('getETICertificationInstitutions')
      if (checkAccess('menuItem-priceEtiCourse')) this.$store.dispatch('getBackOfficeCoursePrices')
      if (checkAccess('menuItem-etiDealing')) this.$store.dispatch('getBackOfficeDealing')
      if (checkAccess('menuItem-agents')) this.$store.dispatch('getAgentGroups')
    }
  }
}
</script>
