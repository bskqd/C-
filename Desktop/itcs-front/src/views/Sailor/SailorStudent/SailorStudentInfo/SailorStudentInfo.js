import { getDateFormat, getStatus } from '@/mixins/main'
import { mapState } from 'vuex'

export default {
  name: 'SailorStudentInfo',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      getDateFormat,
      getStatus
    }
  },
  computed: {
    ...mapState({
      labelName: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr'
    })
  }
}
