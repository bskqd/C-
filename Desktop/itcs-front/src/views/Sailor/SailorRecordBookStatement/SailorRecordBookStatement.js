import { mapState } from 'vuex'
import SailorRecordBookStatementAdd from './SailorRecordBookStatementAdd/SailorRecordBookStatementAdd.vue'

export default {
  name: 'SailorRecordBookStatement',
  components: {
    SailorRecordBookStatementAdd
  },
  data () {
    return {
      fields: [
        { key: 'date_created',
          label: this.$i18n.t('createDate')
        },
        { key: 'delivery',
          label: this.$i18n.t('delivery')
        },
        { key: 'is_payed',
          label: this.$i18n.t('payment')
        },
        { key: 'status_document',
          label: this.$i18n.t('status')
        },
        { key: 'event',
          label: this.$i18n.t('actions'),
          class: 'mw-0 position-relative'
        }
      ],
      viewNewDoc: false
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      items: state => state.sailor.recordBookStatement
    })
  }
}
