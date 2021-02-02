<template>
  <div>
    <b-card>
      <div class="w-100 text-left">
        <b-button
          @click="saveExcelDoc()"
          variant="primary"
        >
          {{ $t('saveAsExcel') }}
        </b-button>
      </div>
      <Table
        :loader="tableLoader"
        :items="items.results"
        :fields="fields"
        :sortBy="sortAcs"
        :sortAcs="sortAcs"
        :sortDesc="sortDesc"
        :getDocuments="getReport"
        type="reportDistributionSailor"/>
      <Paginate
        :current="items.current"
        :next="items.next"
        :prev="items.previous"
        :count="items.count"
        :changePage="getReport" />
    </b-card>
    <notifications group="notify" />
  </div>
</template>

<script>
import Table from '@/components/layouts/Table/Table.vue'
import Paginate from '@/components/atoms/Paginate.vue'
import { mapState } from 'vuex'

export default {
  name: 'ReportDistributionAgent',
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
        { key: 'sailorFullName',
          label: this.$i18n.t('sailor')
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
      sortName: null,
      url: null,
      typeDoc: this.$router.currentRoute.params['typeDoc'],
      firstIdEntry: this.$router.currentRoute.params['firstIdEntry'],
      secondIdEntry: this.$router.currentRoute.params['secondIdEntry']
    }
  },
  computed: {
    ...mapState({
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    })
  },
  mounted () {
    this.getReport()
  },
  methods: {
    getReport (link = null) {
      this.tableLoader = true
      if (link) {
        this.url = link
      } else {
        switch (this.typeDoc) {
          case 'sqc':
          case 'seaman':
            this.url = `api/v1/reports/back_office/distribution/${this.typeDoc}/sailor/?group=${this.firstIdEntry}&agent=${this.secondIdEntry}&${this.search}`
            this.fields.splice(1, 0, { key: 'rank', label: this.$i18n.t('rank') })
            break
          case 'portal':
          case 'sc':
            this.url = `api/v1/reports/back_office/distribution/${this.typeDoc}/sailor/?branch_office=${this.firstIdEntry}&agent=${this.secondIdEntry}&${this.search}`
            this.fields.splice(1, 0, { key: 'rank', label: this.$i18n.t('rank') })
            break
          case 'eti':
            this.url = `api/v1/reports/back_office/distribution/${this.typeDoc}/sailor/?institution=${this.firstIdEntry}&course=${this.secondIdEntry}&${this.search}`
            break
          case 'medical':
            this.url = `api/v1/reports/back_office/distribution/${this.typeDoc}/sailor/?medical=${this.firstIdEntry}&doctor=${this.secondIdEntry || 0}&${this.search}`
            this.fields.unshift({ key: 'number_document', label: this.$i18n.t('number') })
            this.fields.splice(2, 0, { key: 'position', label: this.$i18n.t('position') })
            break
          case 'dpd':
            this.url = `api/v1/reports/back_office/distribution/${this.typeDoc}/${this.secondIdEntry === 'passport' ? 'sailor_passport' : 'qual_doc'}/?branch_office=${this.firstIdEntry}&${this.search}`
            if (this.secondIdEntry === 'passport') {
              this.fields.unshift({ key: 'number_document', label: this.$i18n.t('number') })
            } else {
              this.fields.splice(1, 0, { key: 'rank', label: this.$i18n.t('rank') })
              this.fields.splice(2, 0, { key: 'list_positions', label: this.$i18n.t('position') })
            }
            break
        }
      }

      this.$api.get(this.url).then(response => {
        this.tableLoader = false
        if (response.code === 200) {
          if (this.secondIdEntry === 'qualification') {
            response.data.results.data.map(item => {
              item._list_positions = item.list_positions.map(position => position[this.labelName])
            })
          }
          this.items = response.data
          this.items.results = response.data.results.data
        }
      })
    },

    /** Generate excel document */
    saveExcelDoc () {
      const excelUrl = this.url.split('?').join('xlsx/?')
      this.$api.get(excelUrl).then(() => {
        this.$notification.success(this, this.$i18n.t('exсelStatement'))
      })
    }
  }
}
</script>
