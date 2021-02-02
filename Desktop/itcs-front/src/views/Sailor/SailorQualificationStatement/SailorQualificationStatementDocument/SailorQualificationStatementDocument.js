import SailorQualificationStatementInfo from '@/views/Sailor/SailorQualificationStatement/SailorQualificationStatementInfo/SailorQualificationStatementInfo.vue'
import SailorQualificationStatementEdit from '@/views/Sailor/SailorQualificationStatement/SailorQualificationStatementEdit/SailorQualificationStatementEdit.vue'
import SailorQualificationStatementEditStatus from '@/views/Sailor/SailorQualificationStatement/SailorQualificationStatementEditStatus/SailorQualificationStatementEditStatus.vue'
import ViewPhotoList from '@/components/atoms/ViewPhotoList.vue'
import { viewDetailedComponent, back, deleteConfirmation } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorQualificationStatementDocument',
  components: {
    SailorQualificationStatementInfo,
    SailorQualificationStatementEdit,
    SailorQualificationStatementEditStatus,
    ViewPhotoList
  },
  data () {
    return {
      type: 'qualificationStatement',
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
      return this.$store.getters.sailorDocumentByID({ type: 'qualificationStatement', id: Number(this.documentID) }) || {}
    }
  },
  methods: {
    deleteDocument () {
      deleteConfirmation(this).then(confirmation => {
        if (confirmation) {
          this.$api.delete(`api/v2/sailor/${this.id}/statement/qualification/${this.sailorDocument.id}/`).then(response => {
            if (response.code === 200 || response.code === 204) {
              this.$notification.success(this, this.$i18n.t('deletedDocument'))
              this.$store.commit('deleteDataSailor', { type: 'successQualificationStatement', value: this.sailorDocument })
              if (this.sailorDocument.status_document.id !== 86) {
                this.$store.commit('updateDataSailor', { type: 'qualificationStatement', value: response.data })
                this.$store.commit('decrementBadgeCount', {
                  child: 'qualificationStatement',
                  parent: 'qualificationAll'
                })
              } else {
                this.$store.commit('deleteDataSailor', { type: 'qualificationStatement', value: this.sailorDocument })
              }
              back('qualification-statements')
            } else {
              this.$notification.error(this, this.$i18n.t('cantDeleteDoc'))
            }
          })
        }
      })
    }
  }
}
