import { mapState } from 'vuex'
import ListItem from '@/components/atoms/ListItem'
import { FileTextIcon, FileIcon } from 'vue-feather-icons'
import { checkAccess } from '@/mixins/permissions'

export default {
  name: 'Menu',
  components: {
    FileTextIcon,
    FileIcon,
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
      selfHost: state => state.main.selfHost,
      version: state => state.main.version,
      userNotification: state => state.main.userNotification
    })
  }
}
