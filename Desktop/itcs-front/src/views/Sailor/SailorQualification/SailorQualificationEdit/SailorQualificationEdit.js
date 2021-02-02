import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { clearPosition } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { requiredIf, maxLength, required, maxValue, minValue } from 'vuelidate/lib/validators'
import { mapState } from 'vuex'

export default {
  name: 'SailorQualificationEdit',
  props: {
    sailorDocument: Object
  },
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      clearPosition,
      checkAccess,
      buttonLoader: false
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      lang: state => state.main.lang,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      // mapping documents
      ranks: state => state.directory.ranks,
      typeDocQual: state => state.directory.typeDocQualification,
      country: state => state.directory.country,
      ports: state => state.directory.ports,
      diplomas: state => state.directory.diplomas,
      positionsLimitations: state => state.directory.positionLimitation
    }),
    dateStartObject () {
      return this.sailorDocument.date_start ? new Date(this.sailorDocument.date_start) : null
    },
    dateEndObject () {
      return this.sailorDocument.date_end ? new Date(this.sailorDocument.date_end) : null
    }
  },
  validations () {
    return {
      sailorDocument: {
        number_document: {
          required: requiredIf(function () {
            return (this.sailorDocument.type_document.id !== 16 && !this.sailorDocument.other_number)
          }),
          maxLength: maxLength(20)
        },
        other_number: {
          required: requiredIf(function () {
            return this.sailorDocument.other_number
          }),
          maxLength: maxLength(20)
        },
        other_port: {
          required: requiredIf(function () {
            return (!this.sailorDocument.port)
          })
        },
        list_positions: { required }
      },
      dateStartObject: {
        required,
        minValue: minValue(new Date('1900-01-01')),
        maxValue: maxValue(new Date())
      },
      dateEndObject: {
        required: requiredIf(function () {
          return (this.sailorDocument.date_end)
        }),
        minValue: minValue(this.dateStartObject),
        maxValue: maxValue(new Date('2200-12-31'))
      }
    }
  },
  methods: {
    /**
     * Mapping positions by rank
     * @param rank: rank
     * @return positions
     */
    mappingPositions (rank) {
      if (rank) {
        return this.$store.getters.positionsById(rank.id)
      } else {
        this.rank = null
        return []
      }
    },

    /** Check fields validation before accept editing info */
    checkEditedDoc () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.saveEditedDoc()
    },

    saveEditedDoc () {
      const body = {
        number_document: this.sailorDocument.number_document,
        other_number: this.sailorDocument.other_number || null,
        date_end: this.sailorDocument.date_end,
        date_start: this.sailorDocument.date_start,
        port: this.sailorDocument.port ? this.sailorDocument.port.id : null,
        other_port: this.sailorDocument.other_port ? this.sailorDocument.other_port : null,
        strict_blank: this.sailorDocument.strict_blank
      }

      this.buttonLoader = true

      let url = `api/v2/sailor/${this.id}/qualification/${this.sailorDocument.id}/`
      let typeDocument = 'QualificationDoc'

      if (this.sailorDocument.type_document.id === 16) {
        url = `api/v2/sailor/${this.id}/proof_diploma/${this.sailorDocument.id}/`
        typeDocument = 'ProofOfWorkDiploma'
      } else {
        let positions = this.sailorDocument.list_positions.map(value => {
          return value.id
        })
        body.rank = this.sailorDocument.rank.id
        body.list_positions = positions
      }

      this.$api.patch(url, body).then(response => {
        this.buttonLoader = false
        if (response.code === 200) {
          const files = this.$refs.mediaContent.filesArray
          if (files.length) {
            this.$api.postPhoto(files, typeDocument, this.sailorDocument.id).then((response) => {
              if (response.code !== 200 && response.code !== 201) {
                this.$notification.error(this, this.$i18n.t('errorAddFile'))
              }
            })
          }
          this.$notification.success(this, this.$i18n.t('editedQualificationDoc'))
          this.$store.dispatch('getQualificationDocuments', this.id)
          // this.$store.commit('updateDataSailor', { type: 'qualification', value: response.data })
        }
      })
    }
  }
}
