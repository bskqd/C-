import CoefficientAdd from './BackOfficeCoefficientsAdd/BackOfficeCoefficientsAdd.vue'
import { mapState } from 'vuex'

export default {
  name: 'BackOfficeCoefficients',
  components: {
    CoefficientAdd
  },
  data () {
    return {
      fields: [
        { key: 'date_start',
          label: this.$i18n.t('dateEffective')
        },
        { key: 'date_end',
          label: this.$i18n.t('dateEnd')
        },
        { key: 'percent_of_eti',
          label: this.$i18n.t('etiPercent')
        },
        { key: 'percent_of_profit',
          label: this.$i18n.t('profitPercent')
        },
        { key: 'event',
          label: this.$i18n.t('actions'),
          class: 'mw-0'
        }
      ],
      sortBy: 'date_start',
      sortDesc: false,
      newDoc: false
    }
  },
  computed: {
    ...mapState({
      items: state => state.sailor.backOfficeCoefficient
    })
  }
}
