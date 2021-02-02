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
        type="reportBOPacket"/>
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
  name: 'ReportDebtorPacket',
  components: {
    Table,
    Paginate
  },
  data () {
    return {
      groupID: this.$router.currentRoute.params['groupId'],
      agentID: this.$router.currentRoute.params['agentId'],
      sailorID: this.$router.currentRoute.params['sailorId'],
      packetID: this.$router.currentRoute.params['packetId'],
      fields: [
        { key: 'number_document',
          label: this.$i18n.t('number')
        },
        { key: 'typeDoc',
          label: this.$i18n.t('typeDoc')
        },
        { key: 'sailorFullName',
          label: this.$i18n.t('sailor')
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
      let url = link || `api/v1/reports/back_office/main_report/document/?packet_item=${this.packetID}&${this.search}`
      this.tableLoader = true

      this.$api.get(url).then(response => {
        this.tableLoader = false
        if (response.code === 200) {
          response.data.results.data.filter(item => {
            item.typeDoc = item.type_document.value
          })
          this.items = response.data
          this.items.results = response.data.results.data
        }
      })
    }
  }
}
</script>
