import SailorRecordBookAdd from './SailorRecordBookAdd/SailorRecordBookAdd.vue'
import { mapState } from 'vuex'

export default {
  name: 'SailorRecordBook',
  components: {
    SailorRecordBookAdd
  },
  data () {
    return {
      fields: [
        { key: 'name_book',
          label: this.$i18n.t('number')
        },
        { key: 'date_issued',
          label: this.$i18n.t('dateIssue')
        },
        { key: 'blank_strict_report',
          label: this.$i18n.t('strictBlank')
        },
        { key: 'branch_office',
          label: this.$i18n.t('affiliate')
        },
        { key: 'status',
          label: this.$i18n.t('status')
        },
        { key: 'event',
          label: this.$i18n.t('actions'),
          class: 'mw-0 position-relative'
        }
      ],
      sortBy: 'date_issued',
      sortDesc: true,
      newDoc: false
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      items: state => state.sailor.serviceRecordBook
    })
  }
}
