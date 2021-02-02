import vue2Dropzone from 'vue2-dropzone'
import 'vue2-dropzone/dist/vue2Dropzone.min.css'

export default {
  name: 'DropZone',
  components: {
    vueDropzone: vue2Dropzone
  },
  data () {
    return {
      filesArray: [],
      dropzoneOptions: {
        url: 'https://httpbin.org/post',
        thumbnailWidth: 200,
        thumbnailHeight: 200,
        maxFilesize: 40,
        maxFiles: 10,
        acceptedFiles: 'image/jpeg, image/png, image/jpg, application/pdf',
        addRemoveLinks: true,
        autoProcessQueue: false,
        dictRemoveFile: this.$i18n.t('removeFile'),
        dictFileTooBig: `${this.$i18n.t('tooHeavyFile')}. ${this.$i18n.t('maxFileSize')} - {{maxFilesize}}MB`,
        dictInvalidFileType: this.$i18n.t('invalidDataFormat')
      }
    }
  },
  methods: {
    /** Add new file to array */
    addFile (file) {
      setTimeout(() => {
        if (file.status !== 'error') {
          this.filesArray.push(file)
        }
      }, 1)
    },

    /** Remove file from array */
    removeFile (file) {
      this.filesArray.splice(this.filesArray.indexOf(file), 1)
    }
  }
}
