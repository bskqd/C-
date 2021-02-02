import { mapState } from 'vuex'
import { getDateFormat } from '@/mixins/main'

export default {
  name: 'SailorCitizenPassportInfo',
  props: {
    data: Object
  },
  data () {
    return {
      getDateFormat
    }
  },
  computed: {
    ...mapState({
      labelValue: state => (state.main.lang === 'en') ? 'value_eng' : 'value'
    })
  }
}
