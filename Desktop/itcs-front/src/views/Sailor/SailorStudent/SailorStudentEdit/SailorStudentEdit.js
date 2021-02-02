import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { required, maxValue, minValue } from 'vuelidate/lib/validators'
import { mapState } from 'vuex'

export default {
  name: 'SailorStudentEdit',
  props: {
    sailorDocument: Object
  },
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      buttonLoader: false
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      lang: state => state.main.lang,
      langFields: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      // mapping documents
      mappingInstitution: state => state.directory.institution,
      mappingFaculties: state => state.directory.faculties,
      mappingEducForm: state => state.directory.educationForm
    }),
    dateStartObject () {
      return this.sailorDocument.date_start ? new Date(this.sailorDocument.date_start) : null
    },
    dateEndObject () {
      return this.sailorDocument.date_end ? new Date(this.sailorDocument.date_end) : null
    }
  },
  validations () {
    return {
      sailorDocument: {
        name_nz: { required },
        faculty: { required },
        education_form: { required }
      },
      dateStartObject: {
        required,
        minValue: minValue(new Date('1991-01-01')),
        maxValue: maxValue(new Date())
      },
      dateEndObject: {
        minValue: minValue(this.dateStartObject),
        maxValue: maxValue(new Date('2200-12-31'))
      }
    }
  },
  methods: {
    validateForm () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.saveEditedStudentCard()
    },

    /** Save edited student ID card */
    saveEditedStudentCard () {
      this.buttonLoader = true

      const body = {
        serial: this.sailorDocument.serial,
        number: this.sailorDocument.number,
        name_nz: this.sailorDocument.name_nz.id,
        faculty: this.sailorDocument.faculty.id,
        education_form: this.sailorDocument.education_form.id,
        group: this.sailorDocument.group ? this.sailorDocument.group : null,
        date_start: this.sailorDocument.date_start,
        date_end: this.sailorDocument.date_end ? this.sailorDocument.date_end : null,
        educ_with_dkk: this.sailorDocument.educ_with_dkk,
        passed_educ_exam: this.sailorDocument.passed_educ_exam
      }
      this.$api.patch(`api/v1/cadets/student_id/${this.sailorDocument.id}/`, body).then(response => {
        this.buttonLoader = false
        if (response.code === 200) {
          const files = this.$refs.mediaContent.filesArray
          if (files.length) {
            this.$api.postPhoto(files, 'StudentCard', response.data.id).then((response) => {
              if (response.status !== 'success' && response.status !== 'created') {
                this.$notification.error(this, this.$i18n.t('errorAddFile'))
              }
            })
          }
          this.$notification.success(this, this.$i18n.t('editedStudentCard'))
          this.$store.commit('updateDataSailor', { type: 'student', value: response.data })
        }
      })
    }
  }
}
