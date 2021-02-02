import { mapState } from 'vuex'
import SailorPassportAdd from './SailorPassportAdd/SailorPassportAdd.vue'

export default {
  name: 'SailorPassport',
  components: {
    SailorPassportAdd
  },
  data () {
    return {
      fields: [
        { key: 'number_document',
          label: this.$i18n.t('number'),
          sortable: true
        },
        { key: 'sailorPassportPort',
          label: this.$i18n.t('port'),
          sortable: true
        },
        { key: 'date_start',
          label: this.$i18n.t('dateIssue'),
          sortable: true
        },
        { key: 'date_end',
          label: this.$i18n.t('dateTermValid'),
          sortable: true
        },
        { key: 'status_document',
          label: this.$i18n.t('status'),
          sortable: true
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
      items: state => state.sailor.sailorPassport,
      labelName: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr'
    })
  }
}
