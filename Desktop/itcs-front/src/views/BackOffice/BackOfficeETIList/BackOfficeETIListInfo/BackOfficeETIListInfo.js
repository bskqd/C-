import { getDateFormat, getPaymentStatus } from '@/mixins/main'

export default {
  name: 'BackOfficeListInfoETI',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      fields: [
        { key: 'date_create',
          label: this.$i18n.t('createDate')
        },
        { key: 'date_modified',
          label: this.$i18n.t('dateModified')
        },
        { key: 'date_start',
          label: this.$i18n.t('dateEffective')
        },
        { key: 'date_end',
          label: this.$i18n.t('dateTermination')
        }
      ],
      getDateFormat,
      getPaymentStatus
    }
  }
}
