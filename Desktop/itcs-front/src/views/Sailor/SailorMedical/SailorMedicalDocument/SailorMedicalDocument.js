import SailorMedicalInfo from '@/views/Sailor/SailorMedical/SailorMedicalInfo/SailorMedicalInfo.vue'
import SailorMedicalEdit from '@/views/Sailor/SailorMedical/SailorMedicalEdit/SailorMedicalEdit.vue'
import SailorMedicalEditStatus from '@/views/Sailor/SailorMedical/SailorMedicalEditStatus/SailorMedicalEditStatus.vue'
import ViewPhotoList from '@/components/atoms/ViewPhotoList.vue'
import VerificationSteps from '@/components/atoms/VerificationSteps/VerificationSteps.vue'
import { viewDetailedComponent, back, deleteConfirmation } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorMedicalDocument',
  components: {
    SailorMedicalInfo,
    SailorMedicalEdit,
    SailorMedicalEditStatus,
    ViewPhotoList,
    VerificationSteps
  },
  data () {
    return {
      type: 'sailorMedical',
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
      return this.$store.getters.sailorDocumentByID({ type: 'sailorMedical', id: Number(this.documentID) }) || {}
    }
  },
  methods: {
    deleteDocument () {
      deleteConfirmation(this).then(confirmation => {
        if (confirmation) {
          this.$api.delete(`api/v2/sailor/${this.id}/medical/${this.sailorDocument.id}/`).then(response => {
            if (response.code === 200 || response.code === 204) {
              this.$notification.success(this, this.$i18n.t('deletedDocument'))
              if (this.sailorDocument.status_document.id !== 86) {
                this.$store.commit('updateDataSailor', { type: 'sailorMedical', value: response.data })
                this.$store.commit('decrementBadgeCount', {
                  child: 'medicalDocument',
                  parent: 'medicalAll'
                })
              } else {
                this.$store.commit('deleteDataSailor', { type: 'sailorMedical', value: this.sailorDocument })
              }
              back('medical-certificates')
            } else {
              this.$notification.error(this, this.$i18n.t('cantDeleteDoc'))
            }
          })
        }
      })
    }
  }
}
