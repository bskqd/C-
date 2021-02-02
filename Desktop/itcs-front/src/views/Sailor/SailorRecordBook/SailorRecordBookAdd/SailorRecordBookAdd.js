import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { checkAccess } from '@/mixins/permissions'
import { maxLength, helpers, numeric, requiredIf, minValue, maxValue, required } from 'vuelidate/lib/validators'
import { mapState } from 'vuex'

const alphaUA = helpers.regex('alpha', /^[а-щА-ЩЬьЮюЯяЇїІіЄєҐґ'\-\s ]*$/)
const alphaEN = helpers.regex('alpha', /^[a-zA-Z'\- ]*$/)

function formFieldsInitialState () {
  return {
    newRBAgent: null,
    number: null,
    affiliate: null,
    dateIssue: null,
    agentLNameUK: null,
    agentFNameUK: null,
    agentMNameUK: null,
    agentLNameEN: null,
    agentFNameEN: null,
    agentMNameEN: null,
    blank: null,
    buttonLoader: false
  }
}

export default {
  name: 'SailorRecordBookAdd',
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      dataForm: formFieldsInitialState(),
      checkNewRecord: true,
      checkAccess
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      lang: state => state.main.lang,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      langAgent: state => (state.main.lang === 'en') ? 'FIO_eng' : 'FIO_ukr',
      // mapping documents
      mappingAffiliate: state => state.directory.affiliate,
      mappingAgents: state => state.directory.agents
    }),
    dateIssueObject () {
      return this.dataForm.dateIssue ? new Date(this.dataForm.dateIssue) : null
    }
  },
  validations () {
    return {
      dataForm: {
        newRBAgent: {
          required: requiredIf(function () {
            return this.checkNewRecord
          })
        },
        blank: {
          required: requiredIf(function () {
            return this.checkNewRecord
          })
        },
        number: {
          required: requiredIf(function () {
            return !this.checkNewRecord
          }),
          numeric
        },
        affiliate: {
          required: requiredIf(function () {
            return !this.checkNewRecord
          })
        },
        agentLNameUK: {
          required: requiredIf(function () {
            return !this.checkNewRecord
          }),
          maxLength: maxLength(200),
          alphaUA
        },
        agentFNameUK: {
          required: requiredIf(function () {
            return !this.checkNewRecord
          }),
          maxLength: maxLength(200),
          alphaUA
        },
        agentMNameUK: {
          maxLength: maxLength(200),
          alphaUA
        },
        agentLNameEN: {
          required: requiredIf(function () {
            return !this.checkNewRecord
          }),
          maxLength: maxLength(200),
          alphaEN
        },
        agentFNameEN: {
          required: requiredIf(function () {
            return !this.checkNewRecord
          }),
          maxLength: maxLength(200),
          alphaEN
        },
        agentMNameEN: { maxLength: maxLength(200), alphaEN }
      },
      dateIssueObject: {
        required,
        minValue: minValue(new Date('1900-01-01')),
        maxValue: maxValue(new Date())
      }
    }
  },
  mounted () {
    if (!checkAccess('serviceRecordBook', 'createNewDoc')) {
      this.checkNewRecord = false
    }
  },
  methods: {
    /** Check field validation */
    checkInfo () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.saveNewRecord()
    },

    /** Save new record book */
    saveNewRecord () {
      this.dataForm.buttonLoader = true
      const body = {
        sailor: parseInt(this.id),
        number: this.checkNewRecord ? 0 : parseInt(this.dataForm.number),
        issued_by: 'agent',
        auth_agent_ukr: this.checkNewRecord
          ? this.dataForm.newRBAgent.FIO_ukr
          : `${this.dataForm.agentLNameUK} ${this.dataForm.agentFNameUK} ${this.dataForm.agentMNameUK}`,
        auth_agent_eng: this.checkNewRecord
          ? this.dataForm.newRBAgent.FIO_eng
          : `${this.dataForm.agentLNameEN} ${this.dataForm.agentFNameEN} ${this.dataForm.agentMNameEN}`,
        branch_office: this.checkNewRecord ? 5 : this.dataForm.affiliate.id,
        date_issued: this.dataForm.dateIssue,
        new_record: Boolean(this.checkNewRecord),
        blank_strict_report: this.checkNewRecord ? this.dataForm.blank : null
      }
      this.$api.post(`api/v2/sailor/${this.id}/service_record/`, body).then(response => {
        this.dataForm.buttonLoader = false
        if (response.status === 'created') {
          if (!this.checkNewRecord && this.$refs.mediaContent && this.$refs.mediaContent.filesArray.length) {
            this.$api.postPhoto(this.$refs.mediaContent.filesArray, 'RecordBookDoc', response.data.id)
              .then((response) => {
                if (response.status !== 'created' && response.status !== 'success') {
                  this.$notification.error(this, this.$i18n.t('errorAddFile'))
                }
              })
          }

          this.$notification.success(this, this.$i18n.t('addedRecordBook'))
          this.$store.commit('addDataSailor', { type: 'serviceRecordBook', value: response.data })
          this.$parent.viewAdd = false
          this.$data.dataForm = formFieldsInitialState()
          this.$store.commit('incrementUserNotification', 'documents_on_verification')
          this.$store.commit('incrementBadgeCount', {
            child: 'recordBookDocument',
            parent: 'experienceAll'
          })
          this.$v.$reset()
        }
      })
    }
  }
}
