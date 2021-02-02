import Page from '@/components/layouts/Page'
import { mapState } from 'vuex'

export default {
  name: 'UserNotification',
  components: {
    Page
  },
  data () {
    return {
      newNotifications: [],
      clearedNotifications: [],
      viewNewNotifications: true
    }
  },
  beforeCreate () {
    this.$store.commit('setActivePage', { name: 'userNotification', access: true })
  },
  computed: {
    ...mapState({
      userNotification: state => state.main.userNotification
    })
  },
  mounted () {
    this.getUserNotifications()
  },
  methods: {
    /** Get user notifications */
    getUserNotifications () {
      this.tableLoader = true
      this.$api.get(`api/v1/notifications/user_notification/`).then(response => {
        this.tableLoader = false
        if (response.status === 'success') {
          response.data.map(item => {
            item.behavior = {}
            item.sectionUrl = item.content_type === 'protocolfiles' ? '/report/excel' : null
          })
          this.newNotifications = response.data.filter(value => !value.is_hidden)
          this.clearedNotifications = response.data.filter(value => value.is_hidden)
        }
      })
    },

    /** Move notification to cleared list */
    readNotification (record) {
      const body = {
        is_hidden: true
      }
      this.$api.patch(`api/v1/notifications/user_notification/${record.id}/`, body).then(response => {
        if (response.status === 'success') {
          this.$notification.success(this, this.$i18n.t('moveNotification'))
          this.getUserNotifications()
        }
      })
    }
  }
}
