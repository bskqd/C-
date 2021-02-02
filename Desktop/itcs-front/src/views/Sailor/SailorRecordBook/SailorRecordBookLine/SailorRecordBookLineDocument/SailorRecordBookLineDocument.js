import SailorRecordBookLineInfo from '@/views/Sailor/SailorRecordBook/SailorRecordBookLine/SailorRecordBookLineInfo/SailorRecordBookLineInfo.vue'
import SailorRecordBookLineEdit from '@/views/Sailor/SailorRecordBook/SailorRecordBookLine/SailorRecordBookLineEdit/SailorRecordBookLineEdit.vue'
import SailorRecordBookLineEditStatus from '@/views/Sailor/SailorRecordBook/SailorRecordBookLine/SailorRecordBookLineEditStatus/SailorRecordBookLineEditStatus.vue'
import VerificationSteps from '@/components/atoms/VerificationSteps/VerificationSteps.vue'
import ViewPhotoList from '@/components/atoms/ViewPhotoList.vue'
import { viewDetailedComponent, back, deleteConfirmation } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorRecordBookLineDocument',
  components: {
    SailorRecordBookLineInfo,
    SailorRecordBookLineEdit,
    SailorRecordBookLineEditStatus,
    ViewPhotoList,
    VerificationSteps
  },
  data () {
    return {
      type: 'serviceRecordBookLine',
      viewDetailedComponent,
      deleteConfirmation,
      checkAccess,
      back
    }
  },
  mounted () {
    this.$store.dispatch('getRecordBookLineEntry', { id: this.$route.params.id, service_book: this.$route.params.documentID })
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr'
    }),
    lineID () {
      return this.$route.params.lineID
    },
    sailorDocument () {
      return this.$store.getters.sailorDocumentByID({ type: 'serviceRecordBookLine', id: Number(this.lineID) }) || {}
    }
  },
  methods: {
    deleteDocument () {
      deleteConfirmation(this).then(confirmation => {
        if (confirmation) {
          this.$api.delete(`api/v2/sailor/${this.id}/service_record/${this.sailorDocument.service_record}/line/${this.sailorDocument.id}/`).then(response => {
            if (response.code === 200 || response.code === 204) {
              this.$notification.success(this, this.$i18n.t('deletedDocument'))
              back('experience-records-info')
            } else {
              this.$notification.error(this, this.$i18n.t('cantDeleteDoc'))
            }
          })
        }
      })
    }
  }
}
