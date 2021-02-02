import Paginate from '@/components/atoms/Paginate.vue'
import StatementsSearch from '@/components/molecules/ReportSearch/ReportSearch.vue'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'StatementETI',
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
        { key: 'course',
          label: this.$i18n.t('course')
        },
        { key: 'nameInstitution',
          label: this.$i18n.t('nameInstitution')
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
    this.$store.commit('setActivePage', { name: 'statementETI', access: checkAccess('menuItem-statementETI') })
  },
  computed: {
    ...mapState({
      lang: state => state.main.lang,
      langFields: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    })
  },
  mounted () {
    this.getStatementsETIList()
  },
  methods: {
    getStatementsETIList (link = null) {
      this.tableLoader = true
      const url = link || `api/v1/reports/list/statement_eti/?${this.params}`
      this.$api.get(url).then(response => {
        this.tableLoader = false
        if (response.status === 'success') {
          response.data.results.map((item) => {
            item.nameInstitution = item.institution.name_ukr
          })
          this.items = response.data
        }
      })
    },

    sailorETIStatementsSearch (sort, params) {
      this.params = params
      const url = `api/v1/reports/list/statement_eti/?${this.params}`
      this.getStatementsETIList(url)
    }
  }
}
