import ReportSearch from '@/components/molecules/ReportSearch/ReportSearch.vue'
import Paginate from '@/components/atoms/Paginate.vue'
import { goBack, getDateFormat, viewDetailedBlock, showDetailed } from '@/mixins/main'

export default {
  name: 'DocListFinancialReport',
  components: {
    ReportSearch,
    Paginate
  },
  data () {
    return {
      fields: [
        { key: 'number',
          label: this.$i18n.t('number')
        },
        { key: 'payment_date',
          label: this.$i18n.t('paymentDate')
        },
        { key: 'price_form1',
          label: `${this.$i18n.t('price')} ${this.$i18n.t('firstForm')}`
        },
        { key: 'sum_to_distribution_f1',
          label: `${this.$i18n.t('total')} ${this.$i18n.t('firstForm')}`
        },
        { key: 'price_form2',
          label: `${this.$i18n.t('price')} ${this.$i18n.t('secondForm')}`
        },
        { key: 'sum_to_distribution_f2',
          label: `${this.$i18n.t('total')} ${this.$i18n.t('secondForm')}`
        },
        { key: 'profit',
          label: this.$i18n.t('profit')
        },
        { key: 'document_info',
          label: this.$i18n.t('documentInfo')
        },
        { key: 'event',
          label: this.$i18n.t('actions'),
          class: 'mw-0'
        }
      ],
      items: {},
      resultSearchTitle: null,
      tableLoader: false,
      viewDetailedBlock,
      getDateFormat,
      showDetailed,
      goBack
    }
  },
  // mounted () {
  //   this.$store.dispatch('getAllAccrualTypeDoc')
  // },
  methods: {
    /** Get financial report */
    getFinancialReport (sort = '', params = '', link = '') {
      this.tableLoader = true
      if (params) this.params = params
      if (sort) {
        params = this.params
        params.set('ordering', sort)
      }

      let url = `api/v1/back_off/list/packets/?${params}`
      if (link) url = link

      this.$api.get(url).then(response => {
        this.tableLoader = false
        if (response.status === 'success') {
          response.data.results.map(item => {
            item.behavior = {}
          })
          this.items = response.data
        }
      })
    },

    changePage (link) {
      this.getFinancialReport('', '', link)
    }
  }
}
