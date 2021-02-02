import { hideDetailed } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'BackOfficeCoursesInfo',
  props: {
    row: Object,
    getDocuments: Function
  },
  data () {
    return {
      fields: [
        { key: 'full_number_protocol',
          label: this.$i18n.t('numberProtocol')
        },
        { key: 'date_start',
          label: this.$i18n.t('dateEffective')
        },
        { key: 'date_end',
          label: this.$i18n.t('dateTermination')
        },
        { key: 'course',
          label: this.$i18n.t('course')
        },
        { key: 'is_disable',
          label: this.$i18n.t('status')
        },
        { key: 'event',
          label: this.$i18n.t('actions'),
          class: 'mw-0'
        }
      ],
      items: this.row.item.eti_registry,
      sortBy: 'date_start',
      sortDesc: true,
      hideDetailed,
      checkAccess
    }
  },
  computed: {
    ...mapState({
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    })
  }
}
