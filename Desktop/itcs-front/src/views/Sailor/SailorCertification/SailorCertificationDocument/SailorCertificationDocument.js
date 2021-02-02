import SailorCertificationInfo from '@/views/Sailor/SailorCertification/SailorCertificationInfo/SailorCertificationInfo.vue'
import SailorCertificationEdit from '@/views/Sailor/SailorCertification/SailorCertificationEdit/SailorCertificationEdit.vue'
import SailorCertificationEditStatus from '@/views/Sailor/SailorCertification/SailorCertificationEditStatus/SailorCertificationEditStatus.vue'
import { viewDetailedComponent, back, deleteConfirmation } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorCertificationDocument',
  components: {
    SailorCertificationInfo,
    SailorCertificationEdit,
    SailorCertificationEditStatus
  },
  data () {
    return {
      type: 'certification',
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
      return this.$store.getters.sailorDocumentByID({ type: 'certification', id: Number(this.documentID) }) || {}
    }
  },
  methods: {
    deleteDocument () {
      deleteConfirmation(this).then(confirmation => {
        if (confirmation) {
          this.$api.delete(`api/v2/sailor/${this.id}/certificate/${this.sailorDocument.id}`).then(response => {
            if (response.code === 200 || response.code === 204) {
              this.$notification.success(this, this.$i18n.t('deletedDocument'))
              if (this.sailorDocument.status_document.id !== 86) {
                this.$store.commit('updateDataSailor', { type: 'certification', value: response.data })
                this.$store.commit('decrementBadgeCount', {
                  child: 'certificateDocument',
                  parent: 'certificateAll'
                })
              } else {
                this.$store.commit('deleteDataSailor', { type: 'certification', value: this.sailorDocument })
              }
              back('certification-certificates')
            } else {
              this.$notification.error(this, this.$i18n.t('cantDeleteDoc'))
            }
          })
        }
      })
    }
  }
}
