import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { mapState } from 'vuex'
import { required } from 'vuelidate/lib/validators'

function formFieldsInitialState () {
  return {
    position: null,
    medInstitution: null
  }
}

export default {
  name: 'SailorMedicalStatementAdd',
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      dataForm: formFieldsInitialState(),
      buttonLoader: false
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      // mapping documents
      mappingMedicalInstitutions: state => state.directory.medInstitution,
      mappingPositions: state => state.directory.positionMedical
    })
  },
  validations: {
    dataForm: {
      position: { required },
      medInstitution: { required }
    }
  },
  methods: {
    /** Check fields entries */
    checkFields () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.addMedicalApplication()
    },

    /** Add medical application */
    addMedicalApplication () {
      this.buttonLoader = true
      const body = {
        position: this.dataForm.position.id,
        medical_institution: this.dataForm.medInstitution.id
      }
      this.$api.post(`api/v2/sailor/${this.id}/statement/medical_certificate/`, body).then(response => {
        this.buttonLoader = false
        switch (response.status) {
          case 'created':
            const files = this.$refs.mediaContent.filesArray
            if (files.length) {
              this.$api.postPhoto(files, 'StatementMedicalCertificate', response.data.id).then((response) => {
                if (response.status !== 'created' && response.status !== 'success') {
                  this.$notification.error(this, this.$i18n.t('errorAddFile'))
                }
              })
            }
            this.$notification.success(this, this.$i18n.t('medicalStatementAdded'))
            this.$store.commit('addDataSailor', { type: 'medicalStatement', value: response.data })
            this.$store.commit('incrementBadgeCount', {
              component: 'medicalApplication',
              tab: 'medicalSum'
            })
            this.$parent.viewAdd = false
            this.$data.dataForm = formFieldsInitialState()
            this.$v.$reset()
            break
          case 'error':
            if (response.data[0] === 'Statement exists') {
              this.$notification.error(this, this.$i18n.t('courseExist'))
            }
            break
        }
      })
    }
  }
}
