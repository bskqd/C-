import { hideDetailed } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorRecordBookLineEditStatus',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      status: this.sailorDocument.status_line,
      buttonLoader: false,
      hideDetailed,
      checkAccess
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      userId: state => state.main.user.id
    }),
    mappingStatusLine () {
      let statuses = this.$store.getters.statusChoose('LineInServiceRecord')
      if (checkAccess('admin')) {
        return statuses.concat(this.$store.getters.statusChoose('BackOffice'))
      }
      if (this.userId === 188) {
        return statuses.filter(val => (val.id === 9) || (this.sailorDocument.status_line.id === 9 && val.id === 10))
      } else return statuses
    }
  },
  methods: {
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
    saveNewStatus () {
      this.buttonLoader = true
      const body = {
        status_line: checkAccess('serviceRecordBookLine', 'preVerification', this.sailorDocument) ? this.status.id : 34
      }
      this.$api.patch(`api/v2/sailor/${this.id}/service_record/${this.sailorDocument.service_record}/line/${this.sailorDocument.id}/`, body)
        .then(response => {
          this.buttonLoader = false
          if (response.status === 'success') {
            this.$notification.success(this, this.$i18n.t('editInfoRecordBook'))
            if (this.sailorDocument.status_line.id === 34 && response.data.status_line.id !== 34) {
              this.$store.commit('decrementUserNotification', 'documents_on_verification')
            }
            this.$store.commit('updateDataSailor', { type: 'serviceRecordBookLine', value: response.data })
          }
        })
    }
  }
}
