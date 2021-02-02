import SailorSQCProtocolsInfo from '@/views/Sailor/SailorSQCProtocols/SailorSQCProtocolsInfo/SailorSQCProtocolsInfo.vue'
import SailorSQCProtocolsEdit from '@/views/Sailor/SailorSQCProtocols/SailorSQCProtocolsEdit/SailorSQCProtocolsEdit.vue'
import SailorSQCProtocolsEditStatus from '@/views/Sailor/SailorSQCProtocols/SailorSQCProtocolsEditStatus/SailorSQCProtocolsEditStatus.vue'
import ViewPhotoList from '@/components/atoms/ViewPhotoList.vue'
import { viewDetailedComponent, back, deleteConfirmation } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorSQCProtocolsDocument',
  components: {
    SailorSQCProtocolsInfo,
    SailorSQCProtocolsEdit,
    SailorSQCProtocolsEditStatus,
    ViewPhotoList
  },
  data () {
    return {
      type: 'sailorSQCProtocols',
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
      return this.$store.getters.sailorDocumentByID({ type: 'sailorSQCProtocols', id: Number(this.documentID) }) || {}
    }
  },
  methods: {
    deleteDocument () {
      deleteConfirmation(this).then(confirmation => {
        if (confirmation) {
          this.$api.delete(`api/v2/sailor/${this.id}/protocol_sqc/${this.sailorDocument.id}/`).then(response => {
            if (response.code === 200 || response.code === 204) {
              this.$notification.success(this, this.$i18n.t('deletedDocument'))
              if (this.sailorDocument.status_document.id !== 86) {
                this.$store.commit('updateDataSailor', { type: 'sailorSQCProtocols', value: response.data })
                this.$store.commit('decrementBadgeCount', {
                  child: 'sqcDocument',
                  parent: 'sqcAll'
                })
              } else {
                this.$store.commit('deleteDataSailor', { type: 'sailorSQCProtocols', value: this.sailorDocument })
              }
              back('sqc-protocols')
            } else {
              if (response.data[0] === 'This protocol has a statement qual doc') {
                this.$notification.error(this, this.$i18n.t('associatedWithProtocol'))
              } else if (response.data[0] === 'Document can only be deleted with the packet') {
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
