import { required, requiredIf } from 'vuelidate/lib/validators'
import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { hideDetailed, mappingPositions, enterDoublePosition } from '@/mixins/main'
import { mapState } from 'vuex'

function formFieldsInitialState () {
  return {
    rank: null,
    position: [],
    ports: '',
    protocol: null,
    // protocolAuto: null,
    protocolsList: [],
    type: null,
    typeList: [],
    buttonLoader: false
  }
}

export default {
  name: 'SailorQualificationStatementAdd',
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      hideDetailed,
      mappingPositions,
      enterDoublePosition,
      dataForm: formFieldsInitialState(),
      existProtocol: false,
      protocolView: false,
      typeView: false,
      singlePosition: true
    }
  },
  validations: {
    dataForm: {
      rank: { required },
      position: { required },
      ports: { required },
      // protocol: {
      //   required: requiredIf(function () {
      //     return ((this.dataForm.rank !== null) && (this.dataForm.position !== null) &&
      //       (this.dataForm.rank.type_document === 87) && (this.protocolView)) ||
      //       ((this.dataForm.rank !== null) && (this.dataForm.position !== null) &&
      //         (this.dataForm.rank.type_document === 49) && (this.protocolView)) ||
      //       (((this.dataForm.type !== null)) && (this.dataForm.type.for_service === 'other_proficiency') &&
      //         (this.dataForm.type.id !== 21))
      //   })
      // },
      protocol: {
        required: requiredIf(function () {
          // return (this.dataForm.rank && this.dataForm.position &&
          //   this.dataForm.type && this.dataForm.type.for_service === 'other_proficiency' &&
          //   this.dataForm.type.id !== 21)
          return this.dataForm.rank && this.dataForm.rank.is_dkk
        })
      },
      type: {
        required: requiredIf(function () {
          // return (((this.dataForm.type === null) || (this.dataForm.type.for_service !== 'other_proficiency')) &&
          //   ((this.dataForm.rank === null) || (this.dataForm.rank.type_document !== 87)))
          return this.dataForm.protocol && this.dataForm.protocol.is_continue
        })
      }
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      token: state => state.main.token,
      lang: state => state.main.lang,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      protocolsSQCList: state => state.directory.protocols,
      // mapping documents
      ranksList: state => state.directory.ranks
    }),
    mappingPorts () {
      return this.$store.getters.portsActual(false)
    }
  },
  mounted () {
    this.mappingTypeQualification('diploma')
  },
  methods: {
    mappingProtocols (rank) {
      if (rank !== null) {
        return this.$store.getters.protocolsByRank(rank.id)
      } else {
        return this.protocolsSQCList
      }
    },

    mappingTypeQualification (service) {
      this.dataForm.typeList = this.$store.getters.typeDocQualificationByService(service).map(val => {
        if (val.id === 49) {
          val.name_ukr = 'Диплом та підтвердження'
          val.name_eng = 'Diploma and prof of diploma'
        }
        return val
      })
    },

    checkExistProtocolSQC (rank) {
      this.protocolView = false
      this.typeView = false
      this.dataForm.protocol = null
      this.dataForm.protocolsList = []

      if (rank && rank.is_dkk) {
        this.protocolView = true
        this.dataForm.protocolsList = this.$store.getters.protocolsByRank(rank.id)
        if (this.dataForm.protocolsList.length) {
          this.$notification.success(this, this.$i18n.t('FoundSQC'))
          if (this.dataForm.protocolsList.length === 1) this.dataForm.protocol = this.dataForm.protocolsList[0]
        } else {
          this.$notification.warning(this, this.$i18n.t('NotFoundSQC'))
        }
      }

      const diplomasTypesId = [1, 49]
      this.typeView = diplomasTypesId.includes(this.dataForm.rank.type_document) && this.dataForm.protocol &&
        this.dataForm.protocol.is_continue
    },

    validateForm () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.saveQualificationStatement()
    },

    saveQualificationStatement () {
      this.dataForm.buttonLoader = true

      const body = {
        sailor: this.id,
        port: this.dataForm.ports.id
      }

      let listPositions = this.dataForm.position.map(value => {
        return value.id
      })

      body.rank = this.dataForm.rank.id
      body.list_positions = listPositions
      body.type_document = this.typeView ? this.dataForm.type.id : null
      body.protocol_dkk = this.dataForm.rank && this.dataForm.rank.is_dkk ? this.dataForm.protocol.id : null

      this.$api.post(`api/v2/sailor/${this.id}/statement/qualification/`, body)
        .then(response => {
          this.dataForm.buttonLoader = false
          switch (response.status) {
            case 'created':
              const files = this.$refs.mediaContent.filesArray
              if (files.length) {
                this.$api.postPhoto(files, 'StatementQualificationDoc', response.data.id).then(response => {
                  if (response.status !== 'success' && response.status !== 'created') {
                    this.$notification.error(this, this.$i18n.t('errorAddFile'))
                  }
                })
              }

              this.$notification.success(this, this.$i18n.t('addedQualificationStatement'))
              this.$store.commit('addDataSailor', { type: 'qualificationStatement', value: response.data })
              this.$parent.viewAdd = false
              this.$store.commit('incrementBadgeCount', {
                child: 'qualificationStatement',
                parent: 'qualificationAll'
              })
              this.$data.dataForm = formFieldsInitialState()
              this.$v.$reset()
              break
            case 'error':
              if (response.data[0] === 'Qualification document with this statement exists') {
                this.$notification.error(this, this.$i18n.t('protocolAlreadyUsed'))
              }
              break
          }
        })
    },

    /** Remove second double-position if first was removed */
    removePosition (removedPosition) {
      const doublePositions = [106, 121, 122, 123]
      if (doublePositions.includes(removedPosition.rank)) {
        this.dataForm.position.length = 0
      }
    }
  }
}
