import SailorSQCStatementInfo from '@/views/Sailor/SailorSQCStatement/SailorSQCStatementInfo/SailorSQCStatementInfo.vue'
import SailorSQCStatementEdit from '@/views/Sailor/SailorSQCStatement/SailorSQCStatementEdit/SailorSQCStatementEdit.vue'
import SailorSQCStatementEditStatus from '@/views/Sailor/SailorSQCStatement/SailorSQCStatementEditStatus/SailorSQCStatementEditStatus.vue'
import ViewPhotoList from '@/components/atoms/ViewPhotoList.vue'
import { viewDetailedComponent, back, deleteConfirmation } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorSQCStatementDocument',
  components: {
    SailorSQCStatementInfo,
    SailorSQCStatementEdit,
    SailorSQCStatementEditStatus,
    ViewPhotoList
  },
  data () {
    return {
      type: 'sailorSQCStatement',
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
      return this.$store.getters.sailorDocumentByID({ type: 'sailorSQCStatement', id: Number(this.documentID) }) || {}
    }
  },
  methods: {
    deleteDocument () {
      deleteConfirmation(this).then(confirmation => {
        if (confirmation) {
          this.$api.delete(`api/v2/sailor/${this.id}/statement/protocol_sqc/${this.sailorDocument.id}/`).then(response => {
            if (response.code === 200 || response.code === 204) {
              this.$notification.success(this, this.$i18n.t('deletedDocument'))
              if (this.sailorDocument.status_document.id !== 86) {
                this.$store.commit('updateDataSailor', { type: 'sailorSQCStatement', value: response.data })
                this.$store.commit('decrementBadgeCount', {
                  child: 'sqcStatement',
                  parent: 'sqcAll'
                })
              } else {
                this.$store.commit('deleteDataSailor', { type: 'sailorSQCStatement', value: this.sailorDocument })
              }
              this.$store.commit('deleteDataSailor', { type: 'successStatement', value: this.sailorDocument })
              back('sqc-statements')
            } else {
              if (response.data[0] === 'Statement related to protocol dkk') {
                this.$notification.error(this, this.$i18n.t('relatedStatement'))
              } else if (response.data[0] === 'This protocol has a statement qual doc') {
                this.$notification.error(this, this.$i18n.t('associatedWithProtocol'))
              } else if (response.data[0] === 'Statement can only be deleted with the packet') {
                this.$notification.error(this, this.$i18n.t('deleteOnlyWithPackage'))
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
