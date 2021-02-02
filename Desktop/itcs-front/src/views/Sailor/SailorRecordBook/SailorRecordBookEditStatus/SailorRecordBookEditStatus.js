import { hideDetailed } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorRecordBookEditStatus',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      status: this.sailorDocument.status,
      buttonLoader: false,
      hideDetailed,
      checkAccess
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
          .concat(this.$store.getters.statusChoose('ServiceRecord'))
      } else return this.$store.getters.statusChoose('ServiceRecord')
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
    /** Change recordBook status */
    saveNewStatus () {
      this.buttonLoader = true
      const body = {
        status: checkAccess('serviceRecordBook', 'preVerification', this.sailorDocument) ? this.status.id : 34
      }
      this.$api.patch(`api/v2/sailor/${this.id}/service_record/${this.sailorDocument.id}/`, body).then(response => {
        this.buttonLoader = false
        if (response.status === 'success') {
          this.$notification.success(this, this.$i18n.t('editInfoRecordBook'))
          if (this.sailorDocument.status.id === 34 && response.data.status.id !== 34) {
            this.$store.commit('decrementUserNotification', 'documents_on_verification')
          }
          this.$store.commit('updateDataSailor', { type: 'serviceRecordBook', value: response.data })
        }
      })
    }
  }
}
