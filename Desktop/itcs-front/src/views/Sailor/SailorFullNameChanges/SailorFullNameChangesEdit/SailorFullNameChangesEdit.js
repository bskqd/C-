import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { hideDetailed } from '@/mixins/main'
import { mapState } from 'vuex'
import { helpers, requiredIf, required } from 'vuelidate/lib/validators'

const alphaUA = helpers.regex('alpha', /^[а-щА-ЩЬьЮюЯяЇїІіЄєҐґ'\-\s ]*$/)
const alphaEN = helpers.regex('alpha', /^[a-zA-Z'\-\s ]*$/)

export default {
  name: 'SailorFullNameChangesEdit',
  props: {
    sailorDocument: Object
  },
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      buttonLoader: false,
      hideDetailed
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      lang: state => state.main.lang,
      labelName: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr'
    })
  },
  validations () {
    return {
      sailorDocument: {
        last_name_ukr: { required, alphaUA },
        first_name_ukr: { required, alphaUA },
        middle_name_ukr: {
          required: requiredIf(function () {
            return this.sailorDocument.middle_name_eng
          }),
          alphaUA
        },
        last_name_eng: { required, alphaEN },
        first_name_eng: { required, alphaEN },
        middle_name_eng: { alphaEN },
        change_date: { required }
      }
    }
  },
  methods: {
    /** Check validation before submit editing */
    checkEditedRecord () {
      if (this.$v.$invalid) {
        return this.$v.$touch()
      } else this.saveEditedRecord()
    },

    /** Save edited record */
    saveEditedRecord () {
      this.buttonLoader = true
      const body = {
        change_date: this.sailorDocument.change_date,
        last_name_ukr: this.sailorDocument.last_name_ukr,
        last_name_eng: this.sailorDocument.last_name_eng,
        first_name_ukr: this.sailorDocument.first_name_ukr,
        first_name_eng: this.sailorDocument.first_name_eng
      }
      if (this.sailorDocument.middle_name_ukr) body.middle_name_ukr = this.sailorDocument.middle_name_ukr
      if (this.sailorDocument.middle_name_eng) body.middle_name_eng = this.sailorDocument.middle_name_eng

      this.$api.patch(`api/v2/sailor/${this.id}/old_name/${this.sailorDocument.id}/`, body).then(response => {
        this.buttonLoader = false
        switch (response.status) {
          case 'success':
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
            break
          case 'error':
            if (response.data[0] === 'less date exists') {
              this.$notification.error(this, this.$i18n.t('notLastDate')) // less "change date" is already exist
            }
            break
        }
      })
    }
  }
}
