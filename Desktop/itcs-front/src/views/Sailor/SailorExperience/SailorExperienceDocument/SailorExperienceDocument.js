import SailorExperienceInfo from '@/views/Sailor/SailorExperience/SailorExperienceInfo/SailorExperienceInfo.vue'
import SailorExperienceEdit from '@/views/Sailor/SailorExperience/SailorExperienceEdit/SailorExperienceEdit.vue'
import SailorExperienceEditStatus from '@/views/Sailor/SailorExperience/SailorExperienceEditStatus/SailorExperienceEditStatus.vue'
import VerificationSteps from '@/components/atoms/VerificationSteps/VerificationSteps.vue'
import ViewPhotoList from '@/components/atoms/ViewPhotoList.vue'
import { viewDetailedComponent, back, deleteConfirmation } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorExperienceDocument',
  components: {
    SailorExperienceInfo,
    SailorExperienceEdit,
    SailorExperienceEditStatus,
    ViewPhotoList,
    VerificationSteps
  },
  data () {
    return {
      type: 'experience',
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
      return this.$store.getters.sailorDocumentByID({ type: 'experience', id: Number(this.documentID) }) || {}
    }
  },
  methods: {
    deleteDocument () {
      deleteConfirmation(this).then(confirmation => {
        if (confirmation) {
          this.$api.delete(`api/v2/sailor/${this.id}/experience_certificate/${this.sailorDocument.id}/`).then(response => {
            if (response.code === 200 || response.code === 204) {
              this.$notification.success(this, this.$i18n.t('deletedDocument'))
              if (this.sailorDocument.status_line.id !== 86) {
                this.$store.commit('updateDataSailor', { type: 'experience', value: response.data })
                this.$store.commit('decrementBadgeCount', {
                  child: 'experienceDocument',
                  parent: 'experienceAll'
                })
              } else {
                this.$store.commit('deleteDataSailor', { type: 'experience', value: this.sailorDocument })
              }
              back('experience-reference')
            } else {
              this.$notification.error(this, this.$i18n.t('cantDeleteDoc'))
            }
          })
        }
      })
    }
  }
}
