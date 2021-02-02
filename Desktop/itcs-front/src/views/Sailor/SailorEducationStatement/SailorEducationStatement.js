import SailorEducationStatementAdd from './SailorEducationStatementAdd/SailorEducationStatementAdd.vue'
import { mapState } from 'vuex'

export default {
  name: 'SailorEducationStatement',
  components: {
    SailorEducationStatementAdd
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
          label: this.$i18n.t('dateStartEdu'),
          thClass: 'line-break'
        },
        { key: 'date_end_meeting',
          label: this.$i18n.t('dateEndEdu'),
          thClass: 'line-break'
        },
        { key: 'educational_institution',
          label: this.$i18n.t('nameInstitution'),
          thClass: 'line-break'
        },
        { key: 'level_qualification',
          label: this.$i18n.t('qualification'),
          thClass: 'line-break'
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
      items: state => state.sailor.educationStatement
    })
  }
}
