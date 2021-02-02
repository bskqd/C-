import SailorFullNameChangesAdd from './SailorFullNameChangesAdd/SailorFullNameChangesAdd.vue'
import { mapState } from 'vuex'

export default {
  name: 'SailorFullNameChanges',
  components: {
    SailorFullNameChangesAdd
  },
  data () {
    return {
      fields: [
        { key: 'oldFullName',
          label: this.$i18n.t('fullNameBefore')
        },
        { key: 'newFullName',
          label: this.$i18n.t('fullNameAfter')
        },
        { key: 'change_date',
          label: this.$i18n.t('dateModified')
        },
        { key: 'date_create',
          label: this.$i18n.t('createDate')
        },
        { key: 'event',
          label: this.$i18n.t('actions'),
          class: 'mw-0 position-relative'
        }
      ],
      sortBy: 'change_date',
      sortDesc: true,
      newDoc: false
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      items: state => state.sailor.sailorFullNameChanges,
      labelName: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr'
    })
  }
}
