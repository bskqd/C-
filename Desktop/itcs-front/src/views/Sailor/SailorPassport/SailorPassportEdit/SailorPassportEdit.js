import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { required, maxLength, minValue, maxValue } from 'vuelidate/lib/validators'
import { mapState } from 'vuex'

export default {
  name: 'SailorPassportEdit',
  props: {
    sailorDocument: Object
    // getDocuments: Function
  },
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      dateRenewal: this.sailorDocument.date_renewal,
      buttonLoader: false
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      lang: state => state.main.lang
    }),
    dateIssueObject () {
      return this.sailorDocument.date_start ? new Date(this.sailorDocument.date_start) : null
    },
    dateTerminationObject () {
      return this.sailorDocument.date_end ? new Date(this.sailorDocument.date_end) : null
    },
    dateRenewalObject () {
      return this.sailorDocument.date_renewal ? new Date(this.sailorDocument.date_renewal) : null
    }
  },
  validations () {
    return {
      sailorDocument: {
        number_document: { required, maxLength: maxLength(20) },
        captain: { required, maxLength: maxLength(255) }
      },
      dateIssueObject: {
        required,
        minValue: minValue(new Date('1900-01-01')),
        maxValue: maxValue(new Date())
      },
      dateTerminationObject: {
        required,
        minValue: minValue(this.sailorDocument.date_start ? this.dateIssueObject : new Date('1900-01-01')),
        maxValue: maxValue(new Date('2200-12-31'))
      },
      dateRenewalObject: {
        minValue: minValue(this.sailorDocument.date_end ? this.dateTerminationObject : new Date('1900-01-01')),
        maxValue: maxValue(new Date('2200-12-31'))
      }
    }
  },
  methods: {
    /* Check validation before accept editing */
    checkEditedDocument () {
      if (this.$v.$invalid) {
        return this.$v.$touch()
      } else this.saveEditDocument()
    },

    saveEditDocument () {
      this.buttonLoader = true
      const body = {
        number_document: this.sailorDocument.number_document,
        captain: this.sailorDocument.captain,
        date_end: this.sailorDocument.date_end,
        date_start: this.sailorDocument.date_start,
        date_renewal: this.sailorDocument.date_renewal
      }

      this.$api.patch(`api/v2/sailor/${this.id}/sailor_passport/${this.sailorDocument.id}/`, body).then(response => {
        this.buttonLoader = false
        if (response.status === 'success') {
          const files = this.$refs.mediaContent.filesArray
          if (files.length) {
            this.$api.postPhoto(files, 'SeafarerPassDoc', this.sailorDocument.id).then((response) => {
              if (response.status !== 'success' && response.status !== 'created') {
                this.$notification.error(this, this.$i18n.t('errorAddFile'))
              }
            })
          }
          this.$notification.success(this, this.$i18n.t('editedSailorPassport'))
          this.$store.commit('updateDataSailor', { type: 'sailorPassport', value: response.data })
        } else {
          this.$notification.error(this, this.$i18n.t('errorEditSailorPassport'))
        }
      })
    }
  }
}
