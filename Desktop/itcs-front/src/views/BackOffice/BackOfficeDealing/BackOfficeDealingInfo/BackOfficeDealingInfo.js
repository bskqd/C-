import { mapState } from 'vuex'
import { hideDetailed } from '@/mixins/main'

export default {
  name: 'BackOfficeDealingInfo',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      fields: [
        { key: 'ntz',
          label: this.$i18n.t('eti'),
          sortable: true
        },
        { key: 'ratio',
          label: this.$i18n.t('ratio')
        }
      ],
      hideDetailed
    }
  },
  computed: {
    ...mapState({
      labelName: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr'
    })
  }
}
