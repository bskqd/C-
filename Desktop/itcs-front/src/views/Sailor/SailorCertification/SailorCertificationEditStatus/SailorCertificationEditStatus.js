import { hideDetailed } from '@/mixins/main'
import { mapState } from 'vuex'

export default {
  name: 'SailorCertificationEditStatus',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      status: this.sailorDocument.status_document,
      hideDetailed
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    }),
    mappingStatuses () {
      return this.$store.getters.statusChoose('ServiceRecord')
    }
  },
  methods: {
    saveStatus () {
      const body = {
        status_document: this.status.id
      }

      this.$api.patch(`api/v2/sailor/${this.id}/certificate/${this.sailorDocument.id}/`, body)
        .then(response => {
          if (response.code === 200) {
            this.$notification.success(this, this.$i18n.t('statusETI'))
            this.$store.commit('updateDataSailor', { type: 'certification', value: response.data })
            this.$store.dispatch('getQualificationStatements', this.id)
            this.$store.dispatch('getSQCStatements', this.id)
          }
        })
    }
  }
}
