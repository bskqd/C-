import { hideDetailed } from '@/mixins/main'
import { mapState } from 'vuex'

export default {
  name: 'SailorSQCProtocolsEditStatus',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      status: this.sailorDocument.status_document,
      decision: this.sailorDocument.decision,
      buttonLoader: false,
      hideDetailed
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      // mapping documents
      solutions: state => state.directory.solutions
    }),
    mappingStatuses () {
      return this.$store.getters.statusChoose('ProtocolDKK')
    }
  },
  methods: {
    /** Save status and solution */
    saveStatus () {
      this.buttonLoader = true
      const body = {
        status_document: this.status.id,
        decision: this.decision.id
      }
      this.$api.patch(`api/v2/sailor/${this.id}/protocol_sqc/${this.sailorDocument.id}/`, body).then(response => {
        this.buttonLoader = false
        if (response.status === 'success') {
          this.$notification.success(this, this.$i18n.t('statusProtocolSQC'))
          this.$store.commit('updateDataSailor', { type: 'sailorSQCProtocols', value: response.data })
        }
      })
    }
  }
}
