import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { hideDetailed } from '@/mixins/main'
import { required, maxLength, minLength, helpers } from 'vuelidate/lib/validators'
const phoneNumber = helpers.regex('numeric', /^[+0-9]*$/)

export default {
  name: 'NewAgentsEdit',
  components: {
    ValidationAlert
  },
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      phoneNumber: null,
      telegram: null,
      viber: null,
      buttonLoader: false,
      hideDetailed
    }
  },
  validations: {
    sailorDocument: {
      serial_passport: { required },
      tax_number: { required, maxLength: maxLength(10), minLength: minLength(10) }
    },
    phoneNumber: { required, maxLength: maxLength(13), minLength: minLength(13), phoneNumber },
    telegram: { maxLength: maxLength(13), minLength: minLength(13), phoneNumber },
    viber: { maxLength: maxLength(13), minLength: minLength(13), phoneNumber }
  },
  mounted () {
    this.setContactData()
  },
  methods: {
    /** Set contact models depends on value type */
    setContactData () {
      if (this.sailorDocument.contact_info && this.sailorDocument.contact_info.length) {
        for (const contact of this.sailorDocument.contact_info) {
          switch (contact.type_contact) {
            case 'telegram':
              this.telegram = contact.value.replace(/[()\-\s]/g, '')
              break
            case 'viber':
              this.viber = contact.value.replace(/[()\-\s]/g, '')
              break
            case 'phone_number':
              this.phoneNumber = contact.value.replace(/[()\-\s]/g, '')
              break
          }
        }
      }
    },

    /** Check field entries before submit */
    validationCheck () {
      if (this.$v.$invalid) {
        return this.$v.$touch()
      } else this.editAgentApplication()
    },

    /** Edit agent application */
    editAgentApplication () {
      this.buttonLoader = true
      const body = {
        tax_number: this.sailorDocument.tax_number,
        serial_passport: this.sailorDocument.serial_passport,
        contact_info: [
          { type_contact: 'telegram', value: this.telegram },
          { type_contact: 'viber', value: this.viber },
          { type_contact: 'phone_number', value: this.phoneNumber }
        ]
      }
      this.$api.patch(`api/v1/seaman/statement_seaman/${this.sailorDocument.id}/`, body).then(response => {
        this.buttonLoader = false
        switch (response.status) {
          case 'success':
            this.$notification.success(this, this.$i18n.t('agentStatementEdited'))
            this.$store.commit('updateDataSailor', { type: 'newAgents', value: response.data })
            break
          case 'error':
            if (response.data.contact_info[0] === 'email is used') {
              this.$notification.error(this, this.$i18n.t('useAnotherEmail'))
            }
            break
        }
      })
    }
  }
}
