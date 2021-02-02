import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { requiredIf, maxLength, maxValue, required, minValue } from 'vuelidate/lib/validators'
import { mappingSpecialization, mappingProfession, mappingQualification } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorEducationEdit',
  props: {
    sailorDocument: Object
  },
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      mappingSpecialization,
      mappingProfession,
      mappingQualification,
      checkAccess,
      buttonLoader: false,
      yearTermination: this.sailorDocument.date_end_educ.split('-')[0],
      viewProfession: false,
      viewDiploma: false,
      viewSpecialization: false,
      viewDateTermination: false,
      viewDateEnd: false,
      viewYearEnd: false
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      lang: state => state.main.lang,
      langFields: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      // mapping documents
      mappingExtent: state => state.directory.extent,
      mappingInstitution: state => state.directory.institution,
      professionAll: state => state.directory.profession
    }),
    dateIssuedObject () {
      return this.sailorDocument.date_issue_document ? new Date(this.sailorDocument.date_issue_document) : null
    },
    dateEndObject () {
      return this.sailorDocument.date_end_educ ? new Date(this.sailorDocument.date_end_educ) : null
    }
    // yearTermination () {
    //   return this.sailorDocument.date_end_educ ? this.sailorDocument.date_end_educ.split('-')[0] : null
    // }
  },
  validations () {
    return {
      sailorDocument: {
        type_document: { required },
        serial: {
          required: requiredIf(function () {
            return checkAccess('education', 'editRegistryNumber')
          })
        },
        number_document: {
          required: requiredIf(function () {
            return checkAccess('education', 'editRegistryNumber')
          }),
          maxLength: maxLength(30)
        },
        registry_number: {
          required: requiredIf(function () {
            return checkAccess('education', 'editRegistryNumber')
          })
        }
      },
      dateIssuedObject: {
        required: requiredIf(function () {
          return checkAccess('education', 'editRegistryNumber')
        }),
        minValue: minValue(new Date('1900-01-01')),
        maxValue: maxValue(new Date())
      },
      dateEndObject: {
        required: requiredIf(function () {
          return this.viewDateEnd && checkAccess('education', 'editRegistryNumber')
        }),
        minValue: minValue(new Date('1900-01-01')),
        maxValue: maxValue(this.sailorDocument.date_issue_document ? this.dateIssuedObject : new Date('2200-01-01'))
      },
      yearTermination: {
        required: requiredIf(function () {
          return this.viewYearEnd && checkAccess('education', 'editRegistryNumber')
        }),
        minValue: minValue(1900),
        maxValue: maxValue(this.sailorDocument.date_issue_document ? this.sailorDocument.date_issue_document.split('-')[0] : 2200)
      }
    }
  },
  mounted () {
    this.checkTypeDoc()
  },
  methods: {
    checkTypeDoc () {
      this.viewDiploma = false
      this.viewSpecialization = false
      this.viewProfession = false
      this.viewDateTermination = false
      this.viewYearEnd = false
      this.viewDateEnd = false
      switch (this.sailorDocument.type_document.id) {
        case 1: // диплом
          this.viewDiploma = true
          this.viewSpecialization = true
          this.viewProfession = true
          this.viewYearEnd = true
          break
        case 2: // диплом квалифицированного роботника
          this.viewProfession = true
          this.viewYearEnd = true
          break
        case 3: // свидетельство повышения квалификации
        case 4: // свидетельство присвоения квалификации
          this.viewDateEnd = true
          break
      }
    },
    /**
     * Check empty field before edit document
     */
    checkEditedRecord () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.saveEditedDoc()
    },

    /**
     * Save edited document
     */
    saveEditedDoc () {
      let body = {
        number_document: this.sailorDocument.number_document,
        serial: this.sailorDocument.serial,
        registry_number: this.sailorDocument.registry_number,
        extent: this.sailorDocument.extent ? this.sailorDocument.extent.id : null,
        name_nz: this.sailorDocument.name_nz.id,
        qualification: this.sailorDocument.qualification ? this.sailorDocument.qualification.id : null,
        speciality: this.sailorDocument.speciality ? this.sailorDocument.speciality.id : null,
        specialization: this.sailorDocument.specialization ? this.sailorDocument.specialization.id : null,
        // date_end_educ: dateEndEduc,
        // experied_date: this.dateEnd,
        date_issue_document: this.sailorDocument.date_issue_document,
        special_notes: this.sailorDocument.special_notes,
        is_duplicate: this.sailorDocument.is_duplicate
      }
      // if (!this.dateEnd || this.dateEnd === '-') {
      //   this.dateEnd = null
      // }
      // let dateEndEduc
      switch (this.sailorDocument.type_document.id) {
        case 1:
        case 2:
          // dateEndEduc = this.yearEndEdu + '-01-01'
          body.date_end_educ = this.yearTermination + '-01-01'
          break
        default:
          // dateEndEduc = this.dateEndEdu
          body.date_end_educ = this.sailorDocument.date_end_educ
      }

      this.buttonLoader = true
      this.$api.patch(`api/v2/sailor/${this.id}/education/${this.sailorDocument.id}/`, body).then(response => {
        this.buttonLoader = false
        if (response.status === 'success') {
          const files = this.$refs.mediaContent.filesArray
          if (files.length) {
            this.$api.postPhoto(files, 'GraduationDoc', this.sailorDocument.id).then((response) => {
              if (response.status !== 'success' && response.status !== 'created') {
                this.$notification.error(this, this.$i18n.t('errorAddFile'))
              }
            })
          }
          this.$notification.success(this, this.$i18n.t('editedEducationDoc'))
          this.$store.commit('updateDataSailor', { type: 'education', value: response.data })
        }
      })
    }
  }
}
