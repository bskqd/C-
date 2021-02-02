import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { hideDetailed } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'
import { maxValue, minValue, requiredIf } from 'vuelidate/lib/validators'

export default {
  name: 'AgentStatementsEdit',
  components: {
    ValidationAlert,
    FileDropZone
  },
  props: {
    sailorDocument: Object,
    getDocuments: Function
  },
  data () {
    return {
      status: this.sailorDocument.status_document,
      contractDateEnd: this.sailorDocument.date_end_proxy,
      buttonLoader: false,
      hideDetailed,
      checkAccess
    }
  },
  computed: {
    ...mapState({
      lang: state => state.main.lang,
      langFields: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr'
    }),
    mappingStatuses () {
      let statuses = this.$store.getters.statusChoose('StatementAgentSailor')
      if (checkAccess('agent')) {
        return statuses.filter(value => value.id !== 82 && value.id !== 83)
      }
      return statuses
    },
    dateEndObject () {
      return this.contractDateEnd ? new Date(this.contractDateEnd) : null
    },
    mediaFilesArray () {
      if (checkAccess('admin') || this.sailorDocument.status_document.id === 69 || this.sailorDocument.status_document.id === 82) {
        return this.$refs.mediaContent.filesArray
      } else return []
    }
  },
  validations: {
    mediaFilesArray: {
      required: requiredIf(function () {
        return (checkAccess('agent') && this.status.id === 67 && this.sailorDocument.status_document.id === 69)
      })
    },
    dateEndObject: {
      required: requiredIf(function () {
        return (checkAccess('agent') && this.status.id === 67) || (checkAccess('secretaryService') && !this.sailorDocument.date_end_proxy)
      }),
      minValue: minValue(new Date('1900-01-01')),
      maxValue: maxValue(new Date('2200-01-01'))
    }
  },
  methods: {
    /** Check field entries before submit */
    validationCheck () {
      if (this.$v.$invalid) {
        return this.$v.$touch()
      } else this.saveAgentApplicationStatus()
    },

    /** Save new status for agent application from sailor */
    saveAgentApplicationStatus () {
      this.buttonLoader = true
      let body = {
        date_end_proxy: this.contractDateEnd
      }
      if (this.sailorDocument.status_document.id !== this.status.id) body.status_document = this.status.id

      let agentFormData = new FormData()
      if (this.$refs.mediaContent) {
        for (const photo of this.$refs.mediaContent.filesArray) {
          agentFormData.append('photo', photo)
        }
      }
      this.$api.fetchPhoto(`api/v1/seaman/statement_seaman_sailor/${this.sailorDocument.id}/upload_file/`, { method: 'POST' }, agentFormData)
        .then(response => {
          this.buttonLoader = false
          if (response.status === 'success') {
            this.$api.patch(`api/v1/seaman/statement_seaman_sailor/${this.sailorDocument.id}/`, body).then(resp => {
              switch (resp.status) {
                case 'success':
                  this.$notification.success(this, this.$i18n.t('agentStatementFromSailorEdited'))
                  this.getDocuments()
                  break
                case 'error':
                  if (response.data[0] === 'Agent has reached the limit for the current month') {
                    this.$notification.error(this, this.$i18n.t('agentUserLimit'))
                  }
                  break
              }
            })
          }
        })
    }
  }
}
