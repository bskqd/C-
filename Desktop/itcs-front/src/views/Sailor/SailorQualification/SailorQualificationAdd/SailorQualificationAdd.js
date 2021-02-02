import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { clearPosition, hideDetailed, mappingPositions } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { maxLength, requiredIf, minValue, maxValue, required } from 'vuelidate/lib/validators'
import { mapGetters, mapState } from 'vuex'

function formFieldsInitialState () {
  return {
    number: null,
    type: null,
    rank: null,
    position: [],
    dateStart: null,
    dateEnd: null,
    diploma: null,
    country: {
      id: 2,
      value: 'Україна',
      value_abbr: 'UA',
      value_eng: 'Ukraine'
    },
    port: null,
    statements: null,
    functionPosition: [],
    limitations: [],
    strictBlank: null,
    buttonLoader: false
  }
}

export default {
  name: 'SailorQualificationAdd',
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      hideDetailed,
      checkAccess,
      clearPosition,
      mappingPositions,
      dataForm: formFieldsInitialState(),

      viewDiploma: false,
      viewDateTerm: false,
      viewPortString: false,
      checkNewDocument: true,
      viewDateTermInNewDoc: false,
      viewDiplomaInNewDoc: false,
      viewNumber: true,
      viewLimitation: false
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      token: state => state.main.token,
      lang: state => state.main.lang,
      langCountry: state => (state.main.lang === 'en') ? 'value_eng' : 'value',
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      // mapping documents
      ranks: state => state.directory.ranks,
      typeDocQual: state => state.directory.typeDocQualification,
      countryOptions: state => state.directory.country,
      ports: state => state.directory.ports,
      existStatements: state => state.sailor.successQualificationStatement,
      positionsLimitations: state => state.directory.positionLimitation
    }),
    ...mapGetters({
      diplomas: 'diplomasForQualificationDocs'
    }),
    dateStartObject () {
      return this.dataForm.dateStart ? new Date(this.dataForm.dateStart) : null
    },
    dateEndObject () {
      return this.dataForm.dateEnd ? new Date(this.dataForm.dateEnd) : null
    }
  },
  mounted () {
    if (!checkAccess('qualification', 'createNewQualification')) {
      this.checkNewQualDoc(false)
    }
  },
  validations () {
    return {
      dataForm: {
        number: {
          required: requiredIf(function () {
            return !this.checkNewDocument && this.viewNumber && !this.viewDiploma
          }),
          maxLength: maxLength(20)
        },
        country: {
          required: requiredIf(function () {
            return !this.checkNewDocument && this.viewNumber && !this.viewDiploma
          })
        },
        type: {
          required: requiredIf(function () {
            return !this.checkNewDocument
          })
        },
        port: {
          required: requiredIf(function () {
            return !this.checkNewDocument && this.dataForm.country.id === 2
          })
        },
        diploma: {
          required: requiredIf(function () {
            return (!this.checkNewDocument && this.viewDiploma)
          })
        },
        rank: {
          required: requiredIf(function () {
            return (!this.checkNewDocument && !this.viewDiploma)
          })
        },
        position: {
          required: requiredIf(function () {
            return (!this.checkNewDocument && !this.viewDiploma)
          })
        },
        statements: {
          required: requiredIf(function () {
            return this.checkNewDocument
          })
        },
        strictBlank: { required }
      },
      dateStartObject: {
        required: requiredIf(function () {
          return !this.checkNewDocument
        }),
        minValue: minValue(new Date('1900-01-01')),
        maxValue: maxValue(new Date())
      },
      dateEndObject: {
        required: requiredIf(function () {
          return (!this.checkNewDocument && this.viewDateTerm)
        }),
        minValue: minValue(new Date(this.dataForm.dateStart)),
        maxValue: maxValue(new Date('2200-12-31'))
      }
    }
  },
  methods: {
    checkNewQualDoc (val) {
      this.checkNewDocument = val
    },

    /**
     * Check type documents for show/hide fields
     * @param typeDoc: selected type document
     */
    checkTypeDocument (typeDoc) {
      this.viewDiploma = false
      this.viewDateTerm = false
      this.viewNumber = false
      this.viewLimitation = false
      switch (typeDoc.id) {
        case 16: // proof of diploma
          this.viewDiploma = true
          this.viewDateTerm = true
          this.viewLimitation = true
          break
        case 1:
        case 49: // diploma
          this.viewNumber = true
          break
        case 21:
        case 57:
        case 85:
        case 86:
        case 88:
        case 89:
          this.viewDateTerm = true
          this.viewNumber = true
          break
        default:
          this.viewNumber = true
      }
    },

    mappingFunctionByPosition (position) {
      switch (true) {
        case position && !Array.isArray(position):
          this.dataForm.functionPosition = this.$store.getters.functionByPosition(position.id)
          break
        case position && Array.isArray(position):
          this.dataForm.functionPosition = this.$store.getters.functionByPosition(position[0].id)
          break
        default:
          this.dataForm.functionPosition = []
      }
    },

    updateLimitation (model, value) {
      this.dataForm.limitations[model].mainId = value
    },

    mappingDiplomasByRank (application) {
      return this.$store.getters.diplomasByRank(application.rank_id)
    },

    /**
     * Check field validation
     */
    checkNewDoc () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else {
        this.saveQualificationDocuments()
      }
    },

    /**
     * Save new qualification document
     * @todo: испавить нормально город, если нужен
     */
    saveQualificationDocuments () {
      this.dataForm.buttonLoader = true

      let functionLimitations = this.dataForm.limitations.map(val => {
        let idLimit = val.map(value => {
          return value.id
        })
        return { id_func: val.mainId, id_limit: idLimit }
      })

      let positions = this.dataForm.position.map(value => {
        return value.id
      })

      let type = this.checkNewDocument ? this.dataForm.statements.type_document.id : this.dataForm.type.id
      let country = this.checkNewDocument ? null : this.dataForm.country.id
      let port = this.checkNewDocument ? null : (country === 2 ? this.dataForm.port.id : null)
      let portString = this.checkNewDocument ? null : (country === 2 ? null : this.dataForm.port)
      let number = this.checkNewDocument ? null : country === 2 ? (type === 16 ? null : this.dataForm.number) : null
      let otherNumber = this.checkNewDocument ? null : country === 2 ? null : (type === 16 ? null : this.dataForm.number)
      let dateStart = this.checkNewDocument ? null : this.dataForm.dateStart
      let dateEnd = this.checkNewDocument ? null : this.dataForm.dateEnd
      let diploma = type === 16 ? this.dataForm.diploma.id : null

      let statements = this.checkNewDocument ? this.dataForm.statements.id : null
      // let strictBlank = this.checkNewDocument ? this.dataForm.strictBlank : null
      let limitations = this.checkNewDocument ? null : functionLimitations
      let position = this.checkNewDocument ? null : type === 16 ? null : positions

      let url = `api/v2/sailor/${this.id}/qualification/`
      let typeFiles = 'QualificationDoc'

      let body = {
        sailor: parseInt(this.id),
        country: country,
        port: port,
        other_port: portString,
        number_document: number,
        other_number: otherNumber,
        list_positions: position,
        date_start: dateStart,
        date_end: dateEnd,
        type_document: type,
        photo: null,
        status_document: 2,
        diploma: diploma,
        statement: statements,
        strict_blank: this.dataForm.strictBlank,
        function_limitation: limitations,
        new_document: this.checkNewDocument
      }

      if (type === 16) {
        url = `api/v2/sailor/${this.id}/proof_diploma/`
        typeFiles = 'ProofOfWorkDiploma'
      }

      this.$api.post(url, body)
        .then(response => {
          this.dataForm.buttonLoader = false
          if (response.status === 'created') {
            const files = this.$refs.mediaContent.filesArray
            if (files.length) {
              this.$api.postPhoto(files, typeFiles, response.data.id).then((response) => {
                if (response.status !== 'success' && response.status !== 'created') {
                  this.$notification.error(this, this.$i18n.t('errorAddFile'))
                }
              })
            }

            this.$notification.success(this, this.$i18n.t('addedQualificationDoc'))
            // this.$store.commit('addDataSailor', { type: 'qualification', value: response.data })
            this.$store.dispatch('getQualificationDocuments', this.id)
            this.$parent.viewAdd = false
            this.$store.dispatch('getDiplomas', this.id)
            this.$store.commit('incrementBadgeCount', {
              child: 'qualificationDocument',
              parent: 'qualificationAll'
            })
            this.$store.commit('incrementUserNotification', 'documents_on_verification')
            this.$data.dataForm = formFieldsInitialState()
            this.$v.$reset()
          } else {
            if (response.data[0] === 'Early for create this qualification document') {
              this.$notification.error(this, this.$i18n.t('earlyToCreateQualDoc'))
            }
          }
        })
    }
  }
}
