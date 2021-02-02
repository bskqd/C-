import { hideDetailed } from '@/mixins/main'
import { mapState } from 'vuex'

export default {
  name: 'NewAgentsEditStatus',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      agentGroup: null,
      status: this.sailorDocument.status_document,
      buttonLoader: false,
      hideDetailed
    }
  },
  computed: {
    ...mapState({
      labelName: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr',
      agentGroups: state => state.directory.agentGroups
    }),
    mappingStatuses () {
      return this.$store.getters.statusChoose('StatementAgent')
    }
  },
  methods: {
    /** Save new status for agent application */
    saveAgentApplicationStatus () {
      this.buttonLoader = true
      const body = {
        status_document: this.status.id
      }
      if (this.status.id === 64) {
        body.group = this.agentGroup.id
      }
      this.$api.patch(`api/v1/seaman/statement_seaman/${this.sailorDocument.id}/`, body).then(response => {
        this.buttonLoader = false
        switch (response.status) {
          case 'success':
            this.$notification.success(this, this.$i18n.t('agentStatementEdited'))
            this.$store.commit('updateDataSailor', { type: 'newAgents', value: response.data })
            break
          case 'error':
            if (response.data[0] === 'user was not created') {
              this.$notification.error(this, this.$i18n.t('notCreatedUser'))
            } else if (response.data[0] === 'Please enter your email address') {
              this.$notification.error(this, this.$i18n.t('enterYourEmail'))
            } else if (response.data[0] === 'Please use another email address') {
              this.$notification.error(this, this.$i18n.t('useAnotherEmail'))
            }
            break
          case 'server error':
            this.$notification.error(this, this.$i18n.t('error'))
            break
        }
      })
    }
  }
}
