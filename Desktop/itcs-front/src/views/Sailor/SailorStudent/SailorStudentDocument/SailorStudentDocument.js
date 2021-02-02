import SailorStudentInfo from '@/views/Sailor/SailorStudent/SailorStudentInfo/SailorStudentInfo.vue'
import SailorStudentEdit from '@/views/Sailor/SailorStudent/SailorStudentEdit/SailorStudentEdit.vue'
import SailorStudentEditStatus from '@/views/Sailor/SailorStudent/SailorStudentEditStatus/SailorStudentEditStatus.vue'
import ViewPhotoList from '@/components/atoms/ViewPhotoList.vue'
import { viewDetailedComponent, back, deleteConfirmation } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorStudentDocument',
  components: {
    SailorStudentInfo,
    SailorStudentEdit,
    SailorStudentEditStatus,
    ViewPhotoList
  },
  data () {
    return {
      type: 'student',
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
      return this.$store.getters.sailorDocumentByID({ type: 'student', id: Number(this.documentID) }) || {}
    }
  },
  methods: {
    deleteDocument () {
      deleteConfirmation(this).then(confirmation => {
        if (confirmation) {
          this.$api.delete(`api/v1/cadets/student_id/${this.sailorDocument.id}/`).then(response => {
            if (response.status === 'deleted') {
              this.$notification.success(this, this.$i18n.t('deletedDocument'))
              this.$store.commit('deleteDataSailor', { type: 'student', value: this.sailorDocument })
              this.$store.commit('decrementBadgeCount', {
                child: 'studentCard',
                parent: 'educationAll'
              })
              back('education-student')
            } else {
              this.$notification.error(this, this.$i18n.t('cantDeleteDoc'))
            }
          })
        }
      })
    }
  }
}
