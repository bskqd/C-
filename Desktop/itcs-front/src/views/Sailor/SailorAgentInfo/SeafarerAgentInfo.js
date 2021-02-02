import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { setSearchDelay } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { maxValue, minValue, required } from 'vuelidate/lib/validators'
import { mapState } from 'vuex'

export default {
  name: 'SailorAgentInfo',
  components: {
    ValidationAlert
  },
  data () {
    return {
      allAgents: [],
      agent: null,
      contractDateEnd: null,
      agentName: null,
      delaySearchSeafarer: null,
      agentEditing: false,
      searchLoader: false,
      buttonLoader: false,
      checkAccess
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      lang: state => state.main.lang
    }),
    dateEndObject () {
      return this.contractDateEnd ? new Date(this.contractDateEnd) : null
    }
  },
  mounted () {
    this.getSailorAgent()
  },
  validations: {
    agent: { required },
    dateEndObject: {
      required,
      minValue: minValue(new Date('1900-01-01')),
      maxValue: maxValue(new Date('2200-01-01'))
    }
  },
  methods: {
    /** Get sailor agent */
    getSailorAgent () {
      this.$api.get(`api/v2/sailor/${this.id}/seaman_info/`).then(response => {
        if (Object.keys(response.data).length) {
          this.agentName = `${response.data.last_name} ${response.data.first_name} ${response.data.userprofile.middle_name} (ID: ${response.data.id})`
        } else {
          this.agentName = null
        }
      })
    },

    /** Check field entries validation */
    checkFields () {
      if (this.$v.$invalid) {
        return this.$v.$touch()
      } else this.setAgent()
    },

    /** Set up sailor agent */
    setAgent () {
      this.buttonLoader = true
      const body = {
        agent_id: this.agent.id,
        date_end_proxy: this.contractDateEnd
      }
      this.$api.post(`api/v2/sailor/${this.id}/seaman/`, body).then(response => {
        this.buttonLoader = false
        this.agentEditing = false
        switch (response.status) {
          case 'created':
            this.$notification.success(this, this.$i18n.t('addedAgent'))
            this.getSailorAgent()
            break
          case 'error':
            if (response.data[0] === 'Sailor has agent') {
              this.$notification.error(this, this.$i18n.t('sailorHasAgent'))
            }
            break
        }
      })
    },

    /** Call setTimeOut mixin for search */
    startSearch (searchQuery) {
      setSearchDelay(this, searchQuery, 'delaySearchSeafarer')
    },

    /** Start agent search by name */
    goSearch (searchQuery) {
      if (searchQuery.length >= 3) {
        this.searchLoader = true
        const params = new URLSearchParams({
          page_size: 100,
          agent_name: searchQuery
        })
        this.$api.get(`api/v1/seaman/list_of_seaman/?${params}`).then(response => {
          this.searchLoader = false
          response.data.results.map(item => {
            item.fullName = `${item.last_name} ${item.first_name} ${item.userprofile.middle_name}`
          })
          this.allAgents = response.data.results
        })
      }
    },

    agentDeactivation () {
      this.$api.delete(`api/v2/sailor/${this.id}/seaman/`).then(response => {
        if (response.code === 204) {
          this.$notification.success(this, this.$i18n.t('deactivatedAgent'))
          this.getSailorAgent()
        }
      })
    }
  }
}
