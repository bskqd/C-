import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { mapState } from 'vuex'

export default {
  name: 'SeafarerGraduationApplicationEdit',
  props: {
    sailorDocument: Object
  },
  components: {
    FileDropZone
  },
  data () {
    return {
      qualification: this.sailorDocument.level_qualification,
      buttonLoader: false
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr'
    }),
    mappingQualification () {
      return this.$store.getters.qualificationById(2)
    }
  },
  methods: {
    /** Edit advance training application */
    editAdvanceTrainingApplication () {
      this.buttonLoader = true
      const body = {
        level_qualification: this.qualification.id
      }
      this.$api.patch(`api/v2/sailor/${this.id}/statement/advanced_training/${this.sailorDocument.id}/`, body)
        .then(response => {
          this.buttonLoader = false
          if (response.status === 'success') {
            const files = this.$refs.mediaContent.filesArray
            if (files.length) {
              this.$api.postPhoto(files, 'StatementAdvancedTraining', this.sailorDocument.id).then((response) => {
                if (response.status === 'success' || response.status === 'created') {
                  this.$notification.error(this, this.$i18n.t('errorAddFile'))
                }
              })
            }
            this.$notification.success(this, this.$i18n.t('advanceTrainingStatementEdited'))
            this.$store.commit('updateDataSailor', { type: 'educationStatement', value: response.data })
          }
        })
    }
  }
}
