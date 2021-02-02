import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorQualificationEditStatus',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      checkAccess,
      status: this.sailorDocument.status_document,
      buttonLoader: false
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    }),
    mappingStatuses () {
      let statuses = this.$store.getters.statusChoose('QualificationDoc')
      if (checkAccess('admin')) return statuses.concat(this.$store.getters.statusChoose('BackOffice'))
      if (this.sailorDocument.status_document.id === 19) statuses = statuses.filter(value => value.id !== 21)
      return statuses
    }
  },
  methods: {
    /** Verification confirmation */
    checkSave () {
      this.$swal({
        title: this.$i18n.t('warning'),
        text: this.$i18n.t('continueVerification'),
        icon: 'info',
        buttons: [this.$i18n.t('cancel'), this.$i18n.t('setVerify')],
        dangerMode: true
      }).then((confirmation) => {
        if (confirmation) {
          this.saveNewStatus()
        }
      })
    },

    saveNewStatus () {
      this.buttonLoader = true
      let url = `api/v2/sailor/${this.id}/qualification/${this.sailorDocument.id}/`
      if (this.sailorDocument.type_document.id === 16) {
        url = `api/v2/sailor/${this.id}/proof_diploma/${this.sailorDocument.id}/`
      }

      const body = {
        status_document: checkAccess('qualification', 'preVerification', this.sailorDocument) ? this.status.id : 34
      }

      this.$api.patch(url, body).then(response => {
        this.buttonLoader = false
        if (response.status === 'success') {
          this.$notification.success(this, this.$i18n.t('editedQualificationDoc'))
          if (this.sailorDocument.status_document.id === 34 && response.data.status_document.id !== 34) {
            this.$store.commit('decrementUserNotification', 'documents_on_verification')
          }
          this.$store.dispatch('getDiplomas', this.id)
          this.$store.dispatch('getSQCStatements', this.id)
          this.$store.dispatch('getQualificationStatements', this.id)
          this.$store.dispatch('getQualificationDocuments', this.id)
          // this.$store.commit('updateDataSailor', { type: 'qualification', value: response.data })
        }
      })
    }
  }
}
