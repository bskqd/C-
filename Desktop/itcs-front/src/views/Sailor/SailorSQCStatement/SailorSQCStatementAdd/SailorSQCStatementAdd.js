import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { hideDetailed, enterDoublePosition, mappingSQCPositions } from '@/mixins/main'
import { required } from 'vuelidate/lib/validators'
import { mapGetters, mapState } from 'vuex'

function formFieldsInitialState () {
  return {
    newRank: null,
    newPosition: []
  }
}

export default {
  name: 'SailorSQCStatementAdd',
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      dataForm: formFieldsInitialState(),
      buttonLoader: false,
      enterDoublePosition,
      mappingSQCPositions,
      hideDetailed
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    }),
    ...mapGetters({
      ranks: 'ranksSQC'
    })
  },
  validations: {
    dataForm: {
      newRank: { required },
      newPosition: { required }
    }
  },
  methods: {
    /** Check validation field */
    checkInfo () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.saveNewApplicationSQC()
    },

    /**
     * Save new Application SQC by Seafarer
     * @function checkInfo - validation fields
     * @function saveNewApplicationSQC - save application SQC
     **/
    saveNewApplicationSQC () {
      this.buttonLoader = true
      const positionsList = this.dataForm.newPosition.map(value => value.id)
      const body = {
        sailor: parseInt(this.id),
        is_payed: false,
        rank: this.dataForm.newRank.id,
        list_positions: positionsList
      }
      this.$api.post(`api/v2/sailor/${this.id}/statement/protocol_sqc/`, body).then(response => {
        this.buttonLoader = false
        if (response.status === 'created') {
          const files = this.$refs.mediaContent.filesArray
          if (files.length) {
            this.$api.postPhoto(files, 'StatementSqp', response.data.id).then((response) => {
              if (response.status !== 'created' && response.status !== 'success') {
                this.$notification.error(this, this.$i18n.t('errorAddFile'))
              }
            })
          }

          this.$notification.success(this, this.$i18n.t('addedStatementSQC'))
          this.$store.commit('addDataSailor', { type: 'sailorSQCStatement', value: response.data })
          if (response.data.status_document.id === 25) {
            this.$store.commit('incrementUserNotification', 'processStatementsSQC')
          }
          this.$store.commit('incrementBadgeCount', {
            child: 'sqcStatement',
            parent: 'sqcAll'
          })
          this.$parent.viewAdd = false
          this.$data.dataForm = formFieldsInitialState()
          this.$v.$reset()
        }
      })
    },

    /** Remove second double-position if first was removed */
    removePosition (removedPosition) {
      const doublePositions = [106, 121, 122, 123]
      if (doublePositions.includes(removedPosition.rank)) {
        this.dataForm.newPosition.length = 0
      }
    }
  }
}
