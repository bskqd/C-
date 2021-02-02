<template>
  <div>
    <b-card>
      <Table
        :loader="tableLoader"
        :items="items.results"
        :fields="fields"
        :sortBy="sortAcs"
        :sortAcs="sortAcs"
        :sortDesc="sortDesc"
        :getDocuments="getReport"
        :type="typeDocument"/>
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
  name: 'ReportDistributionGroup',
  components: {
    Table,
    Paginate
  },
  props: {
    search: String
  },
  data () {
    return {
      fields: [
        { key: 'count',
          label: this.$i18n.t('itemsAmount')
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
  computed: {
    typeDocument () {
      if (this.$router.currentRoute.params['typeDoc'] === 'adv_training') {
        return 'reportDistributionAdvanceTraining'
      } else {
        return 'reportBO'
      }
    }
  },
  methods: {
    getReport (link = null) {
      this.tableLoader = true
      const typeDoc = this.$router.currentRoute.params['typeDoc']
      const urlId = this.$router.currentRoute.params['firstIdEntry']

      let url = ''
      if (link) {
        url = link
      } else {
        switch (typeDoc) {
          case 'sqc':
          case 'seaman':
            url = `api/v1/reports/back_office/distribution/${typeDoc}/seaman/?group=${urlId}&${this.search}`
            this.fields.unshift({ key: 'agent', label: this.$i18n.t('userAgent') })
            break
          case 'eti':
            url = `api/v1/reports/back_office/distribution/${typeDoc}/courses/?institution=${urlId}&${this.search}`
            this.fields.unshift({ key: 'course', label: this.$i18n.t('course') })
            break
          case 'medical':
            url = `api/v1/reports/back_office/distribution/${typeDoc}/doctor/?medical=${urlId}&${this.search}`
            this.fields.unshift({ key: 'doctor', label: this.$i18n.t('doctor') })
            break
          case 'dpd':
            url = `api/v1/reports/back_office/distribution/${typeDoc}/document/?branch_office=${urlId}&${this.search}`
            this.fields.splice(0, 1, { key: 'name', label: this.$i18n.t('typeDoc') })
            break
          case 'portal':
          case 'sc':
            url = `api/v1/reports/back_office/distribution/${typeDoc}/seaman/?branch_office=${urlId}&${this.search}`
            this.fields.unshift({ key: 'agent', label: this.$i18n.t('userAgent') })
            break
          case 'adv_training':
            url = `api/v1/reports/back_office/distribution/${typeDoc}/sailor/?level=${urlId}&${this.search}`
            this.fields.splice(0, 1, { key: 'level_qualification', label: this.$i18n.t('qualification') })
            this.fields.unshift({ key: 'sailorFullName', label: this.$i18n.t('seafarer') })
            break
        }
      }
      this.$api.get(url).then(response => {
        this.tableLoader = false
        if (response.code === 200) {
          if (typeDoc === 'dpd') {
            response.data.results.data[0].map(item => {
              item.searchParams = this.search
              item.link = `${urlId}/sailor/${item.type}`
            })
          } else {
            response.data.results.data.map(item => {
              item.searchParams = this.search
              switch (typeDoc) {
                case 'sqc':
                case 'portal':
                case 'seaman':
                case 'sc':
                  item.link = `${urlId}/sailor/${item.agent.id}`
                  break
                case 'eti':
                  item.link = `${urlId}/sailor/${item.course.id}`
                  break
                case 'medical':
                  item.link = `${urlId}/sailor/${item.doctor ? item.doctor.id : 0}`
                  break
              }
            })
          }
          this.items = response.data
          this.items.results = typeDoc === 'dpd' ? response.data.results.data[0] : response.data.results.data
        }
      })
    }
  }
}
</script>
