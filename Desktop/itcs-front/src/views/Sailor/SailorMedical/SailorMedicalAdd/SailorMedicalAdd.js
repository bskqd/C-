import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { hideDetailed } from '@/mixins/main'
import { required, maxValue, minValue } from 'vuelidate/lib/validators'
import { mapState } from 'vuex'

function formFieldsInitialState () {
  return {
    number: null,
    position: null,
    medInstitution: null,
    doctor: null,
    dateIssue: null,
    dateEnd: null,
    limitation: {
      id: 1,
      name_ukr: 'Немає',
      name_eng: 'None' }
  }
}

export default {
  name: 'SailorMedicalAdd',
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      dataForm: formFieldsInitialState(),
      buttonLoader: false,
      hideDetailed
    }
  },
  computed: {
    ...mapState({
      lang: state => state.main.lang,
      id: state => state.sailor.sailorId,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      // mapping documents
      mappingMedicalInstitutions: state => state.directory.medInstitution,
      mappingPositions: state => state.directory.positionMedical,
      mappingLimitations: state => state.directory.limitations
    }),
    dateIssuedObject () {
      return this.dataForm.dateIssue ? new Date(this.dataForm.dateIssue) : null
    },
    dateTerminateObject () {
      return this.dataForm.dateEnd ? new Date(this.dataForm.dateEnd) : null
    }
  },
  validations () {
    return {
      dataForm: {
        number: { required },
        position: { required },
        medInstitution: { required },
        doctor: { required }
      },
      dateIssuedObject: {
        required,
        minValue: minValue(new Date('1900-01-01')),
        maxValue: maxValue(new Date())
      },
      dateTerminateObject: {
        required,
        minValue: minValue(this.dataForm.dateIssue ? this.dateIssuedObject : new Date('1900-01-01')),
        maxValue: maxValue(new Date('2200-12-31'))
      }
    }
  },
  methods: {
    /**
     * Select doctors depending on medical institution
     * @param medInst: medical institution
     * @return doctors
     **/
    mappingDoctors (medInst) {
      if (medInst !== null) {
        if (this.dataForm.doctor !== null) {
          if (this.dataForm.doctor.medical_institution !== medInst.id) {
            this.dataForm.doctor = null
          }
        }
        return this.$store.getters.doctorsById(medInst.id)
      } else {
        this.dataForm.doctor = null
        return []
      }
    },

    /** Check field validation */
    checkInfo () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.saveNewMedicalDocument()
    },

    /** Save new medical document by Sailor */
    saveNewMedicalDocument () {
      this.buttonLoader = true
      const body = {
        number: this.dataForm.number,
        sailor: parseInt(this.id),
        position: this.dataForm.position.id,
        limitation: this.dataForm.limitation.id,
        date_end: this.dataForm.dateEnd,
        date_start: this.dataForm.dateIssue,
        doctor: this.dataForm.doctor.id,
        status_document: 2
      }
      this.$api.post(`api/v2/sailor/${this.id}/medical/`, body).then(response => {
        this.buttonLoader = false
        if (response.status === 'created') {
          const files = this.$refs.mediaContent.filesArray
          if (files.length) {
            this.$api.postPhoto(files, 'MedicalDoc', response.data.id).then((response) => {
              if (response.status !== 'created' && response.status !== 'success') {
                this.$notification.error(this, this.$i18n.t('errorAddFile'))
              }
            })
          }

          this.$notification.success(this, this.$i18n.t('addedMedDoc'))
          this.$store.commit('addDataSailor', { type: 'sailorMedical', value: response.data })
          this.$store.commit('incrementBadgeCount', {
            child: 'medicalDocument',
            parent: 'medicalAll'
          })
          this.$store.commit('incrementUserNotification', 'documents_on_verification')
          this.$data.dataForm = formFieldsInitialState()
          this.$parent.viewAdd = false
          this.$v.$reset()
        }
      })
    }
  }
}
