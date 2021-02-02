import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { hideDetailed } from '@/mixins/main'
import { maxLength, required } from 'vuelidate/lib/validators'
import { mapState } from 'vuex'

export default {
  name: 'SeafarerGraduationApplicationTransfer',
  props: {
    sailorDocument: Object
  },
  components: {
    ValidationAlert
  },
  data () {
    return {
      number: null,
      serial: null,
      registryNumber: null,
      notes: null,
      buttonLoader: false,
      hideDetailed
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId
    })
  },
  validations: {
    number: { required, maxLength: maxLength(30) },
    serial: { required },
    registryNumber: { required }
  },
  methods: {
    /** Check fields validation before submit */
    checkInfo () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.transferApplication()
    },

    /** Transfer application to document */
    transferApplication () {
      this.buttonLoader = true
      const body = {
        number_document: this.number,
        serial: this.serial,
        registry_number: this.registryNumber,
        special_notes: this.notes
      }
      this.$api.post(`api/v2/sailor/${this.id}/statement/advanced_training/${this.sailorDocument.id}/create_advanced_training/`, body)
        .then(response => {
          this.buttonLoader = false
          if (response.status === 'success') {
            this.$notification.success(this, this.$i18n.t('transferredApplication'))
            this.$store.dispatch('getEducationDocs', this.id)
            this.$store.commit('incrementBadgeCount', {
              child: 'educationDocument',
              parent: 'educationAll'
            })
          } else {
            if (response.data[0] === 'Statement used') {
              this.$notification.error(this, this.$i18n.t('applicationInUse'))
            }
          }
        })
    }
  }
}
