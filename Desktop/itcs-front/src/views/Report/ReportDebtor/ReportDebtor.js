import Table from '@/components/layouts/Table/Table.vue'
import Paginate from '@/components/atoms/Paginate.vue'
import ReportSearch from '@/components/molecules/ReportSearch/ReportSearch.vue'
import { mapState } from 'vuex'

export default {
  name: 'ReportDebtor',
  components: {
    Table,
    ReportSearch,
    Paginate
  },
  data () {
    return {
      fields: [
        { key: 'group',
          label: this.$i18n.t('group')
        },
        { key: 'sum_f1f2',
          label: this.$i18n.t('coming')
        },
        { key: 'distribution_sum',
          label: this.$i18n.t('distribution')
        },
        { key: 'profit_sum',
          label: this.$i18n.t('profit')
        },
        { key: 'event',
          label: this.$i18n.t('go'),
          class: 'mw-0'
        }
      ],
      items: [],
      tableLoader: false,
      sortAcs: null,
      sortDesc: null,
      sortName: null,
      params: null,
      typeDocument: 'protocolSQC',
      typeDocumentList: [
        { text: this.$i18n.t('protocolsSQC'), id: 'protocolSQC' },
        { text: this.$i18n.t('statementSQC'), id: 'statementSQC' }
      ]
    }
  },
  computed: {
    ...mapState({
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    })
  },
  methods: {
    /** Get statement SQC reports */
    getReport (sort = '', params = '', link = '') {
      if (params) this.params = params
      if (sort) {
        params = this.params
        params.set('ordering', sort)
      }

      let url = link || `api/v1/reports/back_office/main_report/group/?${params}`
      this.tableLoader = true

      this.$api.get(url).then(response => {
        this.tableLoader = false
        if (response.code === 200) {
          response.data.results.data.map(item => {
            item.searchParams = params
            if (item.group) item.link = `debtor/group/${item.group.id}/`
            else item.link = `debtor/group/${0}/`
          })
          this.items = response.data
          this.items.results = response.data.results.data
        }
      })
    },

    changePage (link) {
      this.getReport('', '', link)
    }
  }
}
