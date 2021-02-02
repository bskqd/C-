import { getDateFormat, getStatus } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorMedicalInfo',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      getStatus,
      checkAccess,
      getDateFormat
    }
  },
  computed: {
    ...mapState({
      labelName: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr'
    })
  }
}
