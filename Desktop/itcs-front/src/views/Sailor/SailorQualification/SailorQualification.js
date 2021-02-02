import { mapState } from 'vuex'
import SailorQualificationAdd from './SailorQualificationAdd/SailorQualificationAdd.vue'

export default {
  name: 'SailorQualification',
  components: {
    SailorQualificationAdd
  },
  data () {
    return {
      fields: [
        { key: 'qualificationNumber',
          label: this.$i18n.t('number'),
          tdClass: 'numberColumn',
          thClass: 'numberColumn'
        },
        { key: 'type_document',
          label: this.$i18n.t('typeDoc')
        },
        { key: 'rank',
          label: this.$i18n.t('rank')
        },
        { key: 'list_positions',
          label: this.$i18n.t('position')
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
      items: state => state.sailor.qualification
    })
  }
}
