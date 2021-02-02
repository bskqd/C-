export default {
  name: 'DocExelListReportSQC',
  data () {
    return {
      fields: [
        { key: 'file_name',
          label: this.$i18n.t('nameDoc'),
          sortable: true
        },
        { key: 'created_at',
          label: this.$i18n.t('createDate'),
          sortable: true
        },
        { key: 'event',
          label: this.$i18n.t('save'),
          class: 'mw-0'
        }
      ],
      items: [],
      filter: null,
      sortBy: 'createDate',
      sortDesc: false,
      tableLoader: true
    }
  },
  mounted () {
    this.getExcelDocuments()
  },
  methods: {
    getExcelDocuments () {
      this.$api.get('api/v1/reports/list_files/').then(response => {
        this.tableLoader = false
        if (response.code === 200) {
          this.items = response.data
        }
      })
    },

    saveExcelDocument (row) {
      this.$api.getPhoto(`api/v1/reports/report/${row.item.token}`).then(response => {
        window.open(response, '_blank')
        this.getExcelDocuments()
      })
    }
  }
}
