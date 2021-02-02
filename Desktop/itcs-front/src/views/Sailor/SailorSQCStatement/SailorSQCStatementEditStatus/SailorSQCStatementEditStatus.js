import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { requiredIf } from 'vuelidate/lib/validators'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorSQCStatementEditStatus',
  props: {
    sailorDocument: Object
  },
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      checkAccess,
      buttonLoader: false,
      buttonLoaderReject: false,
      payment: this.$store.getters.paymentStatusByStatus(this.sailorDocument.is_payed)[0],
      status: this.sailorDocument.status_document
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      // mapping documents
      paymentStatus: state => state.directory.paymentStatus
    }),
    mappingStatuses () {
      let statuses = this.$store.getters.statusChoose('StatementDKK&Qual')
      if (checkAccess('backOffice')) statuses.push(this.$store.getters.statusById(58))
      return statuses
    },
    mappingStudentStatuses () {
      return this.$store.getters.statusChoose('CadetsStatementDKK')
    },
    mediaFilesArray () {
      if (checkAccess('sailorSQCStatement', 'requiredFile', this.sailorDocument)) {
        return this.$refs.mediaContent.filesArray
      } else return []
    }
  },
  validations: {
    mediaFilesArray: {
      required: requiredIf(function () {
        return checkAccess('sailorSQCStatement', 'requiredFile', this.sailorDocument) && !checkAccess('admin')
      })
    }
  },
  methods: {
    /** Check form validation before submit */
    checkForm (status) {
      if (this.$v.$invalid) {
        return this.$v.$touch()
      } else this.saveNewSolution(status || null)
    },

    /** Save new solution in Application SQC by Seafarer */
    saveNewSolution (status) {
      let btnLoaderName = 'buttonLoader'
      const body = {
        status_document: this.status.id,
        is_payed: this.payment.status
      }
      if (checkAccess('sailorSQCStatement', 'preVerification', this.sailorDocument)) {
        body.status_document = 25
      }
      if (checkAccess('sailorSQCStatement', 'requiredFile', this.sailorDocument)) {
        body.status_document = 34
      }
      if (checkAccess('admin')) {
        btnLoaderName = 'buttonLoader'
        body.status_document = this.status.id
      }
      if (status && checkAccess('sailorSQCStatement', 'showRejectButton', this.sailorDocument)) {
        body.status_document = 23
        btnLoaderName = 'buttonLoaderReject'
      }
      this[btnLoaderName] = true
      this.$api.patch(`api/v2/sailor/${this.id}/statement/protocol_sqc/${this.sailorDocument.id}/`, body).then(response => {
        this[btnLoaderName] = false
        if (response.status === 'success') {
          if (checkAccess('sailorSQCStatement', 'requiredFile', this.sailorDocument)) {
            const files = this.$refs.mediaContent.filesArray
            this.$api.postPhoto(files, 'StatementSqp', response.data.id).then((response) => {
              if (response.status !== 'created' && response.status !== 'success') {
                this.$notification.error(this, this.$i18n.t('errorAddFile'))
              }
            })
          }

          this.$notification.success(this, this.$i18n.t('decisionStatementSQC'))
          this.$store.commit('updateDataSailor', { type: 'sailorSQCStatement', value: response.data })
          if (response.data.status_document.id === 24) {
            this.$store.commit('updateDataSailor', { type: 'successStatement', value: this.sailorDocument })
          } else {
            this.$store.commit('deleteDataSailor', { type: 'successStatement', value: this.sailorDocument })
          }

          if (this.sailorDocument.is_payed) {
            if (response.data.status_document.id === 25 && this.sailorDocument.status_document.id !== 25) {
              this.$store.commit('incrementUserNotification', 'processStatementsSQC')
            } else {
              this.$store.commit('decrementUserNotification', 'processStatementsSQC')
            }

            if (response.data.status_document.id !== 24 && this.sailorDocument.status_document.id === 24) {
              this.$store.commit('decrementUserNotification', 'approvedStatementsSQC')
            } else {
              this.$store.commit('incrementUserNotification', 'approvedStatementsSQC')
            }
          }
        }
      })
    }
  }
}
