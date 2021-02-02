import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { dateFormat } from '@/functions/main'
import { mapState } from 'vuex'
import { required, minValue, maxValue } from 'vuelidate/lib/validators'

export default {
  name: 'BackOfficeCoefficientsEdit',
  props: {
    sailorDocument: Object
  },
  components: {
    ValidationAlert
  },
  data () {
    return {
      dateTomorrow: null,
      buttonLoader: false
    }
  },
  computed: {
    ...mapState({
      lang: state => state.main.lang
    }),
    dateStartObject () {
      return this.sailorDocument.date_start ? new Date(this.sailorDocument.date_start) : null
    }
  },
  validations () {
    return {
      sailorDocument: {
        percent_of_eti: { required, minValue: minValue(0), maxValue: maxValue(100) },
        percent_of_profit: { required, minValue: minValue(0), maxValue: maxValue(100) }
      },
      dateStartObject: {
        required,
        minValue: minValue(new Date(this.dateTomorrow)),
        maxValue: maxValue(new Date('2200-01-01'))
      }
    }
  },
  mounted () {
    // Get tomorrow's date
    let tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    this.dateTomorrow = dateFormat(tomorrow)
  },
  methods: {
    validateForm () {
      if (this.$v.$invalid) {
        return this.$v.$touch()
      } else this.saveEditedCoefficient()
    },

    saveEditedCoefficient () {
      this.buttonLoader = true
      const body = {
        date_start: this.sailorDocument.date_start,
        percent_of_eti: parseFloat(this.sailorDocument.percent_of_eti),
        percent_of_profit: parseFloat(this.sailorDocument.percent_of_profit)
      }
      this.$api.patch(`api/v1/back_off/eti_profit_part/${this.sailorDocument.id}/`, body).then(response => {
        this.buttonLoader = false
        if (response.code === 200) {
          this.$notification.success(this, this.$i18n.t('coefficientEdit'))
          this.$store.commit('updateDataSailor', { type: 'backOfficeCoefficient', value: response.data })
        } else {
          if (response.data.non_field_errors[0] === 'Date start is early') {
            this.$notification.error(this, this.$i18n.t('useTodayDate'))
          }
        }
      })
    },

    /** Count ETI and profit percent value */
    countProfitPercent () {
      this.sailorDocument.percent_of_profit = 100 - this.sailorDocument.percent_of_eti
    },
    countPercentETI () {
      this.sailorDocument.percent_of_eti = 100 - this.sailorDocument.percent_of_profit
    }
  }
}
