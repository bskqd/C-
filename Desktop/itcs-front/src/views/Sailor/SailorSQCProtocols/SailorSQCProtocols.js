import { mapState } from 'vuex'
import SailorSQCProtocolsAdd from './SailorSQCProtocolsAdd/SailorSQCProtocolsAdd.vue'

export default {
  name: 'SailorSQCProtocols',
  components: {
    SailorSQCProtocolsAdd
  },
  data () {
    return {
      fields: [
        {
          key: 'number_document',
          label: this.$i18n.t('number'),
          tdClass: 'number-table'
        },
        { key: 'rank',
          label: `${this.$i18n.t('qualification')} - ${this.$i18n.t('rank')}`
        },
        {
          key: 'list_positions',
          label: this.$i18n.t('position')
        },
        {
          key: 'date_meeting',
          label: this.$i18n.t('meetingDate')
        },
        {
          key: 'decision',
          label: this.$i18n.t('solution'),
          tdClass: 'status-table'
        },
        {
          key: 'status_document',
          label: this.$i18n.t('status'),
          tdClass: 'status-table'
        },
        {
          key: 'event',
          label: this.$i18n.t('actions'),
          class: 'mw-0 position-relative'
        }
      ],
      sortBy: 'number',
      sortDesc: true,
      newDoc: false
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      items: state => state.sailor.sailorSQCProtocols
    })
  }
}
