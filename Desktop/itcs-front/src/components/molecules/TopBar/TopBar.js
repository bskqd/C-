import Search from '@/components/molecules/Search/Search.vue'
import ListItem from '@/components/atoms/ListItem'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'TopBar',
  components: {
    Search,
    ListItem
  },
  props: {
    active: String
  },
  data () {
    return {
      checkAccess
    }
  },
  computed: {
    ...mapState({
      lang: state => state.main.lang,
      userNotification: state => state.main.userNotification,
      username: state => state.main.user.name,
      login: state => state.main.user.username,
      userId: state => state.main.user.id
    })
  },
  mounted () {
    this.getInfoNotify()
  },
  methods: {
    logout () {
      localStorage.removeItem('Token')
      window.location = '/login'
    },

    getImgByLang () {
      let images = require.context('@/assets/img/', false, /\.svg$/)
      return images('./Flag_' + this.lang + '.svg')
    },

    getInfoNotify () {
      this.$api.get('api/v1/auth/user_notification/').then(response => {
        if (response.code === 200) {
          this.$store.commit('setUserNotification', response.data)
        }
      })
    }
  }
}
