import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { hideDetailed } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorQualificationStatementEditStatus',
  props: {
    sailorDocument: Object
  },
  components: {
    FileDropZone
  },
  data () {
    return {
      buttonLoader: false,
      payment: this.$store.getters.paymentStatusByStatus(this.sailorDocument.is_payed)[0],
      status: this.sailorDocument.status_document,
      hideDetailed,
      checkAccess
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      // mapping documents
      paymentStatus: state => state.directory.paymentStatus
    }),
    mappingStatuses () {
      return this.$store.getters.statusChoose('StatementDKK&Qual')
    }
  },
  methods: {
    /** Change solution status */
    saveSolution () {
      this.buttonLoader = true
      const body = {
        status_document: checkAccess('qualificationStatement', 'maradVerification', this.sailorDocument) ? 34 : this.status.id,
        is_payed: this.payment.status
      }
      if (checkAccess('admin')) {
        body.status_document = this.status.id
      }
      this.$api.patch(`api/v2/sailor/${this.id}/statement/qualification/${this.sailorDocument.id}/`, body).then(response => {
        this.buttonLoader = false
        if (response.status === 'success') {
          const files = this.$refs.mediaContent ? this.$refs.mediaContent.filesArray : []
          if (checkAccess('qualificationStatement', 'maradVerification', this.sailorDocument) && files.length) {
            this.$api.postPhoto(files, 'StatementQualificationDoc', this.sailorDocument.id).then((response) => {
              if (response.status === 'success' || response.status === 'created') {
                this.$notification.error(this, this.$i18n.t('errorAddFile'))
              }
            })
          }

          this.$notification.success(this, this.$i18n.t('editedQualificationStatement'))
          if (response.data.status_document.id === 24) {
            this.$store.commit('addSuccessQualificationStatement', response.data)
          } else {
            this.$store.commit('deleteDataSailor', { type: 'successQualificationStatement', value: this.sailorDocument })
          }
          this.$store.commit('updateDataSailor', { type: 'qualificationStatement', value: response.data })
          this.$store.dispatch('getSQCStatements', this.id)
        }
      })
    }
  }
}
