import { mapState } from 'vuex'

export default {
  name: 'SailorStudentEditStatus',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      buttonLoader: false,
      status: this.sailorDocument.status_document
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    }),
    mappingStatuses () {
      return this.$store.getters.statusChoose('StudentID')
    }
  },
  methods: {
    saveNewStatus () {
      this.buttonLoader = true
      const body = {
        status_document: this.status.id
      }

      this.$api.patch(`api/v1/cadets/student_id/${this.sailorDocument.id}/`, body).then(response => {
        this.buttonLoader = false
        if (response.code === 200) {
          this.$notification.success(this, this.$i18n.t('editedStudentCard'))
          this.$store.commit('updateDataSailor', { type: 'student', value: response.data })
        }
      })
    }
  }
}
