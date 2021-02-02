import BackOfficeCoursesInfo from '@/views/BackOffice/BackOfficeCourses/BackOfficeCoursesInfo/BackOfficeCoursesInfo.vue'
import BackOfficeCoursesEdit from '@/views/BackOffice/BackOfficeCourses/BackOfficeCoursesEdit/BackOfficeCoursesEdit.vue'
import { back, deleteConfirmation, viewDetailedComponent } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'BackOfficeCoursesDocument',
  components: {
    BackOfficeCoursesInfo,
    BackOfficeCoursesEdit
  },
  data () {
    return {
      sailorDocument: {},
      type: 'backOfficeCourseLine',
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
    }
  },
  mounted () {
    this.getCourseETI()
  },
  methods: {
    getCourseETI () {
      this.$api.get(`api/v1/back_off/certificates/eti_registry/${this.documentID}/`).then(response => {
        if (response.code === 200) {
          response.data.behavior = { viewInfoBlock: true }
          this.sailorDocument = response.data
        }
      })
    },
    deleteDocument () {
      deleteConfirmation(this).then(confirmation => {
        if (confirmation) {
          this.$api.delete(`api/v1/back_off/certificates/eti_registry/${this.sailorDocument.id}/`).then(response => {
            if (response.code === 204) {
              this.$notification.success(this, this.$i18n.t('deletedDocument'))
              back('courses-backoffice')
            }
          })
        }
      })
    }
  }
}
