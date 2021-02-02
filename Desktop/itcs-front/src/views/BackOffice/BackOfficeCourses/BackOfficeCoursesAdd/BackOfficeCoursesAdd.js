import { mapState } from 'vuex'
import { maxValue, minValue, required } from 'vuelidate/lib/validators'
import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'

function formFieldsInitialState () {
  return {
    dateStart: null,
    dateEnd: null,
    institution: null,
    course: null,
    protocolNum: null,
    isDisable: false
  }
}

export default {
  name: 'BackOfficeCoursesAdd',
  components: {
    ValidationAlert
  },
  data () {
    return {
      dataForm: formFieldsInitialState(),
      buttonLoader: false
    }
  },
  computed: {
    ...mapState({
      token: state => state.main.token,
      lang: state => state.main.lang,
      langFields: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      langInstitution: state => (state.main.lang === 'en') ? 'name_en' : 'name',
      // mapping documents
      mappingInstitution: state => state.directory.educationTraining,
      mappingCourses: state => state.directory.courses
    }),
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
        protocolNum: { required },
        institution: { required },
        course: { required }
      },
      dateStartObject: {
        required,
        minValue: minValue(new Date('1900-01-01')),
        maxValue: maxValue(new Date('2200-01-01'))
      },
      dateEndObject: {
        required,
        minValue: minValue(new Date('1900-01-01')),
        maxValue: maxValue(new Date('2200-01-01'))
      }
    }
  },
  methods: {
    /** Check fields entries validation */
    checkFields () {
      if (this.$v.$invalid) {
        return this.$v.$touch()
      } else this.addRegisteredCourse()
    },

    /** Add registered course */
    addRegisteredCourse () {
      this.buttonLoader = true
      const body = {
        institution: this.dataForm.institution.id,
        course: this.dataForm.course.id,
        date_start: this.dataForm.dateStart,
        date_end: this.dataForm.dateEnd,
        number_protocol: this.dataForm.protocolNum,
        is_disable: this.dataForm.isDisable
      }
      this.$api.post('api/v1/back_off/certificates/eti_registry/', body).then(response => {
        this.buttonLoader = false
        switch (response.status) {
          case 'created':
            this.$notification.success(this, this.$i18n.t('etiCourseAdded'))
            this.$parent.newDoc = false
            this.$parent.getCoursesETI()
            this.$data.dataForm = formFieldsInitialState()
            break
          case 'error':
            if (response.data.non_field_errors[0] === 'The fields institution, course, date_start, date_end, number_protocol must make a unique set.') {
              this.$notification.error(this, this.$i18n.t('courseExist'))
            }
            break
        }
      })
    }
  }
}
