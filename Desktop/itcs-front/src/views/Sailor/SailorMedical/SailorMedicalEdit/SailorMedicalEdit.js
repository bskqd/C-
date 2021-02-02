import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { required, minValue, maxValue } from 'vuelidate/lib/validators'
import { mapState } from 'vuex'

export default {
  name: 'SailorMedicalEdit',
  props: {
    sailorDocument: Object
  },
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      number: this.sailorDocument.number,
      position: this.sailorDocument.position,
      limitation: this.sailorDocument.limitation,
      medicalInstitution: this.sailorDocument.doctor.medical_institution,
      doctor: this.sailorDocument.doctor,
      buttonLoader: false
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      lang: state => state.main.lang,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      // mapping documents
      mappingMedicalInstitutions: state => state.directory.medInstitution,
      mappingPositions: state => state.directory.positionMedical,
      mappingLimitations: state => state.directory.limitations
    }),
    mappingDoctors () {
      return this.$store.getters.doctorsById(this.medicalInstitution.id)
    },
    dateIssuedObject () {
      return this.sailorDocument.date_start ? new Date(this.sailorDocument.date_start) : null
    },
    dateTerminateObject () {
      return this.sailorDocument.date_end ? new Date(this.sailorDocument.date_end) : null
    }
  },
  validations () {
    return {
      number: { required },
      doctor: { required },
      dateIssuedObject: {
        required,
        minValue: minValue(new Date('1900-01-01')),
        maxValue: maxValue(new Date())
      },
      dateTerminateObject: {
        required,
        minValue: minValue(this.sailorDocument.date_end ? this.dateIssuedObject : new Date('1900-01-01')),
        maxValue: maxValue(new Date('2200-12-31'))
      }
    }
  },
  methods: {
    /** Check validation before edit document */
    checkEditedRecord () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.saveEditRecord()
    },

    /** Edit document information */
    saveEditRecord () {
      this.buttonLoader = true
      const body = {
        number: this.number,
        position: this.position.id,
        limitation: this.limitation.id,
        doctor: this.doctor.id,
        date_start: this.sailorDocument.date_start,
        date_end: this.sailorDocument.date_end
      }
      this.$api.patch(`api/v2/sailor/${this.id}/medical/${this.sailorDocument.id}/`, body).then(response => {
        this.buttonLoader = false
        if (response.status === 'success') {
          const files = this.$refs.mediaContent.filesArray
          if (files.length) {
            this.$api.postPhoto(files, 'MedicalDoc', this.sailorDocument.id).then(response => {
              if (response.status !== 'success' && response.status !== 'created') {
                this.$notification.error(this, this.$i18n.t('errorAddFile'))
              }
            })
          }

          this.$notification.success(this, this.$i18n.t('editedMedDoc'))
          this.$store.commit('updateDataSailor', { type: 'sailorMedical', value: response.data })
        }
      })
    }
  }
}
