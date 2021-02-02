import BackOfficeCoursePriceAdd from './BackOfficeCoursePricesAdd/BackOfficeCoursePricesAdd.vue'
import { mapState } from 'vuex'

export default {
  name: 'BackOfficePrices',
  components: {
    BackOfficeCoursePriceAdd
  },
  data () {
    return {
      fields: [
        { key: 'date_start',
          label: this.$i18n.t('dateEffective')
        },
        { key: 'date_end',
          label: this.$i18n.t('dateTermination')
        },
        { key: 'course',
          label: this.$i18n.t('course')
        },
        { key: 'price',
          label: this.$i18n.t('price')
        },
        { key: 'type_of_form',
          label: this.$i18n.t('priceForm')
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
      items: state => state.sailor.backOfficeCoursePrice
    })
  }
}
