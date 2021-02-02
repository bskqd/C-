import { mapState } from 'vuex'
import SailorQualificationStatementAdd from './SailorQualificationStatementAdd/SailorQualificationStatementAdd.vue'

export default {
  name: 'SailorQualificationStatement',
  components: {
    SailorQualificationStatementAdd
  },
  data () {
    return {
      fields: [
        { key: 'number',
          label: this.$i18n.t('number')
        },
        { key: 'rank',
          label: this.$i18n.t('rank')
        },
        { key: 'list_positions',
          label: this.$i18n.t('position')
        },
        { key: 'qualificationStatementPort',
          label: this.$i18n.t('port')
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
      sortDesc: true,
      viewNewDoc: false
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      items: state => state.sailor.qualificationStatement
    })
  }
}
