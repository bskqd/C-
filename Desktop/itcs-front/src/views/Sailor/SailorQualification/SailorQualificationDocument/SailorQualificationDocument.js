import SailorQualificationInfo from '@/views/Sailor/SailorQualification/SailorQualificationInfo/SailorQualificationInfo.vue'
import SailorQualificationEdit from '@/views/Sailor/SailorQualification/SailorQualificationEdit/SailorQualificationEdit.vue'
import SailorQualificationEditStatus from '@/views/Sailor/SailorQualification/SailorQualificationEditStatus/SailorQualificationEditStatus.vue'
import VerificationSteps from '@/components/atoms/VerificationSteps/VerificationSteps.vue'
import ViewPhotoList from '@/components/atoms/ViewPhotoList.vue'
import { viewDetailedComponent, back, deleteConfirmation } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorQualificationDocument',
  components: {
    SailorQualificationInfo,
    SailorQualificationEdit,
    SailorQualificationEditStatus,
    VerificationSteps,
    ViewPhotoList
  },
  data () {
    return {
      type: 'qualification',
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
      return this.$store.getters.sailorDocumentByID({ type: 'qualification', id: Number(this.documentID) }) || {}
    }
  },
  methods: {
    deleteDocument () {
      deleteConfirmation(this).then(confirmation => {
        if (confirmation) {
          const url = `api/v2/sailor/${this.id}/${this.sailorDocument.type_document.id === 16 ? 'proof_diploma' : 'qualification'}/${this.sailorDocument.id}/`
          this.$api.delete(url).then(response => {
            if (response.code === 200 || response.code === 204) {
              if (this.sailorDocument.status_document.id !== 86) {
                this.$store.commit('updateDataSailor', { type: 'qualification', value: response.data })
                this.$store.commit('decrementBadgeCount', {
                  child: 'qualificationDocument',
                  parent: 'qualificationAll'
                })
              } else {
                this.$store.commit('deleteDataSailor', { type: 'qualification', value: this.sailorDocument })
              }
              this.$notification.success(this, this.$i18n.t('deletedDocument'))
              this.$store.dispatch('getDiplomas', this.id)
              back('qualification-documents')
            } else {
              this.$notification.error(this, this.$i18n.t('cantDeleteDoc'))
            }
          })
        }
      })
    }
  }
}
