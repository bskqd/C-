import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { required } from 'vuelidate/lib/validators'
import { mapState } from 'vuex'

export default {
  name: 'SeafarerContactUploading',
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      statementAlreadyExist: false,
      buttonLoader: false
    }
  },
  computed: {
    ...mapState({
      userId: state => state.main.user.id,
      sailorId: state => state.sailor.sailorId
    }),
    mediaFilesArray () {
      return this.$refs.mediaContent.filesArray
    }
  },
  validations: {
    mediaFilesArray: { required }
  },
  mounted () {
    this.checkStatementAgent()
  },
  methods: {
    /** Check if statement is already exist */
    checkStatementAgent () {
      this.$api.get(`api/v1/seaman/${this.sailorId}/check_statement_seaman/`).then(response => {
        if (response.status === 'success') {
          this.statementAlreadyExist = response.data.has_statement
        }
      })
    },

    /** Check documents entries before submit */
    validationCheck () {
      if (this.$v.$invalid) {
        return this.$v.$touch()
      } else this.addSailorContract()
    },

    /** Add contact document confirmation between sailor and Morrichservice */
    addSailorContract () {
      this.buttonLoader = true
      const body = {
        agent: this.userId,
        sailor_key: this.sailorId
      }
      this.$api.post(`api/v1/seaman/statement_seaman_sailor/`, body).then(response => {
        this.buttonLoader = false
        if (response.status === 'created') {
          let contractDocs = new FormData()
          for (const photo of this.mediaFilesArray) {
            contractDocs.append('photo', photo)
          }
          this.$api.fetchPhoto(`api/v1/seaman/statement_seaman_sailor/${response.data.id}/upload_file/`, { method: 'POST' }, contractDocs)
            .then(() => {
              this.$notification.success(this, this.$i18n.t('createdStatement'))
              this.statementAlreadyExist = true
            })
        }
      })
    }
  }
}
