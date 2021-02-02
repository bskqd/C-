import { hideDetailed } from '@/mixins/main'

export default {
  name: 'BackOfficeAgentGroupsList',
  props: {
    row: Object,
    getDocuments: Function
  },
  data () {
    return {
      fieldsAgents: [
        { key: 'agentID',
          label: 'ID'
        },
        { key: 'agentFullName',
          label: this.$i18n.t('agentFullName'),
          sortable: true
        },
        { key: 'userType',
          label: this.$i18n.t('position'),
          sortable: true
        },
        { key: 'agentAffiliate',
          label: this.$i18n.t('affiliate')
        },
        { key: 'agentCity',
          label: this.$i18n.t('city')
        },
        { key: 'event',
          label: this.$i18n.t('actions')
        }
      ],
      sortBy: 'agentFullName',
      sortDesc: false,
      hideDetailed
    }
  }
}
