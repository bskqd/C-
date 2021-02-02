import Paginate from '@/components/atoms/Paginate'
import StatementsSearch from '@/components/molecules/ReportSearch/ReportSearch.vue'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'DocListAgentApplicationFromSailor',
  components: {
    Paginate,
    StatementsSearch
  },
  data () {
    return {
      fields: [
        { key: 'statement-dateCreate',
          label: this.$i18n.t('createDate')
        },
        { key: 'agentFullName',
          label: this.$i18n.t('nameEmployee')
        },
        { key: 'seafarerFullName',
          label: this.$i18n.t('sailorFullName')
        },
        { key: 'city',
          label: this.$i18n.t('city')
        },
        { key: 'statement-status',
          label: this.$i18n.t('status')
        },
        { key: 'event',
          label: this.$i18n.t('actions'),
          class: 'mw-0 position-relative'
        }
      ],
      items: [],
      sortName: null,
      sortAcs: false,
      tableLoader: true,
      newDoc: false,
      params: new URLSearchParams({
        page_size: 20
      }),
      checkAccess
    }
  },
  beforeCreate () {
    this.$store.commit('setActivePage', { name: 'agentStatements', access: checkAccess('menuItem-agentsStatementFromSailor') })
  },
  computed: {
    ...mapState({
      langFields: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr'
    })
  },
  mounted () {
    this.getAgentApplicationFromSailor()
  },
  methods: {
    /** Get statements list to work with agent */
    getAgentApplicationFromSailor (page = null, sort) {
      this.tableLoader = true
      if (sort) this.params.set('ordering', sort)
      const url = page || `api/v1/seaman/statement_seaman_sailor/?${this.params}`
      this.$api.get(url).then(response => {
        this.tableLoader = false
        if (response.status === 'success') {
          response.data.results.map(item => {
            item.behavior = {}
            item.sailor = item.sailor_key && item.sailor_key.id ? item.sailor_key.id : null
            item.city = item.agent.userprofile.city
            try {
              item.agentFullName = `${item.agent.last_name} ${item.agent.first_name} ${item.agent.userprofile.middle_name || ''}`
              item.seafarerFullName = `${item.sailor_key.last_name_ukr} ${item.sailor_key.first_name_ukr} ${item.sailor_key.middle_name_ukr || ''}`
            } catch (e) {}
          })
          this.items = response.data
        }
      })
    },

    /** Agent statements search with params */
    agentStatementsSearch (sort, params) {
      this.params = params
      const url = `api/v1/seaman/statement_seaman_sailor/?${params}`
      this.getAgentApplicationFromSailor(url)
    }
  }
}
