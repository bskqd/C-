import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { maxValue, minValue, required } from 'vuelidate/lib/validators'
import { mapState } from 'vuex'

export default {
  name: 'SailorSQCProtocolsEdit',
  props: {
    sailorDocument: Object
  },
  components: {
    ValidationAlert
  },
  data () {
    return {
      buttonLoader: false
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      commissionMembers: state => state.directory.allCommissioners
    })
  },
  validations () {
    return {
      sailorDocument: {
        number: { required },
        headCommission: { required },
        secretaryCommission: { required },
        membersCommission: {
          length: {
            maxValue: maxValue(4),
            minValue: minValue(2)
          }
        }
      }
    }
  },
  methods: {
    /** Check validation before edit document */
    checkEditedProtocol () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.saveEditInfo()
    },

    /** Save edited information */
    saveEditInfo () {
      this.buttonLoader = true

      let membersCommission = this.sailorDocument.membersCommission.map(value => {
        return { signer: value.signer, commissioner_type: 'CH' }
      })
      membersCommission.push({ signer: this.sailorDocument.headCommission.signer, commissioner_type: 'HD' })
      membersCommission.push({ signer: this.sailorDocument.secretaryCommission.signer, commissioner_type: 'SC' })

      const body = {
        number: this.sailorDocument.number,
        commissioner_sign: membersCommission
      }
      this.$api.patch(`api/v2/sailor/${this.id}/protocol_sqc/${this.sailorDocument.id}/`, body).then(response => {
        this.buttonLoader = false
        if (response.status === 'success') {
          this.$notification.success(this, this.$i18n.t('editProtocolSQC'))
          this.$store.commit('updateDataSailor', { type: 'sailorSQCProtocols', value: response.data })
        }
      })
    }
  }
}
