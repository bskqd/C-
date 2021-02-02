import SailorPassportStatementAdd from './SailorPassportStatementAdd/SailorPassportStatementAdd.vue'
import { mapState } from 'vuex'

export default {
  name: 'SailorPassportStatement',
  components: {
    SailorPassportStatementAdd
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
        { key: 'qualificationStatementPort',
          label: this.$i18n.t('port')
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
      sortBy: 'number',
      newDoc: false,
      sortDesc: false
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      items: state => state.sailor.sailorPassportStatement,
      labelName: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr'
    })
  }
}
