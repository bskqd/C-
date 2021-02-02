import ReportSearch from '@/components/molecules/ReportSearch/ReportSearch.vue'
import Paginate from '@/components/atoms/Paginate.vue'

export default {
  name: 'DocListQualReport',
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
        { key: 'number_document',
          label: this.$i18n.t('number')
        },
        { key: 'type_document',
          label: this.$i18n.t('typeDoc')
        },
        { key: 'sailorFullName',
          label: this.$i18n.t('fullName')
        },
        { key: 'sailor.birth_date',
          label: this.$i18n.t('dateBorn')
        },
        { key: 'country',
          label: this.$i18n.t('country')
        },
        { key: 'qualificationStatementPort',
          label: this.$i18n.t('port')
        },
        { key: 'rank',
          label: this.$i18n.t('rank')
        },
        { key: 'sqc_positions',
          label: this.$i18n.t('position')
        },
        { key: 'status_document',
          label: this.$i18n.t('status')
        },
        { key: 'event',
          label: this.$i18n.t('go'),
          class: 'mw-0'
        }
      ],
      typeDocument: 'diplomasQualification',
      typeDocumentList: [
        { text: this.$i18n.t('qualificationDocs'), id: 'diplomasQualification' }
        // { text: this.$i18n.t('qualificationStatement'), id: 'statementQualification' }
      ],
      items: [],
      tableLoader: false,
      sortAcs: null,
      sortDesc: null,
      sortName: null,
      typeDoc: null
    }
  },
  methods: {
    getReportQualification (sort = '', params = '', link = '') {
      if (params) this.params = params
      if (sort) {
        params = this.params
        params.set('ordering', sort)
      }

      let url = `api/v1/reports/list/qual_doc/?${params}`
      this.tableLoader = true

      if (this.typeDocument.id === 'statementQualification') {
        url = `api/v1/reports/list/statement_qual/?${params}`
      }

      if (link) url = link

      this.$api.get(url).then(response => {
        this.tableLoader = false
        if (response.code === 200) {
          response.data.results.map(item => {
            item._list_positions = item.position ? item.position.map(value => {
              return value[this.labelName]
            }) : []
            item.port = item.other_port ? item.other_port : item.port[this.labelName]
          })
          this.items = response.data
        }
      })
    },

    changePage (link) {
      this.getReportQualification('', '', link)
    }
  }
}
