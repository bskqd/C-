import { mapState } from 'vuex'
import { getDateFormat, getStatus } from '@/mixins/main'

export default {
  name: 'SailorMedicalStatementInfo',
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
