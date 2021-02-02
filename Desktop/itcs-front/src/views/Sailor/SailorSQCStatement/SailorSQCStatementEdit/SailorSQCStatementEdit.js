import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { hideDetailed } from '@/mixins/main'
import { mapState } from 'vuex'

export default {
  name: 'SailorSQCStatementEdit',
  props: {
    sailorDocument: Object
  },
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      buttonLoader: false,
      hideDetailed
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      lang: state => state.main.lang
    })
  },
  methods: {
    /** Edit document information */
    saveEditedApplication () {
      this.buttonLoader = true
      const body = {
        date_meeting: this.sailorDocument.date_meeting
      }
      this.$api.patch(`api/v2/sailor/${this.id}/statement/protocol_sqc/${this.sailorDocument.id}/`, body).then(response => {
        this.buttonLoader = false
        if (response.status === 'success') {
          const files = this.$refs.mediaContent.filesArray
          if (files.length) {
            this.$api.postPhoto(files, 'StatementSqp', response.data.id).then((response) => {
              if (response.status !== 'created' && response.status !== 'success') {
                this.$notification.error(this, this.$i18n.t('errorAddFile'))
              }
            })
          }
          this.$notification.success(this, this.$i18n.t('changedStatementSQC'))
          this.$store.commit('updateDataSailor', { type: 'sailorSQCStatement', value: response.data })
        }
      })
    },

    dateDisabled (ymd, date, row) {
      const weekday = date.getDay()
      const day = date.getDate()
      let r = weekday === 0 || weekday === 6 || day === 13
      if (row.disabled_dated) {
        let s = row.disabled_dated.map(val => {
          return ymd >= val[0] && ymd <= val[1] && r
        })
        return s.includes(true)
      } else return r
    }
  }
}
