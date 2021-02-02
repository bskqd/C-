import AgentStatementsInfo from '@/views/AgentStatements/AgentStatementsInfo/AgentStatementsInfo.vue'
import AgentStatementsEdit from '@/views/AgentStatements/AgentStatementsEdit/AgentStatementsEdit.vue'
import ViewPhotoList from '@/components/atoms/ViewPhotoList.vue'
import { viewDetailedComponent, back, deleteConfirmation } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'AgentStatementsDocument',
  components: {
    AgentStatementsInfo,
    AgentStatementsEdit,
    ViewPhotoList
  },
  data () {
    return {
      sailorDocument: {},
      type: 'agentStatements',
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
    this.getAgentStatementDocument()
  },
  methods: {
    getAgentStatementDocument () {
      this.$api.get(`api/v1/seaman/statement_seaman_sailor/${this.documentID}/`).then(response => {
        if (response.status === 'success') {
          response.data.behavior = { viewInfoBlock: true }
          response.data.city = response.data.agent.userprofile.city
          try {
            response.data.agentFullName = `${response.data.agent.last_name} ${response.data.agent.first_name} ${response.data.agent.userprofile.middle_name || ''}`
            response.data.seafarerFullName = `${response.data.sailor_key.last_name_ukr} ${response.data.sailor_key.first_name_ukr} ${response.data.sailor_key.middle_name_ukr || ''}`
          } catch (e) {}
          this.sailorDocument = response.data
        }
      })
    }
  }
}
