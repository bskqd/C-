import SailorRecordBookInfo from '@/views/Sailor/SailorRecordBook/SailorRecordBookInfo/SailorRecordBookInfo.vue'
import SailorRecordBookEdit from '@/views/Sailor/SailorRecordBook/SailorRecordBookEdit/SailorRecordBookEdit.vue'
import SailorRecordBookEditStatus from '@/views/Sailor/SailorRecordBook/SailorRecordBookEditStatus/SailorRecordBookEditStatus.vue'
import SailorRecordBookLineAdd from '@/views/Sailor/SailorRecordBook/SailorRecordBookLine/SailorRecordBookLineAdd/SailorRecordBookLineAdd.vue'
import VerificationSteps from '@/components/atoms/VerificationSteps/VerificationSteps.vue'
import ViewPhotoList from '@/components/atoms/ViewPhotoList.vue'
import { viewDetailedComponent, back, deleteConfirmation } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorRecordBookDocument',
  components: {
    SailorRecordBookInfo,
    SailorRecordBookEdit,
    SailorRecordBookEditStatus,
    SailorRecordBookLineAdd,
    ViewPhotoList,
    VerificationSteps
  },
  data () {
    return {
      type: 'serviceRecordBook',
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
      return this.$store.getters.sailorDocumentByID({ type: 'serviceRecordBook', id: Number(this.documentID) }) || {}
    }
  },
  methods: {
    deleteDocument () {
      deleteConfirmation(this).then(confirmation => {
        if (confirmation) {
          this.$api.delete(`api/v2/sailor/${this.id}/service_record/${this.sailorDocument.id}/`).then(response => {
            if (response.code === 200 || response.code === 204) {
              this.$notification.success(this, this.$i18n.t('deletedDocument'))
              if (this.sailorDocument.status.id !== 86) {
                this.$store.commit('updateDataSailor', { type: 'serviceRecordBook', value: response.data })
                this.$store.commit('decrementBadgeCount', {
                  child: 'recordBookDocument',
                  parent: 'experienceAll'
                })
              } else {
                this.$store.commit('deleteDataSailor', { type: 'serviceRecordBook', value: this.sailorDocument })
              }
              back('experience-records')
            } else {
              this.$notification.error(this, this.$i18n.t('cantDeleteDoc'))
            }
          })
        }
      })
    }
  }
}
