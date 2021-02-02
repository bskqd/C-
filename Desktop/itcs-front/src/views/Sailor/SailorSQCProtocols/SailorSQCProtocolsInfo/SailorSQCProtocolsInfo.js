import Signature from '@/components/molecules/Signature/Signature.vue'
import { getStatus, regenerationConfirmation, getDateFormat } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorSQCProtocolsInfo',
  props: {
    sailorDocument: Object
  },
  components: {
    Signature
  },
  data () {
    return {
      API: process.env.VUE_APP_API,
      getDateFormat,
      checkAccess,
      getStatus
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    }),
    basedStatementSQC () {
      return this.$store.getters.sailorDocumentByID({ type: 'sailorSQCStatement', id: this.sailorDocument.statement_dkk })
    }
  },
  methods: {
    /** Save protocol with conclusion as docx */
    saveDocument () {
      const body = {
        doc_id: this.sailorDocument.id
      }
      this.$api.post(`api/v1/docs/auth_protocol_dkk/`, body).then(response => {
        if (response.status === 'success') {
          window.open(`${this.API}docs/generate_protocol_with_conclusion/${response.data.token}/`, '_blank')
        }
      })
    },

    saveDocWithSign () {
      const body = {
        doc_id: this.sailorDocument.id
      }
      this.$api.post(`api/v1/docs/auth_protocol_dkk/`, body).then(response => {
        if (response.status === 'success') {
          window.open(`${this.API}docs/download_signed_protocol/${response.data.token}/`, '_blank')
        }
      })
    },

    /** Regenerate document */
    regenerateProtocol () {
      regenerationConfirmation(this).then(confirmation => {
        if (confirmation) {
          const body = {
            doc_id: this.sailorDocument.id,
            action: 'update'
          }
          this.$api.post(`api/v1/docs/auth_protocol_dkk/`, body).then(response => {
            if (response.status === 'success') {
              const url = this.API + 'api/v1/docs/generate_protocol_with_conclusion/' + response.data.token + '/'
              this.$api.getPhoto(url).then(responseUrl => {
                window.open(responseUrl, '_blank')
              })
            }
          })
        }
      })
    }
  }
}
