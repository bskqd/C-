import { mapState } from 'vuex'
import { getDateFormat, getStatus } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'

export default {
  name: 'SailorExperienceInfo',
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
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    })
  }
}
