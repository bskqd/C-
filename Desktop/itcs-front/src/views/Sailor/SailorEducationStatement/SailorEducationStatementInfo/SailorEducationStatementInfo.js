import { getStatus, getDateFormat } from '@/mixins/main'
import { mapState } from 'vuex'

export default {
  name: 'SeafarerGraduationApplicationInfo',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      getStatus,
      getDateFormat
    }
  },
  computed: {
    ...mapState({
      labelName: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr'
    })
  }
}
