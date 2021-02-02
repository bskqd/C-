import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'

export default {
  name: 'SailorRecordBookStatementUploadFiles',
  props: {
    sailorDocument: Object
  },
  components: {
    FileDropZone
  },
  data () {
    return {
      buttonLoader: false
    }
  },
  methods: {
    /** Upload file to record book statement */
    uploadFile () {
      this.buttonLoader = true
      const files = this.$refs.mediaContent.filesArray
      this.$api.postPhoto(files, 'StatementServiceRecord', this.sailorDocument.id).then(response => {
        this.buttonLoader = false
        if (response.status === 'created') {
          this.$notification.success(this, this.$i18n.t('AddedStatementRB'))
          // this.getDocuments()
          this.$store.dispatch('getRecordBookStatement', this.id)
        }
      })
    }
  }
}
