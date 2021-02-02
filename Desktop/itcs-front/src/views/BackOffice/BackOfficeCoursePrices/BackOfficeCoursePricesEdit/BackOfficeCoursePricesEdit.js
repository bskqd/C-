import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { maxValue, minValue, required } from 'vuelidate/lib/validators'
import { dateFormat } from '@/functions/main'
import { mapState } from 'vuex'

export default {
  name: 'BackOfficeCoursePricesEdit',
  props: {
    sailorDocument: Object
  },
  components: {
    ValidationAlert
  },
  data () {
    return {
      formTypeList: [
        {
          id: 1,
          ua: 'Ф1 (грн.)',
          en: 'F1 (uah.)',
          value: 'First'
        },
        {
          id: 2,
          ua: 'Ф2 ($)',
          en: 'F2 ($)',
          value: 'Second'
        }
      ],
      formType: this.sailorDocument.type_of_form === 'First'
        ? {
          id: 1,
          ua: 'Ф1 (грн.)',
          en: 'F1 (uah.)',
          value: 'First'
        }
        : {
          id: 2,
          ua: 'Ф2 ($)',
          en: 'F2 ($)',
          value: 'Second'
        },
      dateStart: this.sailorDocument.date_start,
      course: this.sailorDocument.course,
      price: this.sailorDocument.price,
      dateTomorrow: null,
      buttonLoader: false
    }
  },
  computed: {
    ...mapState({
      lang: state => state.main.lang,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      // mapping documents
      mappingCourses: state => state.directory.courses
    }),
    dateStartObject () {
      return this.dateStart ? new Date(this.dateStart) : null
    }
  },
  mounted () {
    // Get tomorrow's date
    let tomorrow = new Date()
    tomorrow.setDate(new Date().getDate() + 1)
    this.dateTomorrow = dateFormat(tomorrow)
  },
  validations () {
    return {
      // course: { required },
      price: { required, minValue: minValue(0) },
      formType: { required },
      dateStartObject: {
        required,
        minValue: minValue(new Date(this.dateTomorrow)),
        maxValue: maxValue(new Date('2200-01-01'))
      }
    }
  },
  methods: {
    /** Check fields entries validation */
    checkCoursePrice () {
      if (this.$v.$invalid) {
        return this.$v.$touch()
      } else this.editCoursePrice()
    },

    /** Edit ETI course price */
    editCoursePrice () {
      this.buttonLoader = true
      const body = {
        date_start: this.dateStart,
        course: this.course.id,
        price: parseFloat(this.price),
        type_of_form: this.formType.value
      }
      this.$api.patch(`api/v1/back_off/course_price/${this.sailorDocument.id}/`, body).then(response => {
        this.buttonLoader = false
        switch (response.status) {
          case 'success':
            this.$notification.success(this, this.$i18n.t('coursePriceEdited'))
            this.$store.commit('updateDataSailor', { type: 'backOfficeCoefficient', value: response.data })
            break
          case 'error':
            if (response.data.non_field_errors && response.data.non_field_errors[0] === 'Minimum date can be tomorrow') {
              this.$notification.error(this, this.$i18n.t('useTodayDate'))
            } else if (response.data.error === 'Price used - use create') {
              this.$notification.error(this, this.$i18n.t('usedPrice'))
            }
            break
        }
      })
    }
  }
}
