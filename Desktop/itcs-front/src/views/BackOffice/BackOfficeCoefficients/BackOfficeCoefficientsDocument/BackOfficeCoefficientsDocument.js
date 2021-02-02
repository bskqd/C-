import BackOfficeCoefficientsInfo from '@/views/BackOffice/BackOfficeCoefficients//BackOfficeCoefficientsInfo/BackOfficeCoefficientsInfo.vue'
import BackOfficeCoefficientsEdit from '@/views/BackOffice/BackOfficeCoefficients/BackOfficeCoefficientsEdit/BackOfficeCoefficientsEdit.vue'
import { back, deleteConfirmation, viewDetailedComponent } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'BackOfficeCoefficientsDocument',
  components: {
    BackOfficeCoefficientsInfo,
    BackOfficeCoefficientsEdit
  },
  data () {
    return {
      type: 'backOfficeCoefficient',
      viewDetailedComponent,
      deleteConfirmation,
      checkAccess,
      back
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr'
    }),
    documentID () {
      return this.$route.params.documentID
    },
    sailorDocument () {
      return this.$store.getters.sailorDocumentByID({ type: 'backOfficeCoefficient', id: Number(this.documentID) }) || {}
    }
  },
  methods: {
    deleteDocument () {
      deleteConfirmation(this).then(confirmation => {
        if (confirmation) {
          this.$api.delete(`api/v1/back_off/eti_profit_part/${this.sailorDocument.id}/`).then(response => {
            if (response.code === 204) {
              this.$notification.success(this, this.$i18n.t('coefficientDelete'))
              this.$store.commit('deleteDataSailor', { type: 'backOfficeCoefficient', value: this.sailorDocument })
              back('coefficients-backoffice')
            }
          })
        }
      })
    }
  }
}
