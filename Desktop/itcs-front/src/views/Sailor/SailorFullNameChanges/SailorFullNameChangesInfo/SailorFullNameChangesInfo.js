import { getDateFormat } from '@/mixins/main'
import { mapState } from 'vuex'

export default {
  name: 'SailorFullNameChangesInfo',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      getDateFormat
    }
  },
  computed: {
    ...mapState({
      labelName: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr'
    })
  }
}
