<template>
  <div>
    <b-card class="vx-card p-2" no-body>
      <StatementsSearch
        :srbStatements="true"
        :getReport="sailorRecordBookStatementsSearch"
        report="srbStatements"
        ref="search"
      />
    </b-card>
    <b-card class="vx-card p-2" no-body>
      <Table
        labelKeyAdd="recordBookStatement"
        :loader="tableLoader"
        :items="items.results"
        :fields="fields"
        :deleteRow="deleteDocument"
        :getDocuments="getApplicationsList"
        type="statementSRB"
        link="experience-statements-info"
        componentInfo="StatementSRBInfo"
        componentStatus="StatementSRBEditStatus"
        componentFiles="StatementSRBFiles"/>
      <Paginate
        :current="items.current"
        :next="items.next"
        :prev="items.previous"
        :count="items.count"
        :changePage="getApplicationsList" />
    </b-card>
  </div>
</template>

<script>
import Paginate from '@/components/atoms/Paginate.vue'
import StatementsSearch from '@/components/molecules/ReportSearch/ReportSearch.vue'
import { hideDetailed, showDetailed, getStatus } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'

export default {
  name: 'ApprovedRB',
  components: {
    Paginate,
    StatementsSearch
  },
  data () {
    return {
      checkAccess,
      filter: null,
      fields: [
        { key: 'date_created',
          label: this.$i18n.t('createDate'),
          sortable: true
        },
        { key: 'sailorFullName',
          label: this.$i18n.t('fullName'),
          sortable: true
        },
        { key: 'delivery',
          label: this.$i18n.t('delivery'),
          sortable: true
        },
        { key: 'is_payed',
          label: this.$i18n.t('payment'),
          sortable: true
        },
        { key: 'status_document',
          label: this.$i18n.t('status'),
          sortable: true
        },
        { key: 'event',
          label: this.$i18n.t('actions'),
          class: 'mw-0'
        }
      ],
      items: [],
      params: new URLSearchParams({
        page_size: 20
      }),
      tableLoader: true,
      buttonLoader: false,
      showDetailed,
      hideDetailed,
      getStatus
    }
  },
  beforeCreate () {
    this.$store.commit('setActivePage', { name: 'statementSRB', access: checkAccess('tab-statementServiceRecordBook') })
  },
  mounted () {
    this.getApplicationsList()
  },
  methods: {
    getApplicationsList (link = null) {
      this.tableLoader = true
      const url = link || `api/v1/reports/list_statement_service_record/?${this.params}`
      this.$api.get(url).then(response => {
        if (response.status === 'success') {
          this.tableLoader = false
          response.data.results.map((item) => {
            item.behavior = {}
          })
          this.items = response.data
        }
      })
    },

    sailorRecordBookStatementsSearch (sort, params) {
      this.params = params
      const url = `api/v1/reports/list_statement_service_record/?${this.params}`
      this.getApplicationsList(url)
    },

    /** Delete record book application */
    deleteDocument (row) {
      this.$api.delete(`api/v2/sailor/${row.item.sailor}/statement/service_record/${row.item.id}/`)
        .then(response => {
          if (response.code === 204) {
            this.$notification.success(this, this.$i18n.t('deletedStatementRB'))
            this.getApplicationsList()
          }
        })
    }
  }
}
</script>

<style scoped>
  .card .card {
    box-shadow: -8px 12px 18px 0 rgba(25, 42, 70, 0.13) !important;
  }
  .active svg {
    fill: #42627e
  }
</style>
