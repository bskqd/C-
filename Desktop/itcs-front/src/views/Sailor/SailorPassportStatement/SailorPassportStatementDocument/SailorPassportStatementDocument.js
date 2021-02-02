import SailorPassportStatementInfo from '@/views/Sailor/SailorPassportStatement/SailorPassportStatementInfo/SailorPassportStatementInfo.vue'
import SailorPassportStatementEditStatus from '@/views/Sailor/SailorPassportStatement/SailorPassportStatementEditStatus/SailorPassportStatementEditStatus.vue'
import ViewPhotoList from '@/components/atoms/ViewPhotoList.vue'
import { viewDetailedComponent, back, deleteConfirmation } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorPassportStatementDocument',
  components: {
    SailorPassportStatementInfo,
    SailorPassportStatementEditStatus,
    ViewPhotoList
  },
  data () {
    return {
      type: 'sailorPassportStatement',
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
      return this.$store.getters.sailorDocumentByID({ type: 'sailorPassportStatement', id: Number(this.documentID) }) || {}
    }
  },
  methods: {
    deleteDocument () {
      deleteConfirmation(this).then(confirmation => {
        if (confirmation) {
          this.$api.delete(`api/v2/sailor/${this.id}/statement/sailor_passport/${this.sailorDocument.id}/`).then(response => {
            if (response.code === 204 || response.code === 200) {
              this.$notification.success(this, this.$i18n.t('deletedDocument'))
              if (this.sailorDocument.status_document.id !== 86) {
                this.$store.commit('updateDataSailor', { type: 'sailorPassportStatement', value: response.data })
                this.$store.commit('decrementBadgeCount', {
                  child: 'passportStatement',
                  parent: 'passportAll'
                })
              } else {
                this.$store.commit('deleteDataSailor', { type: 'sailorPassportStatement', value: this.sailorDocument })
              }
              back('passports-statements')
            } else {
              this.$notification.error(this, this.$i18n.t('cantDeleteDoc'))
            }
          })
        }
      })
    }
  }
}
