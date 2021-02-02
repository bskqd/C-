import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { mapState } from 'vuex'
import { required } from 'vuelidate/lib/validators'

function formFieldsInitialState () {
  return {
    institution: null,
    qualification: null
  }
}

export default {
  name: 'SeafarerGraduationApplicationAdd',
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
      mappingInstitution: state => state.directory.institution
    }),
    mappingQualification () {
      return this.$store.getters.qualificationById(2)
    }
  },
  validations: {
    dataForm: {
      institution: { required },
      qualification: { required }
    }
  },
  methods: {
    /** Check fields entries */
    checkFields () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.addAdvanceTrainingApplication()
    },

    /** Add new advance training application */
    addAdvanceTrainingApplication () {
      this.buttonLoader = true
      const body = {
        level_qualification: this.dataForm.qualification.id,
        educational_institution: this.dataForm.institution.id
      }
      this.$api.post(`api/v2/sailor/${this.id}/statement/advanced_training/`, body).then(response => {
        this.buttonLoader = false
        switch (response.status) {
          case 'created':
            const files = this.$refs.mediaContent.filesArray
            if (files.length) {
              this.$api.postPhoto(files, 'StatementAdvancedTraining', response.data.id).then((response) => {
                if (response.status !== 'success' && response.status !== 'created') {
                  this.$notification.error(this, this.$i18n.t('errorAddFile'))
                }
              })
            }
            this.$notification.success(this, this.$i18n.t('advanceTrainingStatementAdded'))
            this.$store.commit('addDataSailor', { type: 'educationStatement', value: response.data })
            this.$store.commit('incrementBadgeCount', {
              child: 'educationStatement',
              parent: 'educationAll'
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
