import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorEducationEditStatus',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      status: this.sailorDocument.status_document,
      buttonLoader: false,
      checkAccess
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      langFields: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    }),
    mappingStatuses () {
      let statuses = this.$store.getters.statusChoose('ServiceRecord')
      if (checkAccess('admin')) statuses = statuses.concat(this.$store.getters.statusChoose('BackOffice'))
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
        if (confirmation) this.saveNewStatus()
      })
    },

    /** Save edited document status */
    saveNewStatus () {
      this.buttonLoader = true
      const body = {
        status_document: checkAccess('education', 'preVerification', this.sailorDocument) ? this.status.id : 34
      }

      this.$api.patch(`api/v2/sailor/${this.id}/education/${this.sailorDocument.id}/`, body)
        .then(response => {
          this.buttonLoader = false
          if (response.status === 'success') {
            this.$notification.success(this, this.$i18n.t('editedEducationDoc'))
            if (this.sailorDocument.status_document.id === 34 && response.data.status_document.id !== 34) {
              this.$store.commit('decrementUserNotification', 'documents_on_verification')
            }
            this.$store.dispatch('getSQCStatements', this.id)
            this.$store.dispatch('getQualificationStatements', this.id)
            this.$store.commit('updateDataSailor', { type: 'education', value: response.data })
          }
        })
    }
  }
}
