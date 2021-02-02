import { mapState } from 'vuex'
import { required, helpers } from 'vuelidate/lib/validators'
import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'

const alphaUA = helpers.regex('alpha', /^[а-щА-ЩЬьЮюЯяЇїІіЄєҐґ'()\-\s]*$/)
const alphaEN = helpers.regex('alpha', /^[a-zA-Z'()\-\s]*$/)

function formFieldsInitialState () {
  return {
    country: null,
    region: null,
    cityUkr: null,
    cityEng: null,
    typeCity: null
  }
}

export default {
  name: 'DirectoryAddress',
  components: {
    ValidationAlert
  },
  data () {
    return {
      cityType: [
        { priority: 0, name_ukr: 'Місто', name_eng: 'City' },
        { priority: 1, name_ukr: 'ПГТ', name_eng: 'Urban village' },
        { priority: 2, name_ukr: 'Село', name_eng: 'Village' },
        { priority: 3, name_ukr: 'Селище', name_eng: 'Settlement' }
      ],
      dataForm: formFieldsInitialState(),
      buttonLoader: false
    }
  },
  computed: {
    ...mapState({
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      labelValue: state => (state.main.lang === 'en') ? 'value_eng' : 'value',
      // mapping documents
      mappingCountry: state => state.directory.country
    })
  },
  validations: {
    dataForm: {
      country: { required },
      region: { required },
      cityUkr: { required, alphaUA },
      cityEng: { required, alphaEN },
      typeCity: { required }
    }
  },
  methods: {
    mappingRegion (country) {
      if (country !== null) {
        return this.$store.getters.regionById(country.id)
      } else {
        return []
      }
    },

    checkSavingNewCity () {
      if (this.$v.$invalid) {
        return this.$v.$touch()
      } else this.saveNewCity()
    },

    saveNewCity () {
      this.buttonLoader = true
      const body = {
        value: this.dataForm.cityUkr,
        value_eng: this.dataForm.cityEng,
        city_type: this.dataForm.typeCity.priority,
        region: this.dataForm.region.id
      }
      this.$api.post(`api/v1/directory/city/`, body).then(response => {
        this.buttonLoader = false
        if (response.status === 'created') {
          this.$notification.success(this, this.$i18n.t('addNewDirectory'))
          this.$data.dataForm = formFieldsInitialState()
          this.$v.$reset()
        }
      })
    }
  }
}
