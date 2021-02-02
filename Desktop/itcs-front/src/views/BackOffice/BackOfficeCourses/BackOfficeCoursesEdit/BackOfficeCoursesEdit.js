import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { hideDetailed } from '@/mixins/main'
import { mapState } from 'vuex'
import { maxValue, minValue, required } from 'vuelidate/lib/validators'

export default {
  name: 'BackOfficeCoursesEdit',
  props: {
    sailorDocument: Object,
    getDocuments: Function
  },
  components: {
    ValidationAlert
  },
  data () {
    return {
      dateTomorrow: null,
      buttonLoader: false,
      hideDetailed
    }
  },
  computed: {
    ...mapState({
      lang: state => state.main.lang,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      mappingCourses: state => state.directory.courses
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
        full_number_protocol: { required }
        // course: { required }
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
    validateForm () {
      if (this.$v.$invalid) {
        return this.$v.$touch()
      } else this.editCourseETI()
    },

    editCourseETI () {
      this.buttonLoader = true
      const body = {
        course: this.sailorDocument.course.id,
        date_start: this.sailorDocument.date_start,
        date_end: this.sailorDocument.date_end,
        number_protocol: this.sailorDocument.full_number_protocol.split('/')[0],
        is_disable: this.sailorDocument.is_disable
      }
      this.$api.patch(`api/v1/back_off/certificates/eti_registry/${this.sailorDocument.id}/`, body).then(response => {
        this.buttonLoader = false
        if (response.code === 200) {
          this.$notification.success(this, this.$i18n.t('etiCourseEdited'))
          this.getDocuments()
        } else {
          if (response.data.non_field_errors[0] === 'The fields institution, course, date_start, date_end, number_protocol must make a unique set.') {
            this.$notification.error(this, this.$i18n.t('courseExist'))
          }
        }
      })
    }
  }
}
