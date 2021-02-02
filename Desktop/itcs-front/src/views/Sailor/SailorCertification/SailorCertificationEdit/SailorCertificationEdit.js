import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { required, minValue, maxValue } from 'vuelidate/lib/validators'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SeafarerCertificateEdit',
  props: {
    sailorDocument: Object
  },
  components: {
    ValidationAlert
  },
  data () {
    return {
      number: this.sailorDocument.ntz_number,
      dateIssued: this.sailorDocument.date_start,
      dateTerminated: this.sailorDocument.date_end,
      onlyForDPD: this.sailorDocument.is_only_dpd,
      buttonLoader: false,
      checkAccess
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      lang: state => state.main.lang
    }),
    dateIssuedObject () {
      return this.dateIssued ? new Date(this.dateIssued) : null
    },
    dateTerminatedObject () {
      return this.dateTerminated ? new Date(this.dateTerminated) : null
    }

  },
  validations () {
    return {
      number: { required },
      dateIssuedObject: {
        required,
        minValue: minValue(new Date('1900-01-01')),
        maxValue: maxValue(new Date())
      },
      dateTerminatedObject: {
        required,
        minValue: minValue(this.dateIssued ? this.dateIssuedObject : new Date('1900-01-01')),
        maxValue: maxValue(new Date('2200-12-31'))
      }
    }
  },
  methods: {
    /* Check validation before accept editing */
    checkFields () {
      if (this.$v.$invalid) {
        return this.$v.$touch()
      } else this.certificateEditing()
    },

    /** Certificate editing */
    certificateEditing () {
      this.buttonLoader = true
      const body = {
        ntz_number: this.number,
        date_start: this.dateIssued,
        date_end: this.dateTerminated
      }
      if (checkAccess('backOffice')) body.is_only_dpd = this.onlyForDPD

      this.$api.patch(`api/v2/sailor/${this.id}/certificate/${this.sailorDocument.id}/`, body).then(response => {
        this.buttonLoader = false
        if (response.status === 'success') {
          this.$notification.success(this, this.$i18n.t('editedETI'))
          this.$store.commit('updateDataSailor', { type: 'certification', value: response.data })
        }
      })
    }
  }
}
