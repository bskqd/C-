import Paginate from '@/components/atoms/Paginate.vue'
import StatementsSearch from '@/components/molecules/ReportSearch/ReportSearch.vue'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'StatementAdvanceTraining',
  components: {
    Paginate,
    StatementsSearch
  },
  data () {
    return {
      fields: [
        { key: 'date_create',
          label: this.$i18n.t('createDate')
        },
        { key: 'number',
          label: this.$i18n.t('number')
        },
        { key: 'sailorFullName',
          label: this.$i18n.t('fullName')
        },
        { key: 'educational_institution',
          label: this.$i18n.t('nameInstitution')
        },
        { key: 'level_qualification',
          label: this.$i18n.t('qualification')
        },
        { key: 'date_meeting',
          label: this.$i18n.t('dateStartEdu')
        },
        { key: 'date_end_meeting',
          label: this.$i18n.t('dateEndEdu')
        },
        { key: 'is_payed',
          label: this.$i18n.t('payment')
        },
        { key: 'status_document',
          label: this.$i18n.t('status')
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
      tableLoader: false,
      checkAccess
    }
  },
  beforeCreate () {
    this.$store.commit('setActivePage', { name: 'statementAdvanceTraining', access: checkAccess('menuItem-statementAdvanceTraining') })
  },
  computed: {
    ...mapState({
      lang: state => state.main.lang,
      langFields: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    })
  },
  mounted () {
    this.getAdvanceTrainingStatements()
  },
  methods: {
    getAdvanceTrainingStatements (link = null) {
      this.tableLoader = true
      const url = link || `api/v1/reports/list/statement_advanced_training/?${this.params}`
      this.$api.get(url).then(response => {
        this.tableLoader = false
        if (response.status === 'success') {
          // response.data.results.map((item) => {
          //   item.nameInstitution = item.institution.name_ukr
          // })
          this.items = response.data
        }
      })
    },

    advanceTrainingSearch  (sort, params) {
      this.params = params
      const url = `api/v1/reports/list/statement_advanced_training/?${this.params}`
      this.getAdvanceTrainingStatements(url)
    }
  }
}
