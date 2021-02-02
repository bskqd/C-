import { mapState } from 'vuex'
import { getDateFormat } from '@/mixins/main'

export default {
  name: 'MainSailorHistory',
  data () {
    return {
      cardLoader: true,
      sailors: [],
      getDateFormat
    }
  },
  computed: {
    ...mapState({
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    })
  },
  mounted () {
    this.getSailors()
  },
  methods: {
    getSailors () {
      this.$api.get('api/v1/auth/get_user_history/').then(response => {
        this.cardLoader = false
        if (response.code === 200) {
          this.sailors = response.data
          this.sailors.filter(value => {
            this.$api.getPhoto('media/' + value.photo).then((photo) => {
              value.photo = photo
            })
          })
          console.log(this.sailors)
        }
      })
    }
  }
}
