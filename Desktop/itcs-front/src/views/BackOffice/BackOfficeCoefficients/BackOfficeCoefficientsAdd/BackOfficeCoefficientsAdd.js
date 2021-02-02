import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { mapState } from 'vuex'
import { required, minValue, maxValue } from 'vuelidate/lib/validators'
import { dateFormat } from '@/functions/main'

function formFieldsInitialState () {
  return {
    dateStart: null,
    ntzCoefficient: null,
    profitPercent: null
  }
}

export default {
  name: 'BackOfficeCoefficientsAdd',
  components: {
    ValidationAlert
  },
  data () {
    return {
      dataForm: formFieldsInitialState(),
      dateTomorrow: null,
      buttonLoader: false
    }
  },
  computed: {
    ...mapState({
      lang: state => state.main.lang
    }),
    dateIssueObject () {
      return this.dataForm.dateStart ? new Date(this.dataForm.dateStart) : null
    }
  },
  validations () {
    return {
      dataForm: {
        ntzCoefficient: { required, minValue: minValue(0), maxValue: maxValue(100) },
        profitPercent: { required, minValue: minValue(0), maxValue: maxValue(100) }
      },
      dateIssueObject: {
        required,
        minValue: minValue(new Date(this.dateTomorrow)),
        maxValue: maxValue(new Date('2200-01-01'))
      }
    }
  },
  mounted () {
    // Get tomorrow's date
    let tomorrow = new Date()
    tomorrow.setDate(new Date().getDate() + 1)
    this.dateTomorrow = dateFormat(tomorrow)
  },
  methods: {
    validateForm () {
      if (this.$v.$invalid) {
        return this.$v.$touch()
      } else this.addNewCoefficient()
    },

    /** Add new coefficient */
    addNewCoefficient () {
      this.buttonLoader = true
      const body = {
        date_start: this.dataForm.dateStart,
        percent_of_eti: parseFloat(this.dataForm.ntzCoefficient),
        percent_of_profit: parseFloat(this.dataForm.profitPercent)
      }
      this.$api.post('api/v1/back_off/eti_profit_part/', body).then(response => {
        this.buttonLoader = false
        if (response.code === 201) {
          this.$notification.success(this, this.$i18n.t('coefficientAdd'))
          this.$parent.viewAdd = false
          this.$store.commit('addDataSailor', { type: 'backOfficeCoefficient', value: response.data })
          this.$data.dataForm = formFieldsInitialState()
        } else {
          if (response.data[0] === 'New coefficient exists - use update') {
            this.$notification.error(this, this.$i18n.t('existCoefficient'))
          } else if (response.data.non_field_errors[0] === 'Date start is early') {
            this.$notification.error(this, this.$i18n.t('useTodayDate'))
          }
        }
      })
    },

    /** Count ETI and profit percent value */
    countProfitPercent () {
      this.dataForm.profitPercent = 100 - this.dataForm.ntzCoefficient
    },
    countPercentETI () {
      this.dataForm.ntzCoefficient = 100 - this.dataForm.profitPercent
    }
  }
}
