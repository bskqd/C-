import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import SailorRecordBookLine from '../SailorRecordBookLine/SailorRecordBookLine.vue'
import { getStatus, getDateFormat } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorRecordBookInfo',
  props: {
    sailorDocument: Object
  },
  components: {
    ValidationAlert,
    SailorRecordBookLine
  },
  data () {
    return {
      API: process.env.VUE_APP_API,
      showStatementSaving: false,
      strictBlank: null,
      getStatus,
      checkAccess,
      getDateFormat
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    })
  },
  methods: {
    /* Save documents as docx */
    saveDocument () {
      const body = {
        doc_id: this.sailorDocument.id
      }
      this.$api.post(`api/v1/docs/auth_service_record/`, body).then(response => {
        if (response.status === 'success') {
          window.open(this.API + 'docs/generate_service_record/' + response.data.token, '_blank')
        }
      })
    },

    /** Save service record book statement */
    saveApplicationDocument () {
      const body = {
        service_record: this.sailorDocument.id,
        num_blank: this.strictBlank
      }
      this.$api.post(`api/v1/docs/auth_statement_for_record_book/`, body).then(response => {
        if (response.status === 'success') {
          window.open(this.API + 'docs/generate_statemenet_for_record_book/' + response.data.token, '_blank')
          this.$store.dispatch('getRecordBooks', this.id)
        }
      })
    }
  }
}
