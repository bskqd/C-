import { helpers, required, maxLength, minLength, email, minValue, maxValue } from 'vuelidate/lib/validators'
import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import PhoneMaskInput from 'vue-phone-mask-input'
import { hideDetailed } from '@/mixins/main'
import { mapState } from 'vuex'
const alphaUA = helpers.regex('alpha', /^[а-щА-ЩЬьЮюЯяЇїІіЄєҐґ0-9'"«».,()/\-\s ]*$/)
const alphaEN = helpers.regex('alpha', /^[a-zA-Z0-9'"«».,()/\-\s ]*$/)

export default {
  name: 'BackOfficeListEditETI',
  props: {
    sailorDocument: Object
  },
  components: {
    ValidationAlert,
    PhoneMaskInput
  },
  data () {
    return {
      buttonLoader: false,
      hideDetailed
    }
  },
  computed: {
    ...mapState({
      lang: state => state.main.lang
    }),
    contractDateObject () {
      return this.sailorDocument.contract_number_date ? new Date(this.sailorDocument.contract_number_date) : null
    }
  },
  validations () {
    return {
      sailorDocument: {
        name_ukr: { required, alphaUA },
        name_eng: { required, alphaEN },
        name_abbr: { maxLength: maxLength(20) },
        address: { maxLength: maxLength(255) },
        contract_number: { maxLength: maxLength(150) },
        requisites: { maxLength: maxLength(100) },
        director_name: { maxLength: maxLength(255) },
        director_position: { maxLength: maxLength(255) },
        accountant_full_name: { maxLength: maxLength(255) },
        okpo: { required, maxLength: maxLength(10) },
        bank_name: { maxLength: maxLength(255) },
        check_number: { maxLength: maxLength(255) },
        nds_number: { maxLength: maxLength(255) },
        mfo: { maxLength: maxLength(255) },
        email: { email },
        phone: { maxLength: maxLength(13), minLength: minLength(13) }
      },
      contractDateObject: {
        minValue: minValue(new Date('1900-01-01')),
        maxValue: maxValue(new Date('2200-01-01'))
      }
    }
  },
  methods: {
    /** Check data validation in form for editing ETI directory */
    checkFields () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.editDirectoryETI()
    },

    /** Submit edited ETI directory */
    editDirectoryETI () {
      this.buttonLoader = true
      const body = {
        id: this.sailorDocument.id,
        name_ukr: this.sailorDocument.name_ukr,
        name_eng: this.sailorDocument.name_eng,
        name_abbr: this.sailorDocument.name_abbr,
        address: this.sailorDocument.address,
        contract_number: this.sailorDocument.contract_number,
        contract_number_date: this.sailorDocument.contract_number_date,
        director_name: this.sailorDocument.director_name,
        director_position: this.sailorDocument.director_position,
        accountant_full_name: this.sailorDocument.accountant_full_name,
        bank_name: this.sailorDocument.bank_name,
        check_number: this.sailorDocument.check_number,
        nds_number: this.sailorDocument.nds_number,
        mfo: this.sailorDocument.mfo,
        requisites: this.sailorDocument.requisites,
        email: this.sailorDocument.email,
        phone: this.sailorDocument.phone,
        okpo: this.sailorDocument.okpo,
        is_red: this.sailorDocument.is_red,
        is_disable: this.sailorDocument.is_disable
      }
      this.$api.patch(`api/v1/back_off/certificates/institution/${this.sailorDocument.id}/`, body).then(response => {
        this.buttonLoader = false
        if (response.status === 'success') {
          this.$notification.success(this, this.$i18n.t('etiDirectoryEdited'))
          this.$store.dispatch('getETICertificationInstitutions')
        }
      })
    }
  }
}
