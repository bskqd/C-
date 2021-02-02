import { getStatus } from '@/mixins/main'
import { mapState } from 'vuex'

export default {
  name: 'SailorRecordBookStatementInfo',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      getStatus
    }
  },
  computed: {
    ...mapState({
      labelName: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr'
    })
  }
}
