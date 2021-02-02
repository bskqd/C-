import { mapState } from 'vuex'
import SailorExperienceAdd from './SailorExperienceAdd/SailorExperienceAdd.vue'

export default {
  name: 'SailorExperience',
  components: {
    SailorExperienceAdd
  },
  data () {
    return {
      fields: [
        { key: 'record_type',
          label: this.$i18n.t('typeDoc')
        },
        { key: 'responsibilities',
          label: this.$i18n.t('responsibility')
        },
        { key: 'date_start',
          label: this.$i18n.t('hireDate')
        },
        { key: 'date_end',
          label: this.$i18n.t('fireDate')
        },
        { key: 'status_line',
          label: this.$i18n.t('status')
        },
        { key: 'event',
          label: this.$i18n.t('actions'),
          class: 'mw-0 position-relative'
        }
      ],
      sortBy: 'record_type',
      viewNewDoc: false,
      sortDesc: true
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      items: state => state.sailor.experience
    })
  }
}
