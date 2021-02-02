import { hideDetailed } from '@/mixins/main'
import { mapState } from 'vuex'

export default {
  name: 'SailorMedicalStatementEditStatus',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      payment: this.$store.getters.paymentStatusByStatus(this.sailorDocument.is_payed)[0],
      status: this.sailorDocument.status_document,
      buttonLoader: false,
      hideDetailed
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr',
      // mapping documents
      paymentStatus: state => state.directory.paymentStatus
    }),
    mappingStatuses () {
      return this.$store.getters.statusChoose('StatementMedicalCertificate')
    }
  },
  methods: {
    /** Change medical application status */
    updateApplicationStatus () {
      this.buttonLoader = true
      const body = {}
      if (!this.sailorDocument.is_payed) {
        body.is_payed = this.payment.status
      } else {
        body.status_document = this.status.id
      }
      this.$api.patch(`api/v2/sailor/${this.id}/statement/medical_certificate/${this.sailorDocument.id}/`, body).then(response => {
        this.buttonLoader = false
        if (response.status === 'success') {
          this.$notification.success(this, this.$i18n.t('medicalStatementEdited'))
          this.$store.commit('updateDataSailor', { type: 'medicalStatement', value: response.data })
        }
      })
    }
  }
}
