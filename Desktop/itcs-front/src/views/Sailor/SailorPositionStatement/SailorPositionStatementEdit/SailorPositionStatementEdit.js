import Rating from '@/components/atoms/Rating.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SeafarerPositionApplicationEdit',
  props: {
    sailorDocument: Object
  },
  components: {
    Rating,
    FileDropZone
  },
  data () {
    return {
      seafarerPassport: this.sailorDocument.includeSailorPass,
      payment: this.$store.getters.paymentStatusByStatus(this.sailorDocument.is_payed)[0],
      buttonLoader: false,
      showSetRating: false,
      checkAccess
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      rating: state => state.sailor.rating,
      lang: state => state.main.lang,
      labelName: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr',
      // mapping documents
      paymentStatus: state => state.directory.paymentStatus,
      processingOptionsList: state => state.sailor.sailorPassportProcessing
    })
  },
  methods: {
    /** Update position application */
    updatePositionApplication () {
      this.buttonLoader = true
      const body = {
        include_sailor_passport: this.seafarerPassport.id,
        is_payed: this.payment.status
      }
      this.$api.patch(`api/v1/back_off/packet/${this.sailorDocument.id}/`, body).then(response => {
        this.buttonLoader = false
        if (response.status === 'success') {
          const files = this.$refs.mediaContent.filesArray
          if (files.length) {
            this.$api.postPhoto(files, 'PacketItem', this.sailorDocument.id).then((response) => {
              if (response.status !== 'success' && response.status !== 'created') {
                this.$notification.error(this, this.$i18n.t('errorAddFile'))
              }
            })
          }

          this.$notification.success(this, this.$i18n.t('sailorPositionStatementEdited'))
          this.$store.commit('updateDataSailor', { type: 'positionStatement', value: response.data })
          // if (this.payment.status && (this.permissionChangeRating || (this.rating !== 4 && this.permissionWriteRating))) {
          //   this.showSetRating = true
          // } else {
          //   this.getDocuments()
          // }
          if (checkAccess('positionStatement', 'changeRating', response.data)) {
            this.showSetRating = true
          } else {
            this.$store.dispatch('getPositionStatements', this.id)
          }
        }
      })
    }
  }
}
