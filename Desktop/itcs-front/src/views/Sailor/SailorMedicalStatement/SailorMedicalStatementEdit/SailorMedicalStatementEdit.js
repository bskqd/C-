import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { mapState } from 'vuex'
import { required } from 'vuelidate/lib/validators'

export default {
  name: 'SailorMedicalStatementEdit',
  props: {
    sailorDocument: Object
  },
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      position: this.sailorDocument.position,
      buttonLoader: false
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr',
      // mapping documents
      mappingPositions: state => state.directory.positionMedical
    })
  },
  validations: {
    position: { required }
  },
  methods: {
    /** Check fields entries */
    checkFields () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.editMedicalApplication()
    },

    /** Edit advance training application */
    editMedicalApplication () {
      this.buttonLoader = true
      const body = {
        position: this.position.id
      }
      this.$api.patch(`api/v2/sailor/${this.id}/statement/medical_certificate/${this.sailorDocument.id}/`, body)
        .then(response => {
          this.buttonLoader = false
          if (response.status === 'success') {
            const files = this.$refs.mediaContent.filesArray
            if (files.length) {
              this.$api.postPhoto(files, 'StatementMedicalCertificate', response.data.id).then((response) => {
                if (response.status !== 'created' && response.status !== 'success') {
                  this.$notification.error(this, this.$i18n.t('errorAddFile'))
                }
              })
            }
            this.$notification.success(this, this.$i18n.t('medicalStatementEdited'))
            this.$store.commit('updateDataSailor', { type: 'medicalStatement', value: response.data })
          }
        })
    }
  }
}
