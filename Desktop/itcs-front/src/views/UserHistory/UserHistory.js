import Paginate from '@/components/atoms/Paginate.vue'
import UserHistorySearch from '@/components/molecules/ReportSearch/ReportSearch.vue'
import { viewDetailedBlock, showDetailed, goBack } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'

export default {
  name: 'UserHistory',
  components: {
    Paginate,
    UserHistorySearch
  },
  data () {
    return {
      checkAccess,
      fields: [
        { key: 'datetime',
          label: this.$i18n.t('dateModified'),
          tdClass: 'w-15'
        },
        { key: 'sailor_key',
          label: this.$i18n.t('sailorId'),
          class: 'mw-0'
        },
        { key: 'full_user_name',
          label: this.$i18n.t('fullName')
        },
        { key: 'model',
          label: this.$i18n.t('typeDoc'),
          tdClass: 'w-15'
        },
        { key: 'event',
          label: this.$i18n.t('actions'),
          class: 'mw-0'
        }
      ],
      items: [],
      user: null,
      periodStart: null,
      periodEnd: null,
      tableLoader: false,
      buttonLoader: false,
      viewSearch: true,
      params: new URLSearchParams({
        page_size: 20
      }),
      viewDetailedBlock,
      showDetailed,
      goBack
    }
  },
  beforeCreate () {
    this.$store.commit('setActivePage', { name: 'userHistory', access: checkAccess('user-history') })
  },
  methods: {
    getUserHistory (link = null) {
      this.tableLoader = true
      const url = link || `api/v1/auth/history/?${this.params}`
      this.$api.get(url).then(response => {
        this.tableLoader = false
        if (response.code === 200) {
          response.data.results.map(item => {
            item.behavior = {}
            item.sailor = item.sailor_key
            item.model = `model-${item.module.replace(/ /g, '')}`
          })
          this.items = response.data
        }
      })
    },

    userHistorySearch (sort, params) {
      this.params = params
      const url = `api/v1/auth/history/?${this.params}`
      this.getUserHistory(url)
    }
  }
}
