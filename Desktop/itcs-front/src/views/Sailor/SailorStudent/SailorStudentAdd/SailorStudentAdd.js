import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { required, minValue, maxValue } from 'vuelidate/lib/validators'
import { mapState } from 'vuex'

function formFieldsInitialState () {
  return {
    number: null,
    serial: null,
    institution: null,
    faculty: null,
    educationForm: null,
    group: null,
    dateStart: null,
    dateEnd: null,
    status: null,
    educationWithSQC: false,
    passedEducationExam: false,
    buttonLoader: false
  }
}

export default {
  name: 'SailorStudentAdd',
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      dataForm: formFieldsInitialState()
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      lang: state => state.main.lang,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      mappingInstitution: state => state.directory.institution,
      mappingFaculties: state => state.directory.faculties,
      mappingEducForm: state => state.directory.educationForm
    }),
    mappingStatuses () {
      return this.$store.getters.statusChoose('StudentID')
    },
    dateStartObject () {
      return this.dataForm.dateStart ? new Date(this.dataForm.dateStart) : null
    },
    dateEndObject () {
      return this.dataForm.dateEnd ? new Date(this.dataForm.dateEnd) : null
    }
  },
  validations () {
    return {
      dataForm: {
        institution: { required },
        faculty: { required },
        educationForm: { required },
        status: { required }
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
      } else this.saveNewStudentCard()
    },

    /** Save new student id card by Sailor */
    saveNewStudentCard () {
      this.dataForm.buttonLoader = true
      const body = {
        sailor: parseInt(this.id),
        serial: this.dataForm.serial ? this.dataForm.serial : null,
        number: this.dataForm.number ? this.dataForm.number : null,
        name_nz: this.dataForm.institution.id,
        faculty: this.dataForm.faculty.id,
        education_form: this.dataForm.educationForm.id,
        group: this.dataForm.group ? this.dataForm.group : null,
        date_start: this.dataForm.dateStart,
        date_end: this.dataForm.dateEnd ? this.dataForm.dateEnd : null,
        status_document: this.dataForm.status.id,
        educ_with_dkk: this.dataForm.educationWithSQC,
        passed_educ_exam: this.dataForm.passedEducationExam
      }

      this.$api.post(`api/v1/cadets/student_id/`, body).then(response => {
        this.dataForm.buttonLoader = false
        if (response.code === 201) {
          const files = this.$refs.mediaContent.filesArray
          if (files.length) {
            this.$api.postPhoto(files, 'StudentCard', response.data.id).then((response) => {
              if (response.status !== 'success' && response.status !== 'created') {
                this.$notification.error(this, this.$i18n.t('errorAddFile'))
              }
            })
          }

          this.$notification.success(this, this.$i18n.t('addedStudentCard'))
          this.$store.commit('addDataSailor', { type: 'student', value: response.data })
          this.$parent.viewAdd = false
          this.$store.commit('incrementBadgeCount', {
            child: 'studentCard',
            parent: 'educationAll'
          })
          this.$data.dataForm = formFieldsInitialState()
          this.$v.$reset()
        }
      })
    }
  }
}
