import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { mapState } from 'vuex'
import { maxValue, minValue, required } from 'vuelidate/lib/validators'
import { dateFormat } from '@/functions/main'
import { hideDetailed } from '@/mixins/main'

export default {
  name: 'BackOfficeDocumentsPriceEdit',
  props: {
    row: Object,
    getDocuments: Function
  },
  components: {
    ValidationAlert
  },
  data () {
    return {
      dateTomorrow: null,
      buttonLoader: false,
      hideDetailed,

      dateStart: this.row.item.date_start,
      coming: this.row.item.full_price,
      toSQC: this.row.item.to_sqc,
      toQD: this.row.item.to_qd,
      toTD: this.row.item.to_td,
      toSC: this.row.item.to_sc,
      toAgent: this.row.item.to_agent,
      toMedical: this.row.item.to_medical,
      toCEC: this.row.item.to_cec,
      toPortal: this.row.item.to_portal,
      toMRC: this.row.item.to_mrc
    }
  },
  computed: {
    ...mapState({
      lang: state => state.main.lang
    }),
    dateStartObject () {
      return this.dateStart ? new Date(this.dateStart) : null
    }
  },
  validations () {
    return {
      coming: { required, minValue: minValue(0) },
      toSQC: { required, minValue: minValue(0) },
      toQD: { required, minValue: minValue(0) },
      toTD: { required, minValue: minValue(0) },
      toSC: { required, minValue: minValue(0) },
      toAgent: { required, minValue: minValue(0) },
      toMedical: { required, minValue: minValue(0) },
      toCEC: { required, minValue: minValue(0) },
      toPortal: { required, minValue: minValue(0) },
      toMRC: { required, minValue: minValue(0) },
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
    /** Check fields entries validation */
    checkFields () {
      if (this.$v.$invalid) {
        return this.$v.$touch()
      } else this.editDocumentPrice()
    },

    /** Edit position price for document */
    editDocumentPrice () {
      this.buttonLoader = true
      const body = {
        to_sqc: parseFloat(this.toSQC),
        to_qd: parseFloat(this.toQD),
        to_td: parseFloat(this.toTD),
        to_sc: parseFloat(this.toSC),
        to_agent: parseFloat(this.toAgent),
        to_medical: parseFloat(this.toMedical),
        to_cec: parseFloat(this.toCEC),
        to_portal: parseFloat(this.toPortal),
        full_price: parseFloat(this.coming),
        date_start: this.dateStart
      }
      this.$api.patch(`api/v1/back_off/price_for_position/${this.row.item.id}/`, body).then(response => {
        this.buttonLoader = false
        switch (response.status) {
          case 'success':
            this.$notification.success(this, this.$i18n.t('priceEtiEdited'))
            this.getDocuments()
            break
          case 'error':
            if (response.data.error === 'cannot update record') {
              this.$notification.error(this, this.$i18n.t('cantEdit'))
            }
            break
        }
      })
    }
  }
}
