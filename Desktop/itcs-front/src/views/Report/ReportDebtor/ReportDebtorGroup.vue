<template>
  <div>
<!--    <div>-->
<!--      <router-link to="/report/debtor">отчет</router-link>/группа-->
<!--    </div>-->
    <b-card>
      <Table
        :loader="tableLoader"
        :items="items.results"
        :fields="fields"
        :sortBy="sortAcs"
        :sortAcs="sortAcs"
        :sortDesc="sortDesc"
        :getDocuments="getReport"
        type="reportBO"/>
      <Paginate
        :current="items.current"
        :next="items.next"
        :prev="items.previous"
        :count="items.count"
        :changePage="getReport" />
    </b-card>
  </div>
</template>

<script>
import Table from '@/components/layouts/Table/Table.vue'
import Paginate from '@/components/atoms/Paginate.vue'

export default {
  name: 'ReportDebtorGroup',
  components: {
    Table,
    Paginate
  },
  props: {
    search: String
  },
  data () {
    return {
      groupID: this.$router.currentRoute.params['groupId'],
      fields: [
        { key: 'agent',
          label: this.$i18n.t('userAgent')
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
      sortName: null
    }
  },
  mounted () {
    this.getReport()
  },
  methods: {
    getReport (link = '') {
      let url = `api/v1/reports/back_office/main_report/seaman/?group=${this.groupID}&${this.search}`
      this.tableLoader = true

      if (this.groupID === 0 || this.groupID === '0') {
        url = `api/v1/reports/back_office/main_report/seaman/?group_is_null=true&${this.search}`
      }

      if (link) url = link

      this.$api.get(url).then(response => {
        this.tableLoader = false
        if (response.code === 200) {
          response.data.results.data.filter(item => {
            item.searchParams = this.search
            item.link = `agent/${item.agent.id}`
          })
          this.items = response.data
          this.items.results = response.data.results.data
        }
      })
    }
  }
}
</script>
