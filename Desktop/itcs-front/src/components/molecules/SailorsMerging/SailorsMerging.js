import { mapState } from 'vuex'
import i18n from '@/locale'

export default {
  name: 'SailorsMerging',
  data () {
    return {
      sailorID: null,
      availableSailor: [],
      showSailorsMerging: false
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    })
  },
  mounted () {
    this.getAvailableSailor()
  },
  methods: {
    getAvailableSailor () {
      this.$api.get(`api/v2/sailor/${this.id}/merge_sailor/`).then(response => {
        if (response.code === 200) {
          this.availableSailor = response.data
        }
      })
    },

    mergeSailors () {
      this.$swal({
        title: i18n.t('warning'),
        text: i18n.t('sailorMergeWarning'),
        icon: 'info',
        buttons: [this.$i18n.t('cancel'), this.$i18n.t('confirm')],
        dangerMode: true
      }).then(confirmation => {
        if (confirmation) {
          const body = { old_sailor: this.sailorID }
          this.$api.post(`api/v2/sailor/${this.id}/merge_sailor/`, body).then(response => {
            if (response.code === 200) {
              this.$notification.success(this, this.$i18n.t('successSailorMerge'))
              this.$store.dispatch('getSailorInformation', this.id)
              this.showSailorsMerging = false
            }
          })
        }
      })
    }
  }
}
