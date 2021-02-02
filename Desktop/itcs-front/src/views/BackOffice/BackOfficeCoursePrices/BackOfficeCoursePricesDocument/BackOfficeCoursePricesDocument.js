import BackOfficeCoursePriceInfo from '@/views/BackOffice/BackOfficeCoursePrices/BackOfficeCoursePricesInfo/BackOfficeCoursePricesInfo.vue'
import BackOfficeCoursePriceEdit from '@/views/BackOffice/BackOfficeCoursePrices/BackOfficeCoursePricesEdit/BackOfficeCoursePricesEdit.vue'
import { back, deleteConfirmation, viewDetailedComponent } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'BackOfficeCoursePricesDocument',
  components: {
    BackOfficeCoursePriceInfo,
    BackOfficeCoursePriceEdit
  },
  data () {
    return {
      type: 'backOfficeCoursePrice',
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
      return this.$store.getters.sailorDocumentByID({ type: 'backOfficeCoursePrice', id: Number(this.documentID) }) || {}
    }
  },
  methods: {
    deleteDocument () {
      deleteConfirmation(this).then(confirmation => {
        if (confirmation) {
          this.$api.delete(`api/v1/back_off/course_price/${this.sailorDocument.id}/`).then(response => {
            switch (response.status) {
              case 'deleted':
                this.$notification.success(this, this.$i18n.t('coursePriceDeleted'))
                this.$store.commit('deleteDataSailor', { type: 'backOfficeCoursePrice', value: this.sailorDocument })
                back('price-course-backoffice')
                break
              case 'error':
              case 'server error':
                this.$notification.error(this, this.$i18n.t('cantBeDeleted'))
                break
            }
          })
        }
      })
    }
  }
}
