import BackOfficeETIListInfo from '@/views/BackOffice/BackOfficeETIList/BackOfficeETIListInfo/BackOfficeETIListInfo.vue'
import BackOfficeETIListEdit from '@/views/BackOffice/BackOfficeETIList/BackOfficeETIListEdit/BackOfficeETIListEdit.vue'
import { viewDetailedComponent, back, deleteConfirmation } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'BackOfficeETIListDocument',
  components: {
    BackOfficeETIListInfo,
    BackOfficeETIListEdit
  },
  data () {
    return {
      type: 'backOfficeETIList',
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
      return this.$store.getters.sailorDocumentByID({ type: 'backOfficeETIList', id: Number(this.documentID) }) || {}
    }
  }
}
