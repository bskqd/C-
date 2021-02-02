import { getDateFormat, getPaymentStatus } from '@/mixins/main'
import { mapState } from 'vuex'

export default {
  name: 'BackOfficeCoursesInfo',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      getDateFormat,
      getPaymentStatus
    }
  },
  computed: {
    ...mapState({
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    })
  }
}
