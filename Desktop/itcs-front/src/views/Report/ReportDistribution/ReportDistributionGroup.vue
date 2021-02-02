<template>
  <div>
    <b-card>
      <ReportSearch
        report="distribution"
        ref="search"
        :getReport="getReport"
      />
    </b-card>
    <b-card>
      <Table
        :loader="tableLoader"
        :items="items.results"
        :fields="fields"
        :sortBy="sortAcs"
        :sortAcs="sortAcs"
        :sortDesc="sortDesc"
        :getDocuments="getReport"
        :saveExcel="saveExcelDoc"
        type="reportDistributionGroup"/>
      <Paginate
        :current="items.current"
        :next="items.next"
        :prev="items.previous"
        :count="items.count"
        :changePage="changePage" />
    </b-card>
  </div>
</template>

<script>
import Table from '@/components/layouts/Table/Table.vue'
import ReportSearch from '@/components/molecules/ReportSearch/ReportSearch.vue'
import Paginate from '@/components/atoms/Paginate.vue'
import { mapState } from 'vuex'

export default {
  name: 'ReportDistribution',
  components: {
    Table,
    ReportSearch,
    Paginate
  },
  data () {
    return {
      items: [],
      fields: [],
      tableLoader: false,
      sortAcs: null,
      sortDesc: null,
      sortName: null,
      params: null
    }
  },
  computed: {
    ...mapState({
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    })
  },
  methods: {
    getReport (sort = '', params = '', link = null) {
      this.tableLoader = true
      this.items = []
      // Add general table fields (same for each document type)
      this.fields = [
        { key: 'count', label: this.$i18n.t('itemsAmount') },
        { key: 'distribution_sum', label: this.$i18n.t('distribution') },
        { key: 'profit_sum', label: this.$i18n.t('profit') },
        { key: 'event', label: this.$i18n.t('go'), class: 'mw-0' }]

      this.params = params
      const url = link || `api/v1/reports/back_office/distribution/${this.$refs.search.dataForm.distributionType.value}/?${params}`
      this.$api.get(url).then(response => {
        this.tableLoader = false
        if (response.code === 200) {
          response.data.results.data.map(item => {
            item.searchParams = params
            item.allowSaveExcel = this.$refs.search.dataForm.distributionType.value === 'eti'
            switch (this.$refs.search.dataForm.distributionType.value) {
              case 'sqc':
              case 'seaman':
                item.link = `distribution/${this.$refs.search.dataForm.distributionType.value}/seaman/${item.group ? item.group.id : 0}`
                if (!this.fields.find(column => column.key === 'group')) {
                  this.fields.unshift({ key: 'group', label: this.$i18n.t('group') })
                }
                break
              case 'eti':
                item.link = `distribution/${this.$refs.search.dataForm.distributionType.value}/seaman/${item.eti.id}`
                if (!this.fields.find(column => column.key === 'eti')) {
                  this.fields.unshift({ key: 'eti', label: this.$i18n.t('eti') })
                }
                break
              case 'medical':
                item.link = `distribution/${this.$refs.search.dataForm.distributionType.value}/seaman/${item.medical_institution.id}`
                if (!this.fields.find(column => column.key === 'medical_institution')) {
                  this.fields.unshift({ key: 'medical_institution', label: this.$i18n.t('medicalInstitution') })
                }
                break
              case 'dpd':
                item.link = `distribution/${this.$refs.search.dataForm.distributionType.value}/seaman/${item.branch_office.id}`
                if (!this.fields.find(column => column.key === 'branch_office')) {
                  this.fields.splice(0, 1, { key: 'branch_office', label: this.$i18n.t('affiliate') })
                }
                break
              case 'portal':
              case 'sc':
                item.link = `distribution/${this.$refs.search.dataForm.distributionType.value}/seaman/${item.branch_office.id}`
                if (!this.fields.find(column => column.key === 'branch_office')) {
                  this.fields.unshift({ key: 'branch_office', label: this.$i18n.t('affiliate') })
                }
                break
              case 'adv_training':
                item.link = `distribution/${this.$refs.search.dataForm.distributionType.value}/seaman/${item.level_qualification.id}`
                if (!this.fields.find(column => column.key === 'level_qualification')) {
                  this.fields.unshift({ key: 'level_qualification', label: this.$i18n.t('qualification') })
                }
                break
            }
          })
          this.items = response.data
          this.items.results = response.data.results.data
        }
      })
    },

    changePage (link) {
      this.getReport('', '', link)
    },

    saveExcelDoc (row) {
      const params = this.params
      params.set('institution', row.item.eti.id)
      const url = `api/v1/reports/back_office/distribution/eti/sailor/xlsx/?${params}`
      this.$api.get(url).then(() => {
        this.$notification.success(this, this.$i18n.t('exсelStatement'))
      })
    }
  }
}
</script>
