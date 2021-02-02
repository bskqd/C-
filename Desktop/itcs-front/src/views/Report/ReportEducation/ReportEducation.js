import ReportSearch from '@/components/molecules/ReportSearch/ReportSearch.vue'
import Paginate from '@/components/atoms/Paginate'

export default {
  name: 'ReportEducation',
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
        { key: 'serial',
          label: this.$i18n.t('serial')
        },
        { key: 'registry_number',
          label: this.$i18n.t('registrationNumber')
        },
        { key: 'sailorFullName',
          label: this.$i18n.t('fullName')
        },
        { key: 'type_document',
          label: this.$i18n.t('typeDoc')
        },
        { key: 'name_nz',
          label: this.$i18n.t('nameInstitution')
        },
        { key: 'qualification',
          label: this.$i18n.t('qualification')
        },
        { key: 'date_start',
          label: this.$i18n.t('dateIssue')
        },
        { key: 'experied_date',
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
    getEducationReport (sort = '', params = '', link = '') {
      this.tableLoader = true
      if (params) this.params = params
      if (sort) {
        params = this.params
        params.set('ordering', sort)
      }

      let url = `api/v1/reports/list/educ_doc/?${params}`
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
    },

    async setExcelDoc (sort = '', params) {
      if (sort) params.set('ordering', sort)

      let url = `api/v1/reports/xlsx/protocol_dkk/?${params}`

      await this.$api.get(url).then(response => {
        this.$notification.success(this, this.$i18n.t('exсelStatement'))
        this.$refs.search.allowSaveExcel = false
      })
    }
  }
}
