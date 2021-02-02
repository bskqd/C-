import SailorEducationStatementInfo from '@/views/Sailor/SailorEducationStatement/SailorEducationStatementInfo/SailorEducationStatementInfo.vue'
import SailorEducationStatementEdit from '@/views/Sailor/SailorEducationStatement/SailorEducationStatementEdit/SailorEducationStatementEdit.vue'
import SailorEducationStatementEditStatus from '@/views/Sailor/SailorEducationStatement/SailorEducationStatementEditStatus/SailorEducationStatementEditStatus.vue'
import SailorEducationStatementTransfer from '@/views/Sailor/SailorEducationStatement/SailorEducationStatementTransfer/SailorEducationStatementTransfer.vue'
import ViewPhotoList from '@/components/atoms/ViewPhotoList.vue'
import { viewDetailedComponent, back, deleteConfirmation } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorEducationStatementDocument',
  components: {
    SailorEducationStatementInfo,
    SailorEducationStatementEdit,
    SailorEducationStatementEditStatus,
    SailorEducationStatementTransfer,
    ViewPhotoList
  },
  data () {
    return {
      type: 'educationStatement',
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
      return this.$store.getters.sailorDocumentByID({ type: 'educationStatement', id: Number(this.documentID) }) || {}
    }
  },
  methods: {
    deleteDocument () {
      deleteConfirmation(this).then(confirmation => {
        if (confirmation) {
          this.$api.delete(`api/v2/sailor/${this.id}/statement/advanced_training/${this.sailorDocument.id}/`).then(response => {
            if (response.code === 200 || response.code === 204) {
              this.$notification.success(this, this.$i18n.t('deletedDocument'))
              if (this.sailorDocument.status_document.id !== 86) {
                this.$store.commit('updateDataSailor', { type: 'educationStatement', value: response.data })
                this.$store.commit('decrementBadgeCount', {
                  child: 'educationStatement',
                  parent: 'educationAll'
                })
              } else {
                this.$store.commit('deleteDataSailor', { type: 'educationStatement', value: this.sailorDocument })
              }
              back('education-statements')
            } else {
              if (response.data[0] === 'Statement related to advanced training') {
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
