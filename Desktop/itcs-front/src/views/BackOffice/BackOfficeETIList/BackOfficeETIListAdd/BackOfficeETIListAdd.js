import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import PhoneMaskInput from 'vue-phone-mask-input'
import { helpers, maxLength, maxValue, minValue, required, email, minLength } from 'vuelidate/lib/validators'
import { mapState } from 'vuex'
const alphaUA = helpers.regex('alpha', /^[а-щА-ЩЬьЮюЯяЇїІіЄєҐґ0-9'"«».,()/\-\s ]*$/)
const alphaEN = helpers.regex('alpha', /^[a-zA-Z0-9'"«».,()/\-\s ]*$/)

function formFieldsInitialState () {
  return {
    nameUa: '',
    nameEn: '',
    nameAbbr: '',
    address: '',
    contractNumber: '',
    contractDate: null,
    requisites: '',
    directorName: '',
    directorPosition: '',
    accountantFullName: '',
    bank: '',
    checkNumber: '',
    ndsNumber: '',
    mfoCode: '',
    egprou: '',
    email: '',
    phone: '',
    isRed: false,
    isDisable: false
  }
}

export default {
  name: 'BackOfficeListAddETI',
  data () {
    return {
      dataForm: formFieldsInitialState(),
      buttonLoader: false
    }
  },
  components: {
    ValidationAlert,
    PhoneMaskInput
  },
  computed: {
    ...mapState({
      lang: state => state.main.lang
    }),
    contractDateObject () {
      return this.contractDate ? new Date(this.contractDate) : null
    }
  },
  validations () {
    return {
      dataForm: {
        nameUa: { required, alphaUA },
        nameEn: { required, alphaEN },
        nameAbbr: { maxLength: maxLength(20) },
        address: { maxLength: maxLength(255) },
        contractNumber: { maxLength: maxLength(150) },
        requisites: { maxLength: maxLength(100) },
        directorName: { maxLength: maxLength(255) },
        directorPosition: { maxLength: maxLength(255) },
        accountantFullName: { maxLength: maxLength(255) },
        egprou: { required, maxLength: maxLength(10) },
        bank: { maxLength: maxLength(255) },
        checkNumber: { maxLength: maxLength(255) },
        ndsNumber: { maxLength: maxLength(255) },
        mfoCode: { maxLength: maxLength(255) },
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
    /** Check data validation in form for adding new ETI directory */
    checkFields () {
      if (this.$v.$invalid) {
        return this.$v.$touch()
      } else this.addNewDirectoryETI()
    },

    /** Add new ETI directory */
    addNewDirectoryETI () {
      this.buttonLoader = true
      const body = {
        name_ukr: this.dataForm.nameUa,
        name_eng: this.dataForm.nameEn,
        name_abbr: this.dataForm.nameAbbr,
        address: this.dataForm.address,
        contract_number: this.dataForm.contractNumber,
        contract_number_date: this.dataForm.contractDate,
        director_name: this.dataForm.directorName,
        director_position: this.dataForm.directorPosition,
        accountant_full_name: this.dataForm.accountantFullName,
        bank_name: this.dataForm.bank,
        check_number: this.dataForm.checkNumber,
        nds_number: this.dataForm.ndsNumber,
        mfo: this.dataForm.mfoCode,
        requisites: this.dataForm.requisites,
        email: this.dataForm.email,
        phone: this.dataForm.phone,
        okpo: this.dataForm.egprou,
        is_red: this.dataForm.isRed,
        is_disable: this.dataForm.isDisable
      }
      this.$api.post('api/v1/back_off/certificates/institution/', body).then(response => {
        this.buttonLoader = false
        if (response.status === 'created') {
          this.$notification.success(this, this.$i18n.t('etiDirectoryAdded'))
          this.$store.dispatch('getETICertificationInstitutions')
          this.$data.dataForm = formFieldsInitialState()
          this.$parent.viewAdd = false
          this.$v.$reset()
        }
      })
    }
  }
}
