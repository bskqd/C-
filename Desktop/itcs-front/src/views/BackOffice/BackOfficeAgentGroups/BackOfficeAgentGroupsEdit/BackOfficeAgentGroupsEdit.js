import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { hideDetailed } from '@/mixins/main'
import { required } from 'vuelidate/lib/validators'

export default {
  name: 'BackOfficeAgentGroupsEdit',
  components: {
    ValidationAlert
  },
  props: {
    row: Object,
    getDocuments: Function
  },
  data () {
    return {
      agentGroupName: this.row.item.name_ukr,
      buttonLoader: false,
      hideDetailed
    }
  },
  validations: {
    agentGroupName: { required }
  },
  methods: {
    /** Check fields entries validation */
    validationCheck () {
      if (this.$v.$invalid) {
        return this.$v.$touch()
      } else this.editAgentGroup()
    },

    /** Edit agent's group */
    editAgentGroup () {
      this.buttonLoader = true
      const body = {
        name_ukr: this.agentGroupName
      }
      this.$api.patch(`api/v1/seaman/seaman_groups/${this.row.item.id}/`, body).then(response => {
        this.buttonLoader = false
        if (response.status === 'success') {
          this.$notification.success(this, this.$i18n.t('editedAgentGroup'))
          this.getDocuments()
        }
      })
    }
  }
}
