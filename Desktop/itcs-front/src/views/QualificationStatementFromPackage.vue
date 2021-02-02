<template>
  <div class="vx-card p-2">
    <Table
      :loader="tableLoader"
      :items="items.results"
      :fields="fields"
      :sortBy="sortBy"
      :sortDesc="sortDesc"
      :getDocuments="getPackageQualificationStatements"
      link="qualification-statements-info"
      type="qualificationPackageStatement"/>
    <Paginate
      :current="items.current"
      :next="items.next"
      :prev="items.previous"
      :count="items.count"
      :changePage="getPackageQualificationStatements"
    />
  </div>
</template>

<script>
import Paginate from '@/components/atoms/Paginate.vue'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'QualificationStatementFromPackage',
  components: {
    Paginate
  },
  data () {
    return {
      fields: [
        { key: 'number',
          label: this.$i18n.t('number')
        },
        { key: 'date_meeting',
          label: this.$i18n.t('dataEvent'),
          sortable: true
        },
        { key: 'portString',
          label: this.$i18n.t('port'),
          sortable: true
        },
        { key: 'type_document',
          label: this.$i18n.t('typeDoc'),
          sortable: true
        },
        { key: 'rank',
          label: this.$i18n.t('rank'),
          sortable: true
        },
        { key: 'list_positions',
          label: this.$i18n.t('position'),
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
      sortBy: 'number',
      filterMain: null,
      sortDesc: false,
      tableLoader: true,
      checkAccess
    }
  },
  computed: {
    ...mapState({
      labelName: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr'
    })
  },
  beforeCreate () {
    this.$store.commit('setActivePage', { name: 'qualificationPackageStatement',
      access: checkAccess('menuItem-qualificationPackageStatement') })
  },
  mounted () {
    this.getPackageQualificationStatements()
  },
  methods: {
    /** Get package qualification statements */
    getPackageQualificationStatements (page = null) {
      this.tableLoader = true
      const url = page || 'api/v1/reports/list_statement_qual_doc_in_packet/?page_size=20'
      this.$api.get(url).then(response => {
        this.tableLoader = false
        if (response.status === 'success') {
          response.data.results.map(item => {
            item._list_positions = item.list_positions.map(position => position[this.labelName])
            item.portString = item.port[this.labelName]
          })
          this.items = response.data
        }
      })
    }
  }
}
</script>
