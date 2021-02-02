import { mapState } from 'vuex'
import { getDateFormat } from '@/mixins/main'
import Paginate from '@/components/atoms/Paginate'

export default {
  name: 'MainForAgent',
  components: {
    Paginate
  },
  data () {
    return {
      cardLoader: true,
      sailors: [],
      getDateFormat
    }
  },
  computed: {
    ...mapState({
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      labelLang: state => (state.main.lang === 'en') ? 'eng' : 'ukr'
    })
  },
  mounted () {
    this.getSailor()
  },
  methods: {
    getSailor (page = null) {
      this.cardLoader = true
      const url = page || 'api/v1/seaman/sailors/?page_size=20'
      this.$api.get(url).then(response => {
        this.cardLoader = false
        if (response.code === 200) {
          console.log(response.data.results)
          response.data.results.filter((val) => {
            this.$api.getPhoto('media/' + val.photo).then((photo) => {
              val.photo = photo
            })
          })
          this.sailors = response.data
          console.log(this.sailors)
        }
      })
    }
  }
}
