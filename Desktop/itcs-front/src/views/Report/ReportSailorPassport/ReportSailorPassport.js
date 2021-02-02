import ReportSearch from '@/components/molecules/ReportSearch/ReportSearch.vue'
import Paginate from '@/components/atoms/Paginate.vue'

export default {
  name: 'ReportSailorPassport',
  components: {
    ReportSearch,
    Paginate
  },
  data () {
    return {
      fields: [
        { key: 'report-sailorID',
          label: this.$i18n.t('sailorId')
        },
        { key: 'number_document',
          label: this.$i18n.t('number')
        },
        { key: 'sailorPassportPort',
          label: this.$i18n.t('port')
        },
        { key: 'country',
          label: this.$i18n.t('country')
        },
        { key: 'sailorFullName',
          label: this.$i18n.t('fullName')
        },
        { key: 'date_start',
          label: this.$i18n.t('dateIssue')
        },
        { key: 'date_end',
          label: this.$i18n.t('dateTermination')
        },
        { key: 'status_document',
          label: this.$i18n.t('status')
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
      sortName: null
    }
  },
  methods: {
    getSailorPassportReport (sort = '', params = '', link = '') {
      this.tableLoader = true
      if (params) this.params = params
      if (sort) {
        params = this.params
        params.set('ordering', sort)
      }

      let url = `api/v1/reports/list/sailor_passport/?${params}`
      if (link) url = link

      this.$api.get(url).then(response => {
        this.tableLoader = false
        if (response.code === 200) {
          this.items = response.data
        }
      })
    },

    changePage (link) {
      this.getEducationReport('', '', link)
    }
  }
}
