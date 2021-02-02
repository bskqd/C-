import { setSearchDelay } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'

export default {
  name: 'Search',
  data () {
    return {
      setSearch: false,
      search: null,
      sailors: [],
      emptySearchResult: false,
      delaySearch: null,
      checkAccess
    }
  },
  methods: {
    /** Call setTimeOut mixin for search */
    startSearch () {
      setSearchDelay(this, this.search, 'delaySearch')
    },

    goSearch (searchResult) {
      this.setSearch = false
      if (this.search.length >= 3) {
        this.setSearch = true

        let url, method, body
        if (checkAccess('admin') || !checkAccess('main-search')) {
          url = 'api/v1/sailor/search_sailor/'
          method = 'post'
          body = { query: searchResult }
        } else {
          url = `api/v1/seaman/search_sailor/query=${searchResult}/`
          method = 'get'
        }

        this.$api[method](url, body || null)
          .then(response => {
            this.sailors = []
            if (response.status === 'success' && response.data.length) {
              this.emptySearchResult = false
              this.sailors = response.data
            } else this.emptySearchResult = true
          })
      }
    }
  }
}
