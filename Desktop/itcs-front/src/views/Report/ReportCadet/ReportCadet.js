import ReportSearch from '@/components/molecules/ReportSearch/ReportSearch.vue'
import Paginate from '@/components/atoms/Paginate.vue'

export default {
  name: 'ReportCadet',
  components: {
    Paginate,
    ReportSearch
  },
  data () {
    return {
      fields: [
        { key: 'report-sailorID',
          label: this.$i18n.t('sailorId')
        },
        { key: 'sailorFullName',
          label: this.$i18n.t('fullName')
        },
        { key: 'name_nz',
          label: this.$i18n.t('nameInstitution')
        },
        { key: 'educ_with_dkk',
          label: this.$i18n.t('decisionEKK')
        },
        { key: 'passed_educ_exam',
          label: this.$i18n.t('resultEKK')
        },
        { key: 'haveProtocol',
          label: this.$i18n.t('protocolAvailability')
        },
        { key: 'haveStatement',
          label: this.$i18n.t('statementAvailability')
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
      params: null
    }
  },
  methods: {
    getReportCadets (sort = '', params = '', link = '') {
      this.tableLoader = true
      if (params) this.params = params
      if (sort) {
        params = this.params
        params.set('ordering', sort)
      }

      let url = `api/v1/reports/list/student_id/?${params}`
      if (link) url = link

      this.$api.get(url).then(response => {
        this.tableLoader = false
        if (response.code === 200) {
          this.items = response.data
        }
      })
    },

    changePage (link) {
      this.getReportCadets('', '', link)
    }
  }
}
