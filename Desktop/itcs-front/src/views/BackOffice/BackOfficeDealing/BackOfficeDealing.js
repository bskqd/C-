import { mapState } from 'vuex'

export default {
  name: 'BackOfficeDealing',
  data () {
    return {
      fields: [
        { key: 'etiCourseName',
          label: this.$i18n.t('course'),
          sortable: true
        },
        { key: 'event',
          label: this.$i18n.t('actions'),
          class: 'mw-0'
        }
      ]
    }
  },
  computed: {
    ...mapState({
      items: state => state.sailor.backOfficeDealing
    })
  }
}
