import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { mapState } from 'vuex'
// import { requiredIf } from 'vuelidate/lib/validators'

export default {
  name: 'SeafarerPassportApplicationEditStatus',
  components: {
    ValidationAlert
  },
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      documentNumber: null,
      payment: this.$store.getters.paymentStatusByStatus(this.sailorDocument.is_payed)[0],
      blankPayment: this.$store.getters.paymentStatusByStatus(this.sailorDocument.is_payed_blank)[0],
      status: this.sailorDocument.status_document,
      buttonLoader: false
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      langFields: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr',
      // mapping documents
      paymentStatus: state => state.directory.paymentStatus
    }),
    mappingStatuses () {
      return this.$store.getters.statusChoose('StatementSailorPassport')
    }
  },
  // validations: {
  //   documentNumber: {
  //     required: requiredIf(function () {
  //       return !this.sailorDocument.is_continue && this.sailorDocument.is_payed && this.status.id === 70
  //     })
  //   }
  // },
  methods: {
    // /** Check fields entries */
    // checkFields () {
    //   if (this.$v.$invalid) {
    //     this.$v.$touch()
    //   } else this.updateSeafarerPassportApplication()
    // },

    /** Update payment or status of Seafarer Passport application */
    updateSeafarerPassportApplication () {
      this.buttonLoader = true
      let body = {}
      if (!this.sailorDocument.is_payed || !this.sailorDocument.is_payed_blank) {
        body.is_payed = this.payment.status
      }
      // if (!this.sailorDocument.is_continue && this.sailorDocument.is_payed && this.sailorDocument.is_payed_blank && this.status.id === 70) {
      //   body.number_document = this.documentNumber
      // }
      if ((this.sailorDocument.is_payed && this.sailorDocument.is_continue) || (!this.sailorDocument.is_continue &&
        this.sailorDocument.is_payed && this.sailorDocument.is_payed_blank)) {
        body.status_document = this.status.id
      }
      if (!this.sailorDocument.is_continue && (!this.sailorDocument.is_payed_blank || !this.sailorDocument.is_payed)) {
        body.is_payed_blank = this.blankPayment.status
      }
      this.$api.patch(`api/v2/sailor/${this.id}/statement/sailor_passport/${this.sailorDocument.id}/`, body)
        .then(response => {
          this.buttonLoader = false
          switch (response.status) {
            case 'success':
              this.$notification.success(this, this.$i18n.t('sailorPassportStatementEdited'))
              this.$store.commit('updateDataSailor', { type: 'sailorPassportStatement', value: response.data })
              this.$store.dispatch('getApprovedSailorPassportStatements', this.id)
              break
            case 'error':
              if (response.data[0] === 'Sailor passport cannot be renewed') {
                this.$notification.error(this, this.$i18n.t('usedSailorPassportApplication'))
              }
              break
          }
        })
    }
  }
}
