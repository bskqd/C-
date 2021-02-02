import ReportSearch from '@/components/molecules/ReportSearch/ReportSearch.vue'
import Paginate from '@/components/atoms/Paginate.vue'
import { mapState } from 'vuex'

export default {
  name: 'ReportSQC',
  components: {
    ReportSearch,
    Paginate
  },
  data () {
    return {
      API: process.env.VUE_APP_API,
      fields: [
        { key: 'report-sailorID',
          label: this.$i18n.t('sailorId')
        },
        { key: 'report-numberProtocol',
          label: this.$i18n.t('protocol')
        },
        { key: 'report-dateCreated',
          label: this.$i18n.t('createDate')
        },
        { key: 'report-affiliate',
          label: this.$i18n.t('affiliate')
        },
        { key: 'numberStatement',
          label: this.$i18n.t('statement')
        },
        { key: 'sailorFullName',
          label: this.$i18n.t('fullName')
        },
        { key: 'sailor.birth_date',
          label: this.$i18n.t('dateBorn')
        },
        { key: 'documentProperty',
          label: this.$i18n.t('solution')
        },
        { key: 'report-rank',
          label: this.$i18n.t('rank')
        },
        { key: 'sqc_positions',
          label: this.$i18n.t('position')
        },
        { key: 'is_experience_required',
          label: this.$i18n.t('experience')
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
      userId: state => state.main.user.id,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    })
  },
  mounted () {
    if (this.userId === 14365 || this.userId === 14488) {
      const index = this.fields.findIndex(n => n.key === 'is_experience_required')
      if (index !== -1) {
        this.fields.splice(index, 1)
      }
    }
  },
  methods: {
    /** Get statement SQC reports */
    getReportSQC (sort = '', params = '', link = '') {
      console.log(link)
      if (params) this.params = params
      if (sort) {
        params = this.params
        params.set('ordering', sort)
      }

      let url = `api/v1/reports/list/protocol_dkk/?${params}`
      this.tableLoader = true

      if (this.typeDocument === 'statementSQC') {
        url = `api/v1/reports/list/statement_dkk/?${params}`
      }

      if (link) url = link

      this.$api.get(url).then(response => {
        this.tableLoader = false
        if (response.code === 200) {
          response.data.results.map(item => {
            item._list_positions = item.position.map(value => value[this.labelName])
            item.documentProperty = this.$i18n.t(item.document_property)
          })
          this.renderTable(response.data)
        }
      })
    },

    /** Generate table depends on document type */
    renderTable (data) {
      data.results.filter(item => {
        // let position = item.position.map(value => {
        //   return value[this.labelName]
        // })
        item.numberProtocol = this.typeDocument === 'protocolSQC' ? item.number_document : item.protocol_number
        item.numberStatement = this.typeDocument === 'protocolSQC' ? item.statement_dkk : item.number_document
        item.dateCreated = this.typeDocument === 'protocolSQC' ? item.date_meeting : item.date_create
        // item.position = position.join(', ')
      })

      this.items = data
    },

    changePage (link) {
      this.getReportSQC('', '', link)
    },

    /** Sent search result to excel list */
    async setExcelDoc (sort = '', params) {
      if (sort) params.set('ordering', sort)

      let url = `api/v1/reports/xlsx/protocol_dkk/?${params}`

      if (this.typeDocument.id === 'statementSQC') {
        url = `api/v1/reports/xlsx/statement_dkk/?${params}`
      }

      await this.$api.get(url).then(() => {
        this.$notification.success(this, this.$i18n.t('exсelStatement'))
        this.$refs.search.allowSaveExcel = false
      })
    },

    updateTableCells () {
      this.items = []
      this.$refs.search.viewSearch = true
      if (this.typeDocument === 'statementSQC') {
        this.fields = this.fields.filter(value => value.key !== 'documentProperty')
      } else if (this.typeDocument === 'protocolSQC' && !this.fields.find(value => value.key === 'documentProperty')) {
        this.fields.splice(7, 0, { key: 'documentProperty', label: this.$i18n.t('solution') })
      }
    }
  }
}
