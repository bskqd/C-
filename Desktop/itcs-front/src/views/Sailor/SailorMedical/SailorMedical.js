import SailorMedicalAdd from './SailorMedicalAdd/SailorMedicalAdd.vue'
import { mapState } from 'vuex'

export default {
  name: 'SailorMedical',
  components: {
    SailorMedicalAdd
  },
  data () {
    return {
      fields: [
        { key: 'number',
          label: this.$i18n.t('number')
        },
        { key: 'position',
          label: this.$i18n.t('position')
        },
        { key: 'limitation',
          label: this.$i18n.t('limitation')
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
      items: state => state.sailor.sailorMedical
    })
  }
}
