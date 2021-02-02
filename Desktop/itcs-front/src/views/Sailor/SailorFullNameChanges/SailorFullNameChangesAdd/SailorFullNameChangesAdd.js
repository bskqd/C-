import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { helpers, required, requiredIf } from 'vuelidate/lib/validators'
import { mapState } from 'vuex'

const alphaUA = helpers.regex('alpha', /^[а-щА-ЩЬьЮюЯяЇїІіЄєҐґ'\-\s ]*$/)
const alphaEN = helpers.regex('alpha', /^[a-zA-Z'\-\s ]*$/)

function formFieldsInitialState () {
  return {
    lastNameUa: null,
    firstNameUa: null,
    middleNameUa: null,
    lastNameEn: null,
    firstNameEn: null,
    middleNameEn: null,
    dateModified: null
  }
}

export default {
  name: 'SailorFullNameChangesAdd',
  data () {
    return {
      dataForm: formFieldsInitialState(),
      buttonLoader: false
    }
  },
  props: {
    getDocuments: Function
  },
  components: {
    ValidationAlert,
    FileDropZone
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      lang: state => state.main.lang
    })
  },
  validations: {
    dataForm: {
      lastNameUa: {
        required: requiredIf(function () {
          return this.dataForm.lastNameEn
        }),
        alphaUA
      },
      firstNameUa: {
        required: requiredIf(function () {
          return this.dataForm.firstNameEn
        }),
        alphaUA
      },
      middleNameUa: {
        required: requiredIf(function () {
          return this.dataForm.middleNameEn
        }),
        alphaUA
      },
      lastNameEn: {
        required: requiredIf(function () {
          return this.dataForm.lastNameUa
        }),
        alphaEN
      },
      firstNameEn: {
        required: requiredIf(function () {
          return this.dataForm.firstNameUa
        }),
        alphaEN
      },
      middleNameEn: { alphaEN },
      dateModified: { required }
    }
  },
  methods: {
    /** Check fields validation before changing full name */
    checkFields () {
      if (this.$v.$invalid) {
        return this.$v.$touch()
      } else this.changeFullName()
    },

    /** Change full name */
    changeFullName () {
      this.buttonLoader = true
      const body = {
        sailor: this.id,
        change_date: this.dataForm.dateModified
      }
      if (this.dataForm.lastNameUa) body.last_name_ukr = this.dataForm.lastNameUa
      if (this.dataForm.lastNameEn) body.last_name_eng = this.dataForm.lastNameEn
      if (this.dataForm.firstNameUa) body.first_name_ukr = this.dataForm.firstNameUa
      if (this.dataForm.firstNameEn) body.first_name_eng = this.dataForm.firstNameEn
      if (this.dataForm.middleNameUa) body.middle_name_ukr = this.dataForm.middleNameUa
      if (this.dataForm.middleNameEn) body.middle_name_eng = this.dataForm.middleNameEn

      this.$api.post(`api/v2/sailor/${this.id}/old_name/`, body).then(response => {
        this.buttonLoader = false
        if (response.status === 'created') {
          this.$notification.success(this, this.$i18n.t('fullNameWasChanged'))

          const files = this.$refs.mediaContent.filesArray
          if (files.length) {
            this.$api.postPhoto(files, 'OldName', response.data.id).then((response) => {
              if (response.status === 'created' || response.status === 'success') {
                this.$store.dispatch('getFullNameChanges', this.id)
              } else {
                this.$notification.error(this, this.$i18n.t('errorAddFile'))
              }
            })
          } else {
            this.$store.dispatch('getFullNameChanges', this.id)
          }
          this.$store.dispatch('getSailorInformation', this.id)

          this.$parent.viewAdd = false
          this.$data.dataForm = formFieldsInitialState()
          this.$v.$reset()
        } else {
          if (response.data[0] === 'change date is incorrect') {
            this.$notification.error(this, this.$i18n.t('notLastDate')) // less "change date" is already exist
          } else if (response.data[0] === 'not data') {
            this.$notification.error(this, this.$i18n.t('emptyField')) // no data was entered
          }
        }
      })
    }
  }
}
