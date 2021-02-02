import { getDateFormat, getStatus } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorQualificationInfo',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      MAIN: process.env.VUE_APP_MAIN,
      checkAccess,
      getDateFormat,
      getStatus
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      token: state => state.main.token,
      lang: state => state.main.lang,
      labelName: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr',
      // permissions
      permissionWriteCheckDocuments: state => state.main.permissions.writeCheckDocuments,
      permissionReadAuthorApprov: state => state.main.permissions.readAuthorApprov
    }),
    basedQualificationStatement () {
      return this.$store.getters.sailorDocumentByID({ type: 'qualificationStatement', id: this.sailorDocument.statement })
    }
  },
  methods: {
    saveDocument () {
      let url, link
      switch (this.sailorDocument.type_document.id) {
        case 16:
          url = 'api/v1/docs/auth_qualification_proof_of_diplima/'
          link = 'api/v1/docs/generate_qualification_proof_of_diplima/'
          break
        case 1:
        case 49:
          url = 'api/v1/docs/auth_qualification_diplima/'
          link = 'api/v1/docs/generate_qualification_diplima/'
          break
        default:
          url = 'api/v1/docs/auth_qualification_specialist_certificate/'
          link = 'api/v1/docs/generate_qualification_specialist_certificate/'
          break
      }
      let body = {
        doc_id: this.sailorDocument.id,
        num_blank: this.sailorDocument.strict_blank
      }

      this.$api.post(url, body).then(response => {
        if (response.status === 'success') {
          window.open(this.MAIN + link + response.data.token, '_blank')
        }
      })
    }
  }
}
