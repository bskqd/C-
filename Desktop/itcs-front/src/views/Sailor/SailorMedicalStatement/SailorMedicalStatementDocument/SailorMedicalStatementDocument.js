import SailorMedicalStatementInfo from '@/views/Sailor/SailorMedicalStatement/SailorMedicalStatementInfo/SailorMedicalStatementInfo.vue'
import SailorMedicalStatementEdit from '@/views/Sailor/SailorMedicalStatement/SailorMedicalStatementEdit/SailorMedicalStatementEdit.vue'
import SailorMedicalStatementEditStatus from '@/views/Sailor/SailorMedicalStatement/SailorMedicalStatementEditStatus/SailorMedicalStatementEditStatus.vue'
import SailorMedicalStatementTransfer from '@/views/Sailor/SailorMedicalStatement/SailorMedicalStatementTransfer/SailorMedicalStatementTransfer.vue'
import ViewPhotoList from '@/components/atoms/ViewPhotoList.vue'
import { viewDetailedComponent, back, deleteConfirmation } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorMedicalStatementDocument',
  components: {
    SailorMedicalStatementInfo,
    SailorMedicalStatementEdit,
    SailorMedicalStatementEditStatus,
    SailorMedicalStatementTransfer,
    ViewPhotoList
  },
  data () {
    return {
      type: 'medicalStatement',
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
      return this.$store.getters.sailorDocumentByID({ type: 'medicalStatement', id: Number(this.documentID) }) || {}
    }
  },
  methods: {
    deleteDocument () {
      deleteConfirmation(this).then(confirmation => {
        if (confirmation) {
          this.$api.delete(`api/v2/sailor/${this.id}/statement/medical_certificate/${this.sailorDocument.id}/`).then(response => {
            if (response.code === 200 || response.code === 204) {
              this.$notification.success(this, this.$i18n.t('deletedDocument'))
              if (this.sailorDocument.status_document.id !== 86) {
                this.$store.commit('updateDataSailor', { type: 'medicalStatement', value: response.data })
                this.$store.commit('decrementBadgeCount', {
                  child: 'medicalApplication',
                  parent: 'medicalAll'
                })
              } else {
                this.$store.commit('deleteDataSailor', { type: 'medicalStatement', value: this.sailorDocument })
              }
              back('medical-statements')
            } else {
              if (response.data[0] === 'Statement related to medical certificate') {
                this.$notification.error(this, this.$i18n.t('relatedToDocument'))
              } else if (response.data[0] === 'Statement used') {
                this.$notification.error(this, this.$i18n.t('applicationInUse'))
              } else {
                this.$notification.error(this, this.$i18n.t('cantDeleteDoc'))
              }
            }
          })
        }
      })
    }
  }
}
