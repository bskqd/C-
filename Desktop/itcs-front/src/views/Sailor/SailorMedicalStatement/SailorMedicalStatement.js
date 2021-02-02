import SailorMedicalStatementAdd from './SailorMedicalStatementAdd/SailorMedicalStatementAdd.vue'
import { mapState } from 'vuex'

export default {
  name: 'SeafarerMedicalApplication',
  components: {
    SailorMedicalStatementAdd
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
        { key: 'date_meeting',
          label: this.$i18n.t('dateReceipt')
        },
        { key: 'medical_institution',
          label: this.$i18n.t('medicalInstitution')
        },
        { key: 'position',
          label: this.$i18n.t('position')
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
      viewNewDoc: false,
      sortDesc: false,
      sortBy: 'number'
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      items: state => state.sailor.medicalStatement
    })
  }
}
