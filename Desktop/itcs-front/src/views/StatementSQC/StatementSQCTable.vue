<template>
  <div class="vx-card">
    <Table
      :loader="tableLoader"
      :items="items.results"
      :fields="fields"
      type="menuStatementSQC"
      link="sqc-statements-info"
    />
    <Paginate
      :current="items.current"
      :next="items.next"
      :prev="items.previous"
      :count="items.count"
      :changePage="getDocuments" />
  </div>
</template>

<script>
import Paginate from '@/components/atoms/Paginate'

export default {
  name: 'StatementSQCTable',
  components: {
    Paginate
  },
  props: {
    status: Number
  },
  data () {
    return {
      fields: [
        { key: 'sailorFullName',
          label: this.$i18n.t('sailorName')
        },
        { key: 'number_document',
          label: this.$i18n.t('docNumber')
        },
        { key: 'branch_office',
          label: this.$i18n.t('affiliate')
        },
        { key: 'event',
          label: this.$i18n.t('actions'),
          class: 'mw-0'
        }
      ],
      items: [],
      statusID: '24',
      tableLoader: true
    }
  },
  watch: {
    status (newValue) {
      this.setSearchParams(newValue)
    }
  },
  mounted () {
    this.setSearchParams(this.status)
  },
  methods: {
    setSearchParams (status) {
      this.statusID = status.toString()

      const params = new URLSearchParams()
      params.set('page_size', '50')
      params.set('from_date', '2020-02-07')
      params.set('status_document', this.statusID)
      params.set('have_protocol', 'false')

      const url = `api/v1/reports/list/statement_dkk/?${params}`
      this.getDocuments(url)
    },

    getDocuments (url) {
      this.tableLoader = true
      this.$api.get(url).then(response => {
        this.tableLoader = false
        if (response.status === 'success') {
          this.items = response.data
        }
      })
    }
  }
}
</script>
