import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'VerificationSteps',
  props: {
    sailorDocument: Object,
    getFunctionName: String
  },
  data () {
    return {
      verificationStep: this.sailorDocument.verification_status.find(step => step.is_active).order_number || 1,
      comment: null,
      checkAccess
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    })
  },
  methods: {
    setVerificationStatus () {
      const documentId = this.sailorDocument.verification_status.find(step => step.order_number === (this.verificationStep + 1)).id
      const body = {
        verification_status: documentId
      }
      let url, type
      switch (this.getFunctionName) {
        case 'getRecordBooks':
          url = `api/v2/sailor/${this.id}/service_record/${this.sailorDocument.id}/`
          type = 'serviceRecordBook'
          break
        case 'getMedicalCertificates':
          url = `api/v2/sailor/${this.id}/medical/${this.sailorDocument.id}/`
          type = 'sailorMedical'
          break
        case 'getEducationDocs':
          url = `api/v2/sailor/${this.id}/education/${this.sailorDocument.id}/`
          type = 'education'
          break
        case 'getRecordBookLineEntry':
          url = `api/v2/sailor/${this.id}/service_record/${this.sailorDocument.service_record}/line/${this.sailorDocument.id}/`
          type = 'serviceRecordBookLine'
          break
        case 'getSailorPassport':
          url = `api/v2/sailor/${this.id}/sailor_passport/${this.sailorDocument.id}/`
          type = 'sailorPassport'
          break
        case 'getQualificationDocuments':
          url = `api/v2/sailor/${this.id}/${this.sailorDocument.type_document.id === 16 ? 'proof_diploma' : 'qualification'}/${this.sailorDocument.id}/`
          type = 'qualification'
          break
        case 'getExperienceReferences':
          url = `api/v2/sailor/${this.id}/experience_certificate/${this.sailorDocument.id}/`
          type = 'experience'
          break
      }
      this.$api.patch(url, body).then(response => {
        if (response.status === 'success') {
          this.$notification.success(this, this.$i18n.t('verificationStepWasChanged'))
          this.verificationStep += 1
          // response.data.behavior = { viewVerificationStepsBlock: true }
          this.$store.commit('updateDataSailor', { type: type, value: response.data })
        }
      })
    },

    setComment (step) {
      const body = {
        document_id: step.document_id,
        comment: this.comment
      }
      this.$api.post(`api/v2/sailor/${this.id}/comment_for_verification/`, body).then(response => {
        if (response.status === 'created') {
          this.$notification.success(this, this.$i18n.t('commentWasAdded'))
          if (this.getFunctionName === 'getRecordBookLineEntry') {
            this.$store.dispatch(this.getFunctionName, { id: this.id, service_book: this.sailorDocument.service_record })
          } else {
            this.$store.dispatch(this.getFunctionName, this.id)
          }
        }
      })
    },

    deleteComment (comment) {
      this.$api.delete(`api/v2/sailor/${this.id}/comment_for_verification/${comment.id}/`).then(response => {
        if (response.status === 'deleted') {
          this.$notification.success(this, this.$i18n.t('commentWasAdded'))
          this.$store.dispatch(this.getFunctionName, this.id)
        }
      })
    }
  }
}
