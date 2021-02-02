import ReportSearch from '@/components/molecules/ReportSearch/ReportSearch.vue'
import Paginate from '@/components/atoms/Paginate.vue'

export default {
  name: 'DocListCertificatesReport',
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
        { key: 'ntz_number',
          label: this.$i18n.t('number')
        },
        { key: 'sailorFullName',
          label: this.$i18n.t('fullName')
        },
        { key: 'course_traning',
          label: this.$i18n.t('course')
        },
        { key: 'ntz',
          label: this.$i18n.t('nameInstitution')
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
    /** Get certificates reports */
    getReportETI (sort = '', params = '', link = '') {
      this.tableLoader = true
      if (params) this.params = params
      if (sort) {
        params = this.params
        params.set('ordering', sort)
      }

      let url = `api/v1/reports/list/certificate_ntz/?${params}`
      if (link) url = link

      this.$api.get(url).then(response => {
        this.tableLoader = false
        if (response.code === 200) {
          this.items = response.data
        }
      })
    },

    changePage (link) {
      this.getReportETI('', '', link)
    },

    async setExcelDoc (sort = '', params) {
      if (sort) params.set('ordering', sort)

      let url = `api/v1/reports/xlsx/certificate_ntz/?${params}`

      await this.$api.get(url).then(response => {
        this.$notification.success(this, this.$i18n.t('exсelStatement'))
        this.$refs.search.allowSaveExcel = false
      })
    }
  }
}
