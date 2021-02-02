import SailorCertificationStatementInfo from '@/views/Sailor/SailorCertificationStatement/SailorCertificationStatementInfo/SailorCertificationStatementInfo.vue'
import SailorCertificationStatementEdit from '@/views/Sailor/SailorCertificationStatement/SailorCertificationStatementEdit/SailorCertificationStatementEdit.vue'
import SailorCertificationStatementEditStatus from '@/views/Sailor/SailorCertificationStatement/SailorCertificationStatementEditStatus/SailorCertificationStatementEditStatus.vue'
import { viewDetailedComponent, back, deleteConfirmation } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorCertificationStatement',
  components: {
    SailorCertificationStatementInfo,
    SailorCertificationStatementEdit,
    SailorCertificationStatementEditStatus
  },
  data () {
    return {
      sendToInspection: true,
      type: 'certificationStatement',
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
      return this.$store.getters.sailorDocumentByID({ type: 'certificationStatement', id: Number(this.documentID) }) || {}
    }
  },
  methods: {
    mailInspection () {
      this.$api.post(`api/v2/sailor/${this.id}/statement/certificate/${this.sailorDocument.id}/send_to_eti/`)
        .then(response => {
          if (response.code === 200) {
            this.$notification.success(this, this.$i18n.t('sendToInspection'))
            this.sendToInspection = false
          }
        })
    },

    deleteDocument () {
      deleteConfirmation(this).then(confirmation => {
        if (confirmation) {
          this.$api.delete(`api/v2/sailor/${this.id}/statement/certificate/${this.sailorDocument.id}/`).then(response => {
            if (response.code === 200 || response.code === 204) {
              this.$notification.success(this, this.$i18n.t('deletedDocument'))
              if (this.sailorDocument.status_document.id !== 86) {
                this.$store.commit('updateDataSailor', { type: 'certificationStatement', value: response.data })
                this.$store.commit('decrementBadgeCount', {
                  child: 'certificateStatement',
                  parent: 'certificateAll'
                })
              } else {
                this.$store.commit('deleteDataSailor', { type: 'certificationStatement', value: this.sailorDocument })
              }
              back('certification-statements')
            } else {
              if (response.data[0] === 'Statement can only be deleted with the packet') {
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
