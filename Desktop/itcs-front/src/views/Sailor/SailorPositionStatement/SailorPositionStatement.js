import { mapState } from 'vuex'
import SailorPositionStatementAdd from './SailorPositionStatementAdd/SailorPositionStatementAdd.vue'

export default {
  name: 'SailorPositionStatement',
  components: {
    SailorPositionStatementAdd
  },
  data () {
    return {
      fields: [
        { key: 'created_at',
          label: this.$i18n.t('createDate')
        },
        { key: 'full_number',
          label: this.$i18n.t('number')
        },
        { key: 'service_center',
          label: this.$i18n.t('affiliate')
        },
        { key: 'positionStatementRank',
          label: this.$i18n.t('rank')
        },
        { key: 'list_positions',
          label: this.$i18n.t('position')
        },
        { key: 'includeSailorPass',
          label: this.$i18n.t('model-SailorPassport')
        },
        { key: 'positionStatementFullPrice',
          label: this.$i18n.t('price')
        },
        { key: 'is_payed',
          label: this.$i18n.t('payment')
        },
        { key: 'event',
          label: this.$i18n.t('actions'),
          class: 'mw-0 position-relative'
        }
      ],
      newDoc: false,
      sortDesc: false,
      sortBy: 'full_number'
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      items: state => state.sailor.positionStatement
    })
  }
}
