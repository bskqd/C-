import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { maxValue, minValue, required, requiredIf } from 'vuelidate/lib/validators'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorMedicalStatementTransfer',
  props: {
    sailorDocument: Object
  },
  components: {
    ValidationAlert
  },
  data () {
    return {
      number: null,
      doctor: null,
      limitation: null,
      dateEnd: null,
      buttonLoader: false,
      checkAccess
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      lang: state => state.main.lang,
      langFields: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      // mapping documents
      mappingLimitations: state => state.directory.limitations
      // roleMedical: state => (state.main.user.userprofile === 'medical')
    }),
    dateEndObject () {
      return this.dateEnd ? new Date(this.dateEnd) : null
    }
  },
  validations: {
    number: { required },
    limitation: { required },
    doctor: {
      required: requiredIf(function () {
        return !checkAccess('medical')
      })
    },
    dateEndObject: {
      required,
      minValue: minValue(new Date('1900-01-01')),
      maxValue: maxValue(new Date('2200-01-01'))
    }
  },
  methods: {
    /** Mapping doctors by med institution */
    mappingDoctors () {
      return this.$store.getters.doctorsById(this.sailorDocument.medical_institution.id)
    },

    /** Check fields validation before submit */
    checkInfo () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.transferApplication()
    },

    /** Transfer application to document */
    transferApplication () {
      this.buttonLoader = true
      const body = {
        number: this.number,
        doctor: !checkAccess('medicalStatement', 'enterDoctor') ? null : this.doctor.id,
        limitation: this.limitation.id,
        date_end: this.dateEnd
      }
      this.$api.post(`api/v2/sailor/${this.id}/statement/medical_certificate/${this.sailorDocument.id}/create_certificate/`, body)
        .then(response => {
          this.buttonLoader = false
          if (response.code === 200) {
            this.$notification.success(this, this.$i18n.t('transferredApplication'))
            this.$store.dispatch('getMedicalStatements', this.id)
            this.$store.dispatch('getMedicalCertificates', this.id)
            this.$store.commit('incrementBadgeCount', {
              component: 'medical',
              tab: 'medicalSum'
            })
          } else if (response.code === 400) {
            this.$notification.warning(this, this.$i18n.t('courseExist'))
          }
        })
    }
  }
}
