import NewAgentsInfo from '@/views/NewAgents/NewAgentsInfo/NewAgentsInfo.vue'
import NewAgentsEdit from '@/views/NewAgents/NewAgentsEdit/NewAgentsEdit.vue'
import NewAgentsEditStatus from '@/views/NewAgents/NewAgentsEditStatus/NewAgentsEditStatus.vue'
import ViewPhotoList from '@/components/atoms/ViewPhotoList.vue'
import { viewDetailedComponent, back, deleteConfirmation } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'NewAgentsDocument',
  components: {
    NewAgentsInfo,
    NewAgentsEdit,
    NewAgentsEditStatus,
    ViewPhotoList
  },
  data () {
    return {
      type: 'newAgents',
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
      return this.$store.getters.sailorDocumentByID({ type: 'newAgents', id: Number(this.documentID) }) || {}
    }
  }
}
