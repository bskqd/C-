import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { required, numeric, requiredIf, maxLength, maxValue, minValue } from 'vuelidate/lib/validators'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

function formFieldsInitialState () {
  return {
    country: {
      id: 2,
      value: 'Україна',
      value_abbr: 'UA',
      value_eng: 'Ukraine'
    },
    number: null,
    port: null,
    portOther: null,
    captainNewPassport: null,
    dateIssue: null,
    dateTermination: null,
    dateRenewal: null,
    strictBlank: null,
    approvedStatement: null,
    continuingPassport: null,
    buttonLoader: false
  }
}

export default {
  name: 'SailorPassportAdd',
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      newSailorPassport: false,
      viewPortOther: false,
      sevenDaysAgoDate: null,
      dataForm: formFieldsInitialState(),
      checkAccess
    }
  },
  computed: {
    ...mapState({
      token: state => state.main.token,
      lang: state => state.main.lang,
      id: state => state.sailor.sailorId,
      labelValue: state => (state.main.lang === 'en') ? 'value_eng' : 'value',
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      // mapping documents
      existStatements: state => state.sailor.approvedSailorPassportStatements,
      allowToContinuePassport: state => state.sailor.existSailorPassports,
      mappingCountry: state => state.directory.country,
      mappingPort: state => state.directory.ports
    }),
    dateIssueObject () {
      return this.dataForm.dateIssue ? new Date(this.dataForm.dateIssue) : null
    },
    dateTerminationObject () {
      return this.dataForm.dateTermination ? new Date(this.dataForm.dateTermination) : null
    },
    dateRenewalObject () {
      return this.dataForm.dateRenewal ? new Date(this.dataForm.dateRenewal) : null
    }
  },
  validations () {
    return {
      dataForm: {
        country: {
          required: requiredIf(function () {
            return !this.newSailorPassport
          })
        },
        number: {
          required,
          maxLength: maxLength(20)
        },
        port: {
          required: requiredIf(function () {
            return (!this.dataForm.country || (this.dataForm.country && this.dataForm.country.id === 2)) && !this.newSailorPassport
          })
        },
        portOther: {
          required: requiredIf(function () {
            return this.dataForm.country && this.dataForm.country.id !== 2 && !this.newSailorPassport
          })
        },
        captain: {
          required: requiredIf(function () {
            return !this.newSailorPassport
          }),
          maxLength: maxLength(255)
        },
        strictBlank: { numeric },
        approvedStatement: {
          required: requiredIf(function () {
            return this.newSailorPassport
          })
        },
        continuingPassport: {
          required: requiredIf(function () {
            return this.dataForm.approvedStatement && this.dataForm.approvedStatement.is_continue
          })
        }
      },
      dateIssueObject: {
        required: requiredIf(function () {
          return !this.newSailorPassport
        }),
        minValue: minValue(new Date('1900-01-01')),
        maxValue: maxValue(this.sevenDaysAgoDate)
      },
      dateTerminationObject: {
        required: requiredIf(function () {
          return !this.newSailorPassport
        }),
        minValue: minValue(this.dataForm.dateIssue ? this.dateIssueObject : new Date('1900-01-01')),
        maxValue: maxValue(new Date('2200-12-31'))
      },
      dateRenewalObject: {
        minValue: minValue(this.dataForm.dateTermination ? this.dateTerminationObject : new Date('1900-01-01')),
        maxValue: maxValue(new Date('2200-12-31'))
      }
    }
  },
  mounted () {
    let date = new Date()
    date.setDate(date.getDate() - 7)
    this.sevenDaysAgoDate = date
  },
  methods: {
    /** Check validation data in form for add new seafarer passport */
    checkDataForAddNewDocument () {
      if (this.$v.$invalid) {
        return this.$v.$touch()
      } else this.addNewPassport()
    },

    /** Save new seafarer passport */
    addNewPassport () {
      this.dataForm.buttonLoader = true
      let url
      let body = {
        sailor: parseInt(this.id),
        number_document: this.dataForm.number
      }

      if (this.newSailorPassport) {
        url = `api/v2/sailor/${this.id}/sailor_passport/issue_document/`
        body.statement = this.dataForm.approvedStatement.id
        if (this.dataForm.approvedStatement.is_continue) body.passport = this.dataForm.continuingPassport.id
      } else {
        url = `api/v2/sailor/${this.id}/sailor_passport/`
        body.country = this.dataForm.country.id
        body.date_start = this.dataForm.dateIssue
        body.date_end = this.dataForm.dateTermination
        body.date_renewal = this.dataForm.dateRenewal ? this.dataForm.dateRenewal : null
        body.captain = this.dataForm.captain
        body.blank_strict_report = this.dataForm.strictBlank

        if (this.dataForm.country.id === 2) { // Ukraine
          body.port = this.dataForm.port.id
          body.other_port = null
        } else {
          body.port = this.dataForm.port.id
          body.other_port = this.dataForm.portOther
        }
      }

      this.$api.post(url, body)
        .then(response => {
          this.dataForm.buttonLoader = false
          if (response.code === 200 || response.code === 201) {
            const files = this.$refs.mediaContent.filesArray
            if (files.length) {
              this.$api.postPhoto(files, 'SeafarerPassDoc', response.data.id)
                .then((response) => {
                  if (response.status !== 'created' && response.status !== 'success') {
                    this.$notification.error(this, this.$i18n.t('errorAddFile'))
                  }
                })
            }
            this.$notification.success(this, this.$i18n.t('addedSailorPassport'))
            this.$store.commit('addDataSailor', { type: 'sailorPassport', value: response.data })
            // this.$store.dispatch('getSailorPassport', this.id)
            this.$store.commit('incrementBadgeCount', {
              child: 'passportDocument',
              parent: 'passportAll'
            })
            this.$store.commit('incrementUserNotification', 'documents_on_verification')
            this.$parent.viewAdd = false
            this.$data.dataForm = formFieldsInitialState()
            this.$v.$reset()
          }
        })
    }
  }
}
