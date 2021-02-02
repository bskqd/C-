import SailorEducationInfo from '@/views/Sailor/SailorEducation/SailorEducationInfo/SailorEducationInfo.vue'
import SailorEducationEdit from '@/views/Sailor/SailorEducation/SailorEducationEdit/SailorEducationEdit.vue'
import SailorEducationEditStatus from '@/views/Sailor/SailorEducation/SailorEducationEditStatus/SailorEducationEditStatus.vue'
import ViewPhotoList from '@/components/atoms/ViewPhotoList.vue'
import VerificationSteps from '@/components/atoms/VerificationSteps/VerificationSteps.vue'
import { viewDetailedComponent, back, deleteConfirmation } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorEducationDocument',
  components: {
    SailorEducationInfo,
    SailorEducationEdit,
    SailorEducationEditStatus,
    ViewPhotoList,
    VerificationSteps
  },
  data () {
    return {
      type: 'education',
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
      return this.$store.getters.sailorDocumentByID({ type: 'education', id: Number(this.documentID) }) || {}
    }
  },
  methods: {
    deleteDocument () {
      deleteConfirmation(this).then(confirmation => {
        if (confirmation) {
          this.$api.delete(`api/v2/sailor/${this.id}/education/${this.sailorDocument.id}/`).then(response => {
            if (response.code === 200 || response.code === 204) {
              this.$notification.success(this, this.$i18n.t('deletedDocument'))
              if (this.sailorDocument.status_document.id !== 86) {
                this.$store.commit('updateDataSailor', { type: 'education', value: response.data })
                this.$store.commit('decrementBadgeCount', {
                  child: 'educationDocument',
                  parent: 'educationAll'
                })
              } else {
                this.$store.commit('deleteDataSailor', { type: 'education', value: this.sailorDocument })
              }
              back('education-documents')
            } else {
              this.$notification.error(this, this.$i18n.t('cantDeleteDoc'))
            }
          })
        }
      })
    }
  }
}
