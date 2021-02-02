import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'NewAgents',
  data () {
    return {
      fields: [
        { key: 'date_create',
          label: this.$i18n.t('createDate')
        },
        { key: 'fullName',
          label: this.$i18n.t('fullName'),
          sortable: true
        },
        { key: 'city',
          label: this.$i18n.t('city'),
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
      sortBy: 'fullName',
      sortDesc: false,
      newDoc: false,
      checkAccess
    }
  },
  beforeCreate () {
    this.$store.commit('setActivePage', { name: 'newAgents', access: checkAccess('menuItem-agentsStatement') })
  },
  computed: {
    ...mapState({
      items: state => state.sailor.newAgents
    })
  }
}
