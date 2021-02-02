export default {
  name: 'BackOfficeAgentGroups',
  data () {
    return {
      fields: [
        { key: 'name_ukr',
          label: this.$i18n.t('agentGroup'),
          sortable: true
        },
        { key: 'event',
          label: this.$i18n.t('actions')
        }
      ],
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
      items: [],
      sortBy: 'name_ukr',
      sortDesc: false,
      tableLoader: false
    }
  },
  mounted () {
    this.getAgentGroupList()
  },
  methods: {
    /** Get all agents list by groups */
    getAgentGroupList () {
      this.tableLoader = true
      this.$api.get(`api/v1/seaman/seaman_by_group/`).then(response => {
        this.tableLoader = false
        if (response.status === 'success') {
          response.data.map(group => {
            group.behavior = {}
            group.agents.map(agent => {
              agent.behavior = {}
              agent.agentID = agent.id
              agent.userType = this.$i18n.t(`group-${agent.userprofile.type_user}`)
              agent.agentFullName = `${agent.last_name} ${agent.first_name} ${agent.userprofile.middle_name || ''}`
            })
          })
          this.items = response.data.filter(group => group.agents.length)
        }
      })
    }
  }
}
