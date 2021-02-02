import { getDateFormat, getStatus } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorCertificationInfo',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      getDateFormat,
      checkAccess,
      getStatus
    }
  },
  computed: {
    ...mapState({
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    })
  }
}
