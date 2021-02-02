import { mapState } from 'vuex'
import { required, maxLength, helpers, maxValue, requiredIf } from 'vuelidate/lib/validators'
import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import SelectSex from '@/components/atoms/FormComponents/SelectSex/SelectSex.vue'
import { checkAccess } from '@/mixins/permissions'

const alphaUA = helpers.regex('alpha', /^[а-щА-ЩЬьЮюЯяЇїІіЄєҐґ'\- ]*$/)
const alphaEN = helpers.regex('alpha', /^[a-zA-Z'\- ]*$/)

export default {
  name: 'AddSailor',
  components: {
    ValidationAlert,
    SelectSex
  },
  data () {
    return {
      checkAccess,
      lastNameUK: null,
      submitStatus: null,
      firstNameUK: null,
      middleNameUK: '',
      lastNameEN: null,
      firstNameEN: null,
      dateBorn: '',
      sex: null,
      taxNumber: '',
      sailorPhoto: [],
      innPhoto: []
    }
  },
  beforeCreate () {
    this.$store.commit('setActivePage', { name: 'home', access: checkAccess('main-addSailor') })
  },
  computed: {
    ...mapState({
      lang: state => state.main.lang
    })
  },
  validations: {
    lastNameUK: { required, maxLength: maxLength(200), alphaUA },
    firstNameUK: { required, maxLength: maxLength(200), alphaUA },
    middleNameUK: { maxLength: maxLength(200), alphaUA },
    lastNameEN: { required, alphaEN, maxLength: maxLength(200) },
    firstNameEN: { required, alphaEN, maxLength: maxLength(200) },
    dateBorn: { required },
    sex: { required },
    taxNumber: {
      required: requiredIf(function () {
        return !this.checkAccess('main-addSailorWithoutTaxNumber')
      })
    },
    sailorPhoto: {
      $each: {
        size: { maxValue: maxValue(41943040) }
      }
    },
    innPhoto: {
      $each: {
        size: { maxValue: maxValue(41943040) }
      }
    }
  },
  methods: {
    validateForm () {
      if (this.$v.$invalid) {
        return this.$v.$touch()
      } else {
        this.saveSailor()
      }
    },

    saveSailor () {
      const body = {
        first_name_ukr: this.firstNameUK,
        first_name_eng: this.firstNameEN,
        last_name_ukr: this.lastNameUK,
        last_name_eng: this.lastNameEN,
        middle_name_ukr: this.middleNameUK,
        sex: this.sex.id,
        date_birth: this.dateBorn,
        passport: {
          inn: this.taxNumber ? this.taxNumber : null
        }
      }

      this.$api.post('api/v2/sailor/', body).then(response => {
        if (response.code === 201) {
          this.$notification.success(this, this.$i18n.t('addedNewSailor'))

          this.$api.postPhoto(this.sailorPhoto, 'profile', response.data.id)
          this.$api.postPhoto(this.innPhoto, 'passport', response.data.id)

          this.$router.push({ name: 'sailor', params: { id: response.data.id } })
        } else {
          this.$notification.error(this, this.$i18n.t('sailorExist'))
        }
      })
    }
  }
}
