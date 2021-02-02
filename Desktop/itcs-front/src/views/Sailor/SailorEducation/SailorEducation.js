import SailorEducationAdd from './SailorEducationAdd/SailorEducationAdd.vue'
import { mapState } from 'vuex'

export default {
  name: 'SailorEducation',
  components: {
    SailorEducationAdd
  },
  data () {
    return {
      fields: [
        { key: 'number_document',
          label: this.$i18n.t('number')
        },
        { key: 'date_issue_document',
          label: this.$i18n.t('dateIssue')
        },
        { key: 'qualification',
          label: this.$i18n.t('qualification')
        },
        { key: 'speciality',
          label: `${this.$i18n.t('profession')} / ${this.$i18n.t('specialty')}`
        },
        { key: 'name_nz',
          label: this.$i18n.t('nameInstitution'),
          sortable: true
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
      items: state => state.sailor.education
    })
  }
}
