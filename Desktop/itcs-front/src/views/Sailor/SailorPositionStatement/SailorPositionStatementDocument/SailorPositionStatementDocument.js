import SailorPositionStatementInfo from '@/views/Sailor/SailorPositionStatement/SailorPositionStatementInfo/SailorPositionStatementInfo.vue'
import SailorPositionStatementEdit from '@/views/Sailor/SailorPositionStatement/SailorPositionStatementEdit/SailorPositionStatementEdit.vue'
import ViewPhotoList from '@/components/atoms/ViewPhotoList.vue'
import { viewDetailedComponent, back, deleteConfirmation } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorPositionStatementDocument',
  components: {
    SailorPositionStatementInfo,
    SailorPositionStatementEdit,
    ViewPhotoList
  },
  data () {
    return {
      type: 'positionStatement',
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
      return this.$store.getters.sailorDocumentByID({ type: 'positionStatement', id: Number(this.documentID) }) || {}
    }
  },
  methods: {
    deleteDocument () {
      deleteConfirmation(this).then(confirmation => {
        if (confirmation) {
          this.$api.delete(`api/v1/back_off/packet/${this.sailorDocument.id}/`).then(response => {
            if (response.status === 'deleted') {
              this.$notification.success(this, this.$i18n.t('deletedDocument'))
              this.$store.commit('deleteDataSailor', { type: 'positionStatement', value: this.sailorDocument })
              this.$store.commit('decrementBadgeCount', {
                child: 'positionStatement',
                parent: ''
              })
              back('position-statements')
            } else {
              this.$notification.error(this, this.$i18n.t('cantDeleteDoc'))
            }
          })
        }
      })
    }
  }
}
