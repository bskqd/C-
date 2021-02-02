import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { mapState } from 'vuex'
import { required } from 'vuelidate/lib/validators'

function formFieldsInitialState () {
  return {
    eti: null,
    course: null,
    city: null
  }
}

export default {
  name: 'SailorCertificationStatementAdd',
  components: {
    ValidationAlert
  },
  data () {
    return {
      dataForm: formFieldsInitialState(),
      certApplicationInstitution: [],
      buttonLoader: false,
      institutionsCity: [
        'Чорноморськ',
        'Одеса',
        'Миколаїв',
        'Херсон',
        'Маріуполь',
        'Ізмаїл'
      ]
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      filteredInstitutionsList: state => state.directory.filteredETI,
      // mapping documents
      mappingCourses: state => state.directory.courses
    })
  },
  validations: {
    dataForm: {
      eti: { required },
      city: { required },
      course: { required }
    }
  },
  methods: {
    /** Check fields validation before submit adding */
    validateForm () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.saveCertApplication()
    },

    /** Save new eti certifications statement */
    saveCertApplication () {
      this.buttonLoader = true
      const body = {
        sailor: parseInt(this.id),
        institution: this.dataForm.eti.ntz.id,
        course: this.dataForm.course.id,
        is_payed: false
      }
      this.$api.post(`api/v2/sailor/${this.id}/statement/certificate/`, body).then(response => {
        this.buttonLoader = false
        if (response.code === 201) {
          this.$notification.success(this, this.$i18n.t('etiStatementAdded'))
          this.$store.commit('addDataSailor', { type: 'certificationStatement', value: response.data })
          this.$store.commit('incrementBadgeCount', {
            child: 'certificateStatement',
            parent: 'certificatesAll'
          })
          this.$store.commit('clearFilteredEtiList')
          this.$data.dataForm = formFieldsInitialState()
          this.$parent.viewAdd = false
        }
      })
    },

    /** Mapping available ETI for adding application by city and course */
    mappingCertApplicationInstitution () {
      if (this.dataForm.course && this.dataForm.city) {
        const searchQueries = {
          course: this.dataForm.course,
          city: this.dataForm.city,
          arrayIndex: 0,
          labelName: this.labelName
        }
        this.$store.dispatch('getFilteredETI', searchQueries).then(() => {
          this.dataForm.eti = this.filteredInstitutionsList[0][0]
        })
      }
    }
  }
}
