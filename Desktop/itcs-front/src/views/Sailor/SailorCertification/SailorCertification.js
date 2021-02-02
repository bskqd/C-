import { mapState } from 'vuex'
import SailorCertificationAdd from './SailorCertificationAdd/SailorCertificationAdd.vue'

export default {
  name: 'SailorCertification',
  components: {
    SailorCertificationAdd
  },
  data () {
    return {
      fields: [
        { key: 'ntz_number',
          label: this.$i18n.t('number'),
          tdClass: 'tableNumber'
        },
        { key: 'ntz',
          label: this.$i18n.t('passportIssued'),
          tdClass: 'ellipsis'
        },
        { key: 'course_traning',
          label: this.$i18n.t('course'),
          tdClass: 'ellipsis'
        },
        { key: 'date_start',
          label: this.$i18n.t('dateIssue'),
          tdClass: 'tableDate',
          sortable: true
        },
        { key: 'date_end',
          label: this.$i18n.t('dateEnd'),
          tdClass: 'tableDate',
          sortable: true
        },
        { key: 'status_document',
          label: this.$i18n.t('status'),
          tdClass: 'tableStatus'
        },
        { key: 'event',
          label: this.$i18n.t('actions'),
          class: 'mw-0 position-relative'
        }
      ],
      sortBy: 'ntz_number',
      sortDesc: true,
      viewNewDoc: false
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      items: state => state.sailor.certification
    })
  }
}
