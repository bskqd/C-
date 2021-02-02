import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { mappingQualification, mappingSpecialization, mappingProfession } from '@/mixins/main'
import { required, maxLength, requiredIf, maxValue, minValue } from 'vuelidate/lib/validators'
import { mapState } from 'vuex'

function formFieldsInitialState () {
  return {
    type: null,
    serial: null,
    registrationNumber: null,
    number: null,
    educationExtent: null,
    nameInstitution: null,
    qualification: null,
    speciality: null,
    specialization: null,
    dateIssued: null,
    dateTermination: null,
    dateEnd: null,
    yearTermination: null,
    notes: null,
    isDuplicate: false,
    buttonLoader: false
  }
}

export default {
  name: 'SailorEducationAdd',
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      dataForm: formFieldsInitialState(),
      mappingQualification,
      mappingSpecialization,
      mappingProfession,
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
      mappingTypeDoc: state => state.directory.typeDoc,
      mappingExtent: state => state.directory.extent,
      mappingInstitution: state => state.directory.institution,
      professionAll: state => state.directory.profession
    }),
    dateIssuedObject () {
      return this.dataForm.dateIssued ? new Date(this.dataForm.dateIssued) : null
    },
    dateEndObject () {
      return this.dataForm.dateEnd ? new Date(this.dataForm.dateEnd) : null
    }
  },
  validations () {
    return {
      dataForm: {
        type: { required },
        serial: { required },
        number: { required, maxLength: maxLength(30) },
        registrationNumber: { required },
        educationExtent: {
          required: requiredIf(function () {
            return this.viewDiploma
          })
        },
        nameInstitution: { required },
        qualification: { required },
        speciality: {
          required: requiredIf(function () {
            return this.viewProfession
          })
        },
        yearTermination: {
          required: requiredIf(function () {
            return this.viewYearEnd
          }),
          minValue: minValue(1900),
          maxValue: maxValue(this.dataForm.dateIssued ? this.dataForm.dateIssued.split('-')[0] : 2200)
        }
      },
      dateIssuedObject: {
        required,
        minValue: minValue(new Date('1900-01-01')),
        maxValue: maxValue(new Date())
      },
      dateEndObject: {
        required: requiredIf(function () {
          return this.viewDateEnd
        }),
        minValue: minValue(new Date('1900-01-01')),
        maxValue: maxValue(this.dataForm.dateIssued ? this.dateIssuedObject : new Date('2200-01-01'))
      }
    }
  },
  methods: {
    /**
     * Show/hide field depending on type document
     * «Свидоцтво про пидвищення квалификации» квалификации с type_NZ: 2 ПРОФЕССИИ СКРЫТЫ
     */
    checkTypeDoc () {
      this.viewDiploma = false
      this.viewSpecialization = false
      this.viewProfession = false
      this.viewDateTermination = false
      this.viewYearEnd = false
      this.viewDateEnd = false
      switch (this.dataForm.type.id) {
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
     * Check field validation
     */
    checkNewDoc () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.saveEducationDocument()
    },

    saveEducationDocument () {
      let body = {
        sailor: parseInt(this.id),
        type_document: this.dataForm.type.id,
        number_document: this.dataForm.number,
        name_nz: this.dataForm.nameInstitution.id,
        qualification: this.dataForm.qualification.id,
        is_duplicate: this.dataForm.isDuplicate,
        experied_date: this.dataForm.dateTermination,
        date_issue_document: this.dataForm.dateIssued,
        special_notes: this.dataForm.notes,
        status_document: 14,
        serial: this.dataForm.serial,
        registry_number: this.dataForm.registrationNumber
      }

      switch (this.dataForm.type.id) {
        case 1: // диплом
          body.extent = this.dataForm.educationExtent.id
          body.speciality = this.dataForm.speciality.id
          body.specialization = this.dataForm.specialization ? this.dataForm.specialization.id : null
          body.date_end_educ = this.dataForm.yearTermination + '-01-01'
          break
        case 2: // диплом квалифицированного роботника
          body.extent = null
          body.speciality = this.dataForm.speciality.id
          body.specialization = null
          body.date_end_educ = this.dataForm.yearTermination + '-01-01'
          break
        case 3: // свидетельство повышения квалификации
        case 4: // свидетельство присвоения квалификации
          body.extent = null
          body.speciality = null
          body.specialization = null
          body.date_end_educ = this.dataForm.dateEnd
          break
      }
      this.dataForm.buttonLoader = true

      this.$api.post(`api/v2/sailor/${this.id}/education/`, body)
        .then(response => {
          this.dataForm.buttonLoader = false
          if (response.status === 'created') {
            const files = this.$refs.mediaContent.filesArray
            if (files.length) {
              this.$api.postPhoto(files, 'GraduationDoc', response.data.id).then((response) => {
                if (response.status !== 'success' && response.status !== 'created') {
                  this.$notification.error(this, this.$i18n.t('errorAddFile'))
                }
              })
            }

            this.$notification.success(this, this.$i18n.t('addedEducationDoc'))
            this.$store.commit('addDataSailor', { type: 'education', value: response.data })
            this.$parent.viewAdd = false
            this.$store.commit('incrementBadgeCount', {
              child: 'educationDocument',
              parent: 'educationAll'
            })
            this.$store.commit('incrementUserNotification', 'documents_on_verification')
            this.$data.dataForm = formFieldsInitialState()
            this.$v.$reset()
          }
        })
    },

    clearSpecialization () {
      if (this.dataForm.specialization && this.dataForm.specialization.speciality !== this.dataForm.speciality.id) {
        this.dataForm.specialization = null
      }
    }
  }
}
