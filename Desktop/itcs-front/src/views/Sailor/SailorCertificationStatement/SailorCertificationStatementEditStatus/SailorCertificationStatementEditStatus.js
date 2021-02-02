import { mapState } from 'vuex'

export default {
  name: 'SailorCertificationStatementEditStatus',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      status: this.sailorDocument.status_document,
      payment: this.$store.getters.paymentStatusByStatus(this.sailorDocument.is_payed)[0],
      buttonLoader: false
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      paymentStatus: state => state.directory.paymentStatus
    }),
    mappingStatuses () {
      return this.$store.getters.statusChoose('StatementETI')
    }
  },
  methods: {
    /** Save new application status */
    saveEditedStatus () {
      this.buttonLoader = true
      const body = {}
      if (this.sailorDocument.is_payed) {
        body.status_document = this.status.id
      } else {
        body.is_payed = this.payment.status
      }
      this.$api.patch(`api/v2/sailor/${this.id}/statement/certificate/${this.sailorDocument.id}/`, body)
        .then(response => {
          this.buttonLoader = false
          if (response.code === 200) {
            this.$notification.success(this, this.$i18n.t('etiStatementEdited'))
            this.$store.commit('updateDataSailor', { type: 'certificationStatement', value: response.data })
          }
        })
    }
  }
}
