import { mapState } from 'vuex'

export default {
  name: 'SailorRecordBookLine',
  props: {
    serviceRecordBookId: [String, Number]
  },
  data () {
    return {
      fields: [
        { key: 'number_page_book',
          label: this.$i18n.t('numberPage')
        },
        { key: 'recordBookResponsibilities',
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
          class: 'mw-0'
        }
      ],
      sortBy: 'number_page_book',
      sortDesc: true
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      items: state => state.sailor.serviceRecordBookLine,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    })
  },
  mounted () {
    this.$store.dispatch('getRecordBookLineEntry', { id: this.id, service_book: this.serviceRecordBookId })
  }
}
