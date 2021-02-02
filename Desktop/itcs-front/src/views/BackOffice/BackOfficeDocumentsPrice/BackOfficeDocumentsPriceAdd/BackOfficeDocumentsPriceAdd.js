import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { mapState } from 'vuex'
import { required, minValue, maxValue } from 'vuelidate/lib/validators'
import { dateFormat } from '@/functions/main'

function formFieldsInitialState () {
  return {
    documentType: null,
    formType: null,
    dateStart: null,
    coming: 0,
    toSQC: 0,
    toQD: 0,
    toTD: 0,
    toSC: 0,
    toAgent: 0,
    toMedical: 0,
    toCEC: 0,
    toPortal: 0,
    toMRC: 0
  }
}

export default {
  name: 'BackOfficePriceETIAdd',
  components: {
    ValidationAlert
  },
  props: {
    getDocuments: Function
  },
  data () {
    return {
      dateTomorrow: null,
      buttonLoader: false,
      dataForm: formFieldsInitialState()
    }
  },
  computed: {
    ...mapState({
      lang: state => state.main.lang,
      // mapping documents
      mappingAccrualTypeDoc: state => state.directory.allAccrualTypeDoc
    }),
    dateStartObject () {
      return this.dataForm.dateStart ? new Date(this.dataForm.dateStart) : null
    },
    formTypeList () {
      return [
        {
          id: 1,
          ua: 'Ф1 (грн.)',
          en: 'F1 (uah.)',
          value: 'First'
        },
        {
          id: 2,
          ua: this.dataForm.documentType && this.dataForm.documentType.id === 9 ? 'Ф2 (%)' : 'Ф2 ($)',
          en: this.dataForm.documentType && this.dataForm.documentType.id === 9 ? 'F2 (%)' : 'F2 ($)',
          value: 'Second'
        }
      ]
    }
  },
  validations () {
    return {
      dataForm: {
        documentType: { required },
        formType: { required },
        coming: { required, minValue: minValue(0) },
        toSQC: { required, minValue: minValue(0) },
        toQD: { required, minValue: minValue(0) },
        toTD: { required, minValue: minValue(0) },
        toSC: { required, minValue: minValue(0) },
        toAgent: { required, minValue: minValue(0) },
        toMedical: { required, minValue: minValue(0) },
        toCEC: { required, minValue: minValue(0) },
        toPortal: { required, minValue: minValue(0) },
        toMRC: { required, minValue: minValue(0) }
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
    /** Check fields entries validation */
    checkFields () {
      if (this.$v.$invalid) {
        return this.$v.$touch()
      } else this.addDocumentPrice()
    },

    /** Add new document price */
    addDocumentPrice () {
      this.buttonLoader = true
      const body = {
        to_sqc: parseFloat(this.dataForm.toSQC),
        to_qd: parseFloat(this.dataForm.toQD),
        to_td: parseFloat(this.dataForm.toTD),
        to_sc: parseFloat(this.dataForm.toSC),
        to_agent: parseFloat(this.dataForm.toAgent),
        to_medical: parseFloat(this.dataForm.toMedical),
        to_cec: parseFloat(this.dataForm.toCEC),
        to_portal: parseFloat(this.dataForm.toPortal),
        to_mrc: parseFloat(this.dataForm.toMRC),
        full_price: parseFloat(this.dataForm.coming),
        date_start: this.dataForm.dateStart,
        type_of_form: this.dataForm.formType.value,
        type_document: this.dataForm.documentType.id
      }
      this.$api.post('api/v1/back_off/price_for_position/', body).then(response => {
        this.buttonLoader = false
        switch (response.status) {
          case 'created':
            this.$notification.success(this, this.$i18n.t('priceEtiAdded'))
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
