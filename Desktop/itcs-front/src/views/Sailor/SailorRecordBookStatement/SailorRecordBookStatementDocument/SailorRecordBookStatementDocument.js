import SailorRecordBookStatementInfo from '@/views/Sailor/SailorRecordBookStatement/SailorRecordBookStatementInfo/SailorRecordBookStatementInfo.vue'
import SailorRecordBookStatementEdit from '@/views/Sailor/SailorRecordBookStatement/SailorRecordBookStatementEdit/SailorRecordBookStatementEdit.vue'
import SailorRecordBookStatementUploadFiles from '@/views/Sailor/SailorRecordBookStatement/SailorRecordBookStatementUploadFiles/SailorRecordBookStatementUploadFiles.vue'
import ViewPhotoList from '@/components/atoms/ViewPhotoList.vue'
import { viewDetailedComponent, back, deleteConfirmation } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorRecordBookStatementDocument',
  components: {
    SailorRecordBookStatementInfo,
    SailorRecordBookStatementEdit,
    SailorRecordBookStatementUploadFiles,
    ViewPhotoList
  },
  data () {
    return {
      type: 'recordBookStatement',
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
      return this.$store.getters.sailorDocumentByID({ type: 'recordBookStatement', id: Number(this.documentID) }) || {}
    }
  },
  methods: {
    deleteDocument () {
      deleteConfirmation(this).then(confirmation => {
        if (confirmation) {
          this.$api.delete(`api/v2/sailor/${this.id}/statement/service_record/${this.sailorDocument.id}/`).then(response => {
            if (response.code === 200 || response.code === 204) {
              this.$notification.success(this, this.$i18n.t('deletedDocument'))
              if (this.sailorDocument.status_document.id !== 86) {
                this.$store.commit('updateDataSailor', { type: 'recordBookStatement', value: response.data })
                this.$store.commit('decrementBadgeCount', {
                  child: 'recordBookStatement',
                  parent: 'experienceAll'
                })
              } else {
                this.$store.commit('deleteDataSailor', { type: 'recordBookStatement', value: this.sailorDocument })
              }
              this.$store.commit('decrementUserNotification', 'statement_service_record')
              back('experience-statements')
            } else {
              this.$notification.error(this, this.$i18n.t('cantDeleteDoc'))
            }
          })
        }
      })
    }
  }
}
