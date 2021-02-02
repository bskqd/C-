import Paginate from '@/components/atoms/Paginate.vue'
import StatementsSearch from '@/components/molecules/ReportSearch/ReportSearch.vue'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'PaymentsETI',
  components: {
    Paginate,
    StatementsSearch
  },
  data () {
    return {
      fields: [
        { key: 'pay_time',
          label: this.$i18n.t('paymentDate')
        },
        { key: 'platon_id',
          label: this.$i18n.t('paymentId')
        },
        { key: 'full_name',
          label: this.$i18n.t('fullName')
        },
        { key: 'eti-course',
          label: this.$i18n.t('course')
        },
        { key: 'eti-institution',
          label: this.$i18n.t('nameInstitution')
        },
        { key: 'amount',
          label: this.$i18n.t('amount')
        },
        { key: 'event',
          label: this.$i18n.t('actions'),
          class: 'mw-0'
        }
      ],
      items: [],
      todayDate: new Date(),
      params: new URLSearchParams({
        page_size: 20,
        from_pay_date: this.todayDate
      }),
      tableLoader: false,
      checkAccess
    }
  },
  beforeCreate () {
    this.$store.commit('setActivePage', { name: 'etiPayments', access: checkAccess('menuItem-etiPayments') })
  },
  computed: {
    ...mapState({
      lang: state => state.main.lang,
      langFields: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    })
  },
  mounted () {
    this.todayDate = new Date()
    this.params.set('from_pay_date', this.todayDate.toISOString().split('T')[0])
    this.getPaymentsETI()
  },
  methods: {
    getPaymentsETI (link = null, sort) {
      this.tableLoader = true
      if (sort) {
        this.params.set('ordering', sort)
      }
      const url = link || `api/v1/reports/list/payment/statement_eti/?${this.params}`
      this.$api.get(url).then(response => {
        this.tableLoader = false
        if (response.status === 'success') {
          response.data.results.map((item) => {
            item.amount = `${item.amount} ${this.$i18n.t('uah')}`
          })
          this.items = response.data
        }
      })
    },

    sailorPaymentsETISearch (sort, params) {
      this.params = params
      const url = `api/v1/reports/list/payment/statement_eti/?${this.params}`
      this.getPaymentsETI(url)
    }
  }
}
