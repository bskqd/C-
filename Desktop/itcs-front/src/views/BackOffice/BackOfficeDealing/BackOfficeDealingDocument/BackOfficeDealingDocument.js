import BackOfficeDealingInfo from '@/views/BackOffice/BackOfficeDealing/BackOfficeDealingInfo/BackOfficeDealingInfo.vue'
import BackOfficeDealingEdit from '@/views/BackOffice/BackOfficeDealing/BackOfficeDealingEdit/BackOfficeDealingEdit.vue'
import { viewDetailedComponent, back, deleteConfirmation } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'BackOfficeDealingDocument',
  components: {
    BackOfficeDealingInfo,
    BackOfficeDealingEdit
  },
  data () {
    return {
      type: 'backOfficeDealing',
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
      return this.$store.getters.sailorDocumentByID({ type: 'backOfficeDealing', id: Number(this.documentID) }) || {}
    }
  }
}
