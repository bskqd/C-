import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { hideDetailed } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { requiredIf, minValue, maxValue } from 'vuelidate/lib/validators'
import { mapState } from 'vuex'

export default {
  name: 'SailorRecordBookStatementEdit',
  props: {
    sailorDocument: Object
  },
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      agent: null,
      dateStart: null,
      payment: this.sailorDocument.is_payed,
      buttonLoader: false,
      hideDetailed,
      checkAccess
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => (state.main.lang === 'en') ? 'FIO_eng' : 'FIO_ukr',
      lang: state => state.main.lang,
      // mapping documents
      mappingAgents: state => state.directory.agents
    }),
    dateStartObject () {
      return this.dateStart ? new Date(this.dateStart) : null
    }
  },
  validations: {
    agent: {
      required: requiredIf(function () {
        return this.sailorDocument.is_payed
      })
    },
    dateStartObject: {
      required: requiredIf(function () {
        return this.sailorDocument.is_payed
      }),
      minValue: minValue(new Date('1900-01-01')),
      maxValue: maxValue(new Date())
    }
  },
  methods: {
    /** Check field validation */
    checkInfo () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.processApplication()
    },

    /** Move sailor record book statement to service record */
    processApplication () {
      this.buttonLoader = true
      const body = {
        sailor_id: this.id,
        statement_id: this.sailorDocument.id,
        auth_agent_ukr: this.agent.FIO_ukr,
        auth_agent_eng: this.agent.FIO_eng,
        date_start: this.dateStart
      }
      this.$api.post(`api/v2/sailor/${this.id}/statement/service_record/${this.sailorDocument.id}/create_service_record/`, body)
        .then(response => {
          this.buttonLoader = false
          switch (response.status) {
            case 'success':
              this.$store.dispatch('getRecordBookStatement', this.id)
              this.$store.dispatch('getRecordBooks', this.id)
              this.$notification.success(this, this.$i18n.t('AddedStatementRB'))
              this.$store.commit('incrementBadgeCount', {
                child: 'recordBookDocument',
                parent: 'experienceAll'
              })
              break
            case 'Sailor does not exists':
              this.$notification.error(this, this.$i18n.t('sailorNotFound'))
              break
            default:
              this.$notification.error(this, this.$i18n.t('error'))
          }
        })
    },

    /** Change payment status or set rejected status */
    changeApplication (statusId = null) {
      this.buttonLoader = true
      const body = {}
      if (statusId) {
        body.status_document = statusId
      } else {
        body.is_payed = this.payment
      }

      this.$api.patch(`api/v2/sailor/${this.id}/statement/service_record/${this.sailorDocument.id}/`, body).then(response => {
        this.buttonLoader = false
        if (response.status === 'success') {
          if (!this.sailorDocument.is_payed && this.$refs.mediaContent.filesArray.length) {
            this.$api.postPhoto(this.$refs.mediaContent.filesArray, 'StatementServiceRecord', this.sailorDocument.id)
              .then((response) => {
                if (response.status !== 'success' && response.status !== 'created') {
                  this.$notification.error(this, this.$i18n.t('errorAddFile'))
                }
              })
          }
          this.$notification.success(this, this.$i18n.t('AddedStatementRB'))
          this.$store.commit('updateDataSailor', { type: 'recordBookStatement', value: response.data })
        }
      })
    }
  }
}
