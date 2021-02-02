import SailorPassportInfo from '@/views/Sailor/SailorPassport/SailorPassportInfo/SailorPassportInfo.vue'
import SailorPassportEdit from '@/views/Sailor/SailorPassport/SailorPassportEdit/SailorPassportEdit.vue'
import SailorPassportEditStatus from '@/views/Sailor/SailorPassport/SailorPassportEditStatus/SailorPassportEditStatus.vue'
import VerificationSteps from '@/components/atoms/VerificationSteps/VerificationSteps.vue'
import ViewPhotoList from '@/components/atoms/ViewPhotoList.vue'
import { viewDetailedComponent, back, deleteConfirmation } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorPassportDocument',
  components: {
    SailorPassportInfo,
    SailorPassportEdit,
    SailorPassportEditStatus,
    ViewPhotoList,
    VerificationSteps
  },
  data () {
    return {
      type: 'sailorPassport',
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
      return this.$store.getters.sailorDocumentByID({ type: 'sailorPassport', id: Number(this.documentID) }) || {}
    }
  },
  methods: {
    deleteDocument () {
      deleteConfirmation(this).then(confirmation => {
        if (confirmation) {
          this.$api.delete(`api/v2/sailor/${this.id}/sailor_passport/${this.sailorDocument.id}/`).then(response => {
            if (response.code === 204 || response.code === 200) {
              this.$notification.success(this, this.$i18n.t('deletedDocument'))
              if (this.sailorDocument.status_document.id !== 86) {
                this.$store.commit('updateDataSailor', { type: 'sailorPassport', value: response.data })
                this.$store.commit('decrementBadgeCount', {
                  child: 'passportDocument',
                  parent: 'passportAll'
                })
              } else {
                this.$store.commit('deleteDataSailor', { type: 'sailorPassport', value: this.sailorDocument })
              }
              back('passports-sailors')
            } else {
              this.$notification.error(this, this.$i18n.t('cantDeleteDoc'))
            }
          })
        }
      })
    }
  }
}
