import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { maxValue, minValue, required } from 'vuelidate/lib/validators'
import { dateFormat } from '@/functions/main'
import { mapState } from 'vuex'

function formFieldsInitialState () {
  return {
    dateStart: null,
    course: null,
    price: null,
    formType: null,
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
    ]
  }
}

export default {
  name: 'BackOfficeCoursePricesAdd',
  data () {
    return {
      dataForm: formFieldsInitialState(),
      dateTomorrow: null,
      buttonLoader: false
    }
  },
  components: {
    ValidationAlert
  },
  props: {
    getDocuments: Function
  },
  computed: {
    ...mapState({
      lang: state => state.main.lang,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      // mapping document
      mappingCourses: state => state.directory.courses
    }),
    dateStartObject () {
      return this.dataForm.dateStart ? new Date(this.dataForm.dateStart) : null
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
      dataForm: {
        course: { required },
        price: { required, minValue: minValue(0) },
        formType: { required }
      },
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
      } else this.addCoursePrice()
    },

    /** Add ETI course prise */
    addCoursePrice () {
      this.buttonLoader = true
      const body = {
        date_start: this.dataForm.dateStart,
        course: this.dataForm.course.id,
        price: parseFloat(this.dataForm.price),
        type_of_form: this.dataForm.formType.value
      }
      this.$api.post('api/v1/back_off/course_price/', body).then(response => {
        this.buttonLoader = false
        switch (response.status) {
          case 'created':
            this.$notification.success(this, this.$i18n.t('coursePriceAdded'))
            this.$parent.viewAdd = false
            this.$data.dataForm = formFieldsInitialState()
            this.getDocuments()
            break
          case 'error':
            this.$notification.error(this, this.$i18n.t('existCoefficient'))
            break
        }
      })
    }
  }
}
