import SailorSQCStatementAdd from './SailorSQCStatementAdd/SailorSQCStatementAdd.vue'
import { mapState } from 'vuex'

export default {
  name: 'SailorSQCStatement',
  components: {
    SailorSQCStatementAdd
  },
  data () {
    return {
      fields: [
        { key: 'date_create',
          label: this.$i18n.t('createDate')
        },
        { key: 'number',
          label: this.$i18n.t('number')
        },
        { key: 'rank',
          label: `${this.$i18n.t('qualification')} - ${this.$i18n.t('rank')}`
        },
        { key: 'list_positions',
          label: this.$i18n.t('position')
        },
        { key: 'statementDecision',
          label: this.$i18n.t('solution')
        },
        { key: 'status_document',
          label: this.$i18n.t('status')
        },
        { key: 'event',
          label: this.$i18n.t('actions'),
          class: 'mw-0 position-relative'
        }
      ],
      sortBy: 'number',
      newDoc: false,
      sortDesc: true
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      items: state => state.sailor.sailorSQCStatement
    })
  }
}
