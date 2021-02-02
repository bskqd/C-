import { hideDetailed } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorPassportEditStatus',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      status: this.sailorDocument.status_document,
      hideDetailed,
      checkAccess,
      buttonLoader: false
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    }),
    mappingStatuses () {
      if (checkAccess('admin')) {
        return this.$store.getters.statusChoose('BackOffice')
          .concat(this.$store.getters.statusChoose('QualificationDoc'))
      } else return this.$store.getters.statusChoose('QualificationDoc')
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
      const body = {
        status_document: checkAccess('sailorPassport', 'preVerification', this.sailorDocument) ? this.status.id : 34
      }
      this.$api.patch(`api/v2/sailor/${this.id}/sailor_passport/${this.sailorDocument.id}/`, body)
        .then(response => {
          this.buttonLoader = false
          if (response.code === 200) {
            this.$notification.success(this, this.$i18n.t('editedSailorPassport'))
            if (this.sailorDocument.status_document.id === 34 && response.data.status_document.id !== 34) {
              this.$store.commit('decrementUserNotification', 'documents_on_verification')
            }
            this.$store.commit('updateDataSailor', { type: 'sailorPassport', value: response.data })
          } else {
            this.$notification.error(this, this.$i18n.t('errorEditSailorPassport'))
          }
        })
    }
  }
}
