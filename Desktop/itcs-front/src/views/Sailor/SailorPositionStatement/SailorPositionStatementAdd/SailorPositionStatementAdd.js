import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import SailorPositionStatementPreview from '../SailorPositionStatementPreview/SailorPositionStatementPreview.vue'
import { required, requiredIf } from 'vuelidate/lib/validators'
import { enterDoublePosition, mappingAvailablePositions } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapGetters, mapState } from 'vuex'

function formFieldsInitialState () {
  return {
    typeDoc: null,
    seafarerPassport: null,
    affiliate: null,
    rank: null,
    packetTypeDoc: null,
    singleDocumentsArr: [],
    position: [],
    educationWithSQC: false
  }
}

export default {
  name: 'SeafarerPositionApplicationAdd',
  components: {
    ValidationAlert,
    FileDropZone,
    SailorPositionStatementPreview
  },
  data () {
    return {
      packetTypeDocList: [
        { id: 0, name: this.$i18n.t('diplomaProof'), value: true },
        { id: 1, name: this.$i18n.t('diplomaAndConfirmation'), value: false }
      ],
      documentsType: [
        { id: 0, name: this.$i18n.t('model-StatementETI'), value: 'statementeti' },
        { id: 1, name: this.$i18n.t('model-StatementSailorPassport'), value: 'statementsailorpassport' },
        { id: 2, name: this.$i18n.t('model-StatementMedicalCertificate'), value: 'statementmedicalcertificate' },
        { id: 3, name: this.$i18n.t('model-StatementAdvancedTraining'), value: 'statementadvancedtraining' }
      ],
      institutionsCity: [
        'Чорноморськ',
        'Одеса',
        'Миколаїв',
        'Херсон',
        'Маріуполь',
        'Ізмаїл'
      ],
      dataForm: formFieldsInitialState(),
      packageIsContinue: null,
      invalidPackageInfo: {},
      canCreatePackage: false,
      singleDocTab: false,
      buttonLoader: false,
      mappingAvailablePositions,
      enterDoublePosition,
      checkAccess
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      // mapping documents
      processingOptionsList: state => state.sailor.sailorPassportProcessing,
      ranksList: state => state.sailor.availableRank,
      affiliatesList: state => state.directory.affiliate.filter(value => !value.is_disable),
      coursesList: state => state.directory.courses,
      medicalInstitutionsList: state => state.directory.medInstitution,
      medicalPositionsList: state => state.directory.positionMedical,
      institutionsList: state => state.directory.institution,
      filteredInstitutionsList: state => state.directory.filteredETI
    }),
    ...mapGetters({
      portsList: 'notDisabledPorts',
      validProcessingOptionsList: 'validSailorPassportProcessing',
      sailorIsCadet: 'sailorIsCadet'
    }),
    qualificationLevelsList () {
      return this.$store.getters.qualificationById(2)
    }
  },
  validations: {
    dataForm: {
      affiliate: { required },
      seafarerPassport: {
        required: requiredIf(function () {
          return !this.singleDocTab
        })
      },
      position: {
        required: requiredIf(function () {
          return !this.singleDocTab
        })
      },
      rank: {
        required: requiredIf(function () {
          return !this.singleDocTab
        })
      },
      packetTypeDoc: {
        required: requiredIf(function () {
          return !this.singleDocTab && this.packageIsContinue === 1
        })
      },
      typeDoc: {
        required: requiredIf(function () {
          return this.singleDocTab
        })
      },
      singleDocumentsArr: {
        $each: {
          document_object: {
            course_id: {
              required: requiredIf(function (value) {
                const indexContentType = this.dataForm.singleDocumentsArr.findIndex(record =>
                  record.document_object.course_id === value.course_id &&
                  record.document_object.institution_id === value.institution_id &&
                  record.document_object.city === value.city)
                return this.dataForm.singleDocumentsArr[indexContentType].content_type === 'statementeti' && this.singleDocTab
              })
            },
            institution_id: {
              required: requiredIf(function (value) {
                const indexContentType = this.dataForm.singleDocumentsArr.findIndex(record =>
                  record.document_object.course_id === value.course_id &&
                  record.document_object.institution_id === value.institution_id &&
                  record.document_object.city === value.city)
                return this.dataForm.singleDocumentsArr[indexContentType].content_type === 'statementeti' && this.singleDocTab
              })
            },
            city: {
              required: requiredIf(function (value) {
                const indexContentType = this.dataForm.singleDocumentsArr.findIndex(record =>
                  record.document_object.course_id === value.course_id &&
                  record.document_object.institution_id === value.institution_id &&
                  record.document_object.city === value.city)
                return this.dataForm.singleDocumentsArr[indexContentType].content_type === 'statementeti' && this.singleDocTab
              })
            },
            port_id: {
              required: requiredIf(function (value) {
                const indexContentType = this.dataForm.singleDocumentsArr.findIndex(record =>
                  record.document_object.port_id === value.port_id &&
                  record.document_object.type_receipt === value.type_receipt)
                return this.dataForm.singleDocumentsArr[indexContentType].content_type === 'statementsailorpassport' && this.singleDocTab
              })
            },
            position_id: {
              required: requiredIf(function (value) {
                const indexContentType = this.dataForm.singleDocumentsArr.findIndex(record =>
                  record.document_object.position_id === value.position_id &&
                  record.document_object.medical_institution_id === value.medical_institution_id)
                return this.dataForm.singleDocumentsArr[indexContentType].content_type === 'statementmedicalcertificate' && this.singleDocTab
              })
            },
            medical_institution_id: {
              required: requiredIf(function (value) {
                const indexContentType = this.dataForm.singleDocumentsArr.findIndex(record =>
                  record.document_object.position_id === value.position_id &&
                  record.document_object.medical_institution_id === value.medical_institution_id)
                return this.dataForm.singleDocumentsArr[indexContentType].content_type === 'statementmedicalcertificate' && this.singleDocTab
              })
            },
            level_qualification_id: {
              required: requiredIf(function (value) {
                const indexContentType = this.dataForm.singleDocumentsArr.findIndex(record =>
                  record.document_object.level_qualification_id === value.level_qualification_id &&
                  record.document_object.educational_institution_id === value.educational_institution_id)
                return this.dataForm.singleDocumentsArr[indexContentType].content_type === 'statementadvancedtraining' && this.singleDocTab
              })
            },
            educational_institution_id: {
              required: requiredIf(function (value) {
                const indexContentType = this.dataForm.singleDocumentsArr.findIndex(record =>
                  record.document_object.level_qualification_id === value.level_qualification_id &&
                  record.document_object.educational_institution_id === value.educational_institution_id)
                return this.dataForm.singleDocumentsArr[indexContentType].content_type === 'statementadvancedtraining' && this.singleDocTab
              })
            }
          }
        }
      }
    }
  },
  methods: {
    /** Set active tab */
    checkSingleDoc (value) {
      this.singleDocTab = value
    },

    /** Check packet type document view */
    checkTypeDocumentView () {
      this.canCreatePackage = false
      this.invalidPackageInfo = {}
      // check @dataForm.rank is not null
      if (!this.dataForm.rank || !this.dataForm.position.length) return (this.packageIsContinue = null)

      this.packageIsContinue = null
      const notValidDocType = [57, 85, 86, 87, 88, 89, 21]
      if (!notValidDocType.includes(this.dataForm.rank.type_document)) {
        const positions = this.dataForm.position.map(position => { return position.id })
        const body = { position: positions }
        this.$api.post(`api/v2/sailor/${this.id}/check_is_continue/`, body).then(response => {
          if (response.status === 'success') {
            this.packageIsContinue = response.data.is_continue
          }
        })
      }
    },

    /** Check fields entries */
    checkNewCertApplication () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else {
        switch (this.singleDocTab) {
          case true:
            this.saveCertApplication()
            break
          case false:
            if (this.canCreatePackage) {
              this.saveCertApplication()
            } else {
              const positions = this.dataForm.position.map(position => { return position.id })
              const body = { position: positions }
              if (!this.singleDocTab && this.sailorIsCadet && this.dataForm.rank && (this.dataForm.rank.id === 23 ||
                this.dataForm.rank.id === 86 || this.dataForm.rank.id === 90)) {
                body.education_with_sqc = this.dataForm.educationWithSQC
              } else {
                body.education_with_sqc = false
              }
              this.$api.post(`api/v1/back_off/${this.id}/packet_preview/`, body).then(response => {
                if (response.data.can_create_packet) {
                  this.$notification.success(this, this.$i18n.t('validPackageInfo'))
                  if (checkAccess('positionStatement', 'createAfterPreview')) this.canCreatePackage = true
                } else {
                  this.$notification.error(this, this.$i18n.t('invalidPackageInfo'))
                }
                this.invalidPackageInfo = response.data
              })
            }
            break
        }
      }
    },

    /** Add new position application */
    saveCertApplication () {
      this.buttonLoader = true
      let body = {
        sailor_id: this.id,
        is_payed: false,
        service_center: this.dataForm.affiliate.id
      }
      if (!this.singleDocTab && this.sailorIsCadet && this.dataForm.rank && (this.dataForm.rank.id === 23 ||
        this.dataForm.rank.id === 86 || this.dataForm.rank.id === 90)) {
        body.education_with_sqc = this.dataForm.educationWithSQC
      } else {
        body.education_with_sqc = false
      }
      if (this.singleDocTab) {
        const filteredArr = JSON.parse(JSON.stringify(this.dataForm)).singleDocumentsArr.map(item => {
          switch (item.content_type) {
            case 'statementeti':
              item.document_object.course_id = item.document_object.course_id.id
              item.document_object.institution_id = item.document_object.institution_id.ntz.id
              delete item.document_object.city
              return item
            case 'statementsailorpassport':
              item.document_object.port_id = item.document_object.port_id.id
              item.document_object.type_receipt = item.document_object.type_receipt.id
              return item
            case 'statementmedicalcertificate':
              item.document_object.medical_institution_id = item.document_object.medical_institution_id.id
              item.document_object.position_id = item.document_object.position_id.id
              return item
            case 'statementadvancedtraining':
              item.document_object.educational_institution_id = item.document_object.educational_institution_id.id
              item.document_object.level_qualification_id = item.document_object.level_qualification_id.id
              return item
          }
        })
        body.dependencies = filteredArr
      } else {
        const positions = this.dataForm.position.map(val => {
          return val.id
        })
        body.include_sailor_passport = this.dataForm.seafarerPassport.id
        body.position = positions
        if (this.packageIsContinue === 1) body.is_only_proof = this.dataForm.packetTypeDoc.value
      }
      this.$api.post('api/v1/back_off/packet/', body)
        .then(response => {
          this.buttonLoader = false
          switch (response.status) {
            case 'created':
              const files = this.$refs.mediaContent.filesArray
              if (files.length) {
                this.$api.postPhoto(files, 'PacketItem', response.data.id).then((response) => {
                  if (response.status !== 'created' && response.status !== 'success') {
                    this.$notification.error(this, this.$i18n.t('errorAddFile'))
                  }
                })
              }

              this.$notification.success(this, this.$i18n.t('sailorPositionStatementAdded'))
              this.$store.commit('addDataSailor', { type: 'positionStatement', value: response.data })
              this.$parent.viewAdd = false
              this.$data.dataForm = formFieldsInitialState()
              this.$store.commit('clearFilteredEtiList')
              this.$store.commit('incrementBadgeCount', {
                child: 'positionStatement',
                parent: ''
              })
              this.$v.$reset()
              break
            case 'error':
              if (response.data[0] === 'Not diploma of higher education') {
                this.$notification.error(this, this.$i18n.t('notFoundDiploma'))
              } else if (response.data.error === 'You have some document in another statement') {
                this.$notification.error(this, this.$i18n.t('existPositionStatement',
                  { documentName: response.data.document_name, num: response.data.number }))
              } else if (response.data[0] === 'Package creation is closed this month') {
                this.$notification.error(this, this.$i18n.t('closedPackageCreating'))
              }
              break
          }
        })
    },

    /** Remove second double-position if first was removed */
    removePosition (removedPosition) {
      const doublePositions = [106, 121, 122, 123]
      if (doublePositions.includes(removedPosition.rank)) {
        this.dataForm.position.length = 0
      }
    },

    /** Push custom object to single documents array */
    createSingleDocument (documentType) {
      if (!documentType) return false
      let singleDocument = {
        content_type: documentType.value,
        document_object: {}
      }
      switch (documentType.id) {
        case 0: // ETI certificate
          singleDocument.document_object.course_id = null
          singleDocument.document_object.institution_id = null
          singleDocument.document_object.city = null
          break
        case 1: // Seafarer passport application
          singleDocument.document_object.port_id = null
          singleDocument.document_object.type_receipt = { id: 2, name_ukr: 'Потрібно за 7 днів', name_eng: 'Needed in 7 days' }
          break
        case 2: // Medical application
          singleDocument.document_object.position_id = null
          singleDocument.document_object.medical_institution_id = null
          break
        case 3: // Advance training application
          singleDocument.document_object.level_qualification_id = null
          singleDocument.document_object.educational_institution_id = null
          break
      }
      this.dataForm.singleDocumentsArr.push(singleDocument)
    },

    /** Get filtered ETI institution list by course and city */
    getInstitutionList (index) {
      const searchQueries = {
        course: this.dataForm.singleDocumentsArr[index].document_object.course_id,
        city: this.dataForm.singleDocumentsArr[index].document_object.city,
        arrayIndex: index,
        labelName: this.labelName
      }
      if (searchQueries.city && searchQueries.course) {
        this.$store.dispatch('getFilteredETI', searchQueries).then(() => {
          this.dataForm.singleDocumentsArr[index].document_object.institution_id = this.filteredInstitutionsList[index][0]
        })
      }
    },

    /** Clear document record from @singleDocumentsArr */
    clearArrayDocument (index) {
      this.dataForm.singleDocumentsArr.splice(index, 1)
      if (!this.dataForm.singleDocumentsArr.length) {
        this.dataForm.typeDoc = null
      }
    }
  }
}
