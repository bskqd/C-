import { requiredIf } from 'vuelidate/lib/validators'
import { mapState } from 'vuex'

export default {
  name: 'SailorSQCStatementTableChanges',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      contentTypesList: [
        { id: 0, name_ukr: 'НТЗ', name_eng: 'ETI', content_type: 'certificateeti' },
        { id: 1, name_ukr: 'Медичний сертифікат', name_eng: 'Medical certificate', content_type: 'medicalcertificate' },
        { id: 2, name_ukr: 'Освітні документи', name_eng: 'Education document', content_type: 'education' },
        { id: 3, name_ukr: 'Кваліфікаційні документи', name_eng: 'Qualification document', content_type: 'qualificationdocument' },
        { id: 4, name_ukr: 'Підтвердження диплому', name_eng: 'Diploma confirmation', content_type: 'proofofworkdiploma' }
      ],
      tabs: null,
      newDocument: null,
      documentFrom: null,
      documentTo: null,
      contentType: null,
      activeModal: false
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      validCertificatesETI: state => state.sailor.certification.filter(value => value.status_document.id === 2),
      validMedicalCertificates: state => state.sailor.sailorMedical.filter(value => value.status_document.id === 19),
      validEducation: state => state.sailor.education.filter(value => value.status_document.id === 2),
      validQualification: state => state.sailor.qualification.filter(value => value.status_document.id === 19 && value.type_document.id !== 16),
      validDiplomaProof: state => state.sailor.qualification.filter(value => value.status_document.id === 19 && value.type_document.id === 16)
    }),
    documentFromErrors () {
      const errors = []
      if (!this.$v.documentFrom.$dirty) return errors
      !this.$v.documentFrom.required && errors.push(this.$i18n.t('emptyField'))
      return errors
    },
    documentToErrors () {
      const errors = []
      if (!this.$v.documentTo.$dirty) return errors
      !this.$v.documentTo.required && errors.push(this.$i18n.t('emptyField'))
      return errors
    },
    newDocumentErrors () {
      const errors = []
      if (!this.$v.newDocument.$dirty) return errors
      !this.$v.newDocument.required && errors.push(this.$i18n.t('emptyField'))
      return errors
    }
  },
  validations: {
    documentFrom: {
      required: requiredIf(function () {
        return this.tabs === 0
      })
    },
    documentTo: {
      required: requiredIf(function () {
        return this.tabs === 0
      })
    },
    newDocument: {
      required: requiredIf(function () {
        return this.tabs === 1
      })
    }
  },
  methods: {
    checkFieldsEntries () {
      if (this.$v.$invalid) {
        return this.$v.$touch()
      } else this.saveEditedDocument()
    },

    saveEditedDocument () {
      let method = ''
      let body = {}
      if (this.tabs === 0) {
        method = 'patch'
        body.content_type = this.documentFrom.content_type
        body.old_document = this.documentFrom.id
        body.new_document = this.documentTo.id
      } else {
        method = 'post'
        body.content_type = this.contentType.content_type
        body.new_document = this.newDocument.id
      }
      this.$api[method](`api/v2/sailor/${this.id}/statement/protocol_sqc/${this.sailorDocument.id}/related_docs/`, body)
        .then(response => {
          if (response.code === 200) {
            this.$notification.success(this, this.$i18n.t('editedDocument'))
            this.$store.dispatch('getSQCStatements', this.id)
            this.activeModal = false
          } else {
            this.$notification.error(this, this.$i18n.t('error'))
          }
        })
    },

    mappingDocumentsList (item) {
      if (item) {
        let documents = []
        switch (item.content_type) {
          case 'certificateeti':
            documents = this.validCertificatesETI
            break
          case 'medicalcertificate':
            documents = this.validMedicalCertificates
            break
          case 'education':
            documents = this.validEducation
            break
          case 'qualificationdocument':
            documents = this.validQualification
            break
          case 'proofofworkdiploma':
            documents = this.validDiplomaProof
            break
        }
        if (this.tabs === 0) documents = documents.filter(value => value.id !== item.id)
        return documents
      }
    },

    customDocumentLabel (item) {
      let type = this.tabs === 0 ? this.documentFrom : this.contentType
      if (type) {
        switch (type.content_type) {
          case 'certificateeti':
            return `${item.ntz_number} — ${item.ntz[this.labelName]}`
          case 'medicalcertificate':
            return `${item.number} — ${item.position[this.labelName]}`
          case 'education':
            return `${item.number_document} — ${item.speciality[this.labelName] || item.qualification[this.labelName]}`
          case 'qualificationdocument':
            return `${item.number} — ${item.type_document[this.labelName]} — ${item.rank[this.labelName]}`
          case 'proofofworkdiploma':
            return `${item.number_document} — ${item.rank[this.labelName]}`
        }
      }
    }
  }
}
