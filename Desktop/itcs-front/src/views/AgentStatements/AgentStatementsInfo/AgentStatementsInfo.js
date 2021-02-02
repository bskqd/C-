import { hideDetailed, getStatus, getDateFormat } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'AgentStatementsInfo',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      getStatus,
      checkAccess,
      hideDetailed,
      getDateFormat
    }
  },
  computed: {
    ...mapState({
      langFields: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr'
    })
  }
}
