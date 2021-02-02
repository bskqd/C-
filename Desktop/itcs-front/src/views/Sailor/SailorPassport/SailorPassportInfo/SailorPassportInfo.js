import { mapState } from 'vuex'
import { hideDetailed, getStatus, getDateFormat } from '@/mixins/main'

export default {
  name: 'SailorPassportInfo',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      hideDetailed,
      getStatus,
      getDateFormat
    }
  },
  computed: {
    ...mapState({
      labelValue: state => state.main.lang === 'en' ? 'value_eng' : 'value',
      labelName: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr'
    })
  }
}
