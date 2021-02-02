import { hideDetailed } from '@/mixins/main'
import { mapState } from 'vuex'

export default {
  name: 'SailorQualificationStatementEdit',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      buttonLoader: false,
      hideDetailed
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      langFields: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    }),
    portsList () {
      return this.$store.getters.portsActual(false)
    }
  },
  methods: {
    /** Save edited qualification application */
    saveEditedStatement () {
      this.buttonLoader = true
      const body = {
        port: this.sailorDocument.port.id
      }
      this.$api.patch(`api/v2/sailor/${this.id}/statement/qualification/${this.sailorDocument.id}/`, body).then(response => {
        this.buttonLoader = false
        if (response.status === 'success') {
          this.$notification.success(this, this.$i18n.t('editedQualificationStatement'))
          this.$store.commit('updateDataSailor', { type: 'qualificationStatement', value: response.data })
        }
      })
    }
  }
}
