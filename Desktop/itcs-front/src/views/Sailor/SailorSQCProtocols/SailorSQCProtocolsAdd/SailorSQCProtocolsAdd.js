import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { hideDetailed } from '@/mixins/main'
import { required, maxValue, minValue } from 'vuelidate/lib/validators'
import { mapState } from 'vuex'

function formFieldsInitialState () {
  return {
    approvedApplications: null,
    dateMeeting: null,
    headCommission: null,
    membersCommission: null,
    decision: null
  }
}

export default {
  name: 'SailorSQCProtocolsAdd',
  props: {
    getDocuments: Function
  },
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      dataForm: formFieldsInitialState(),
      buttonLoader: false,
      hideDetailed
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      lang: state => state.main.lang,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      // mapping documents
      approvedApplications: state => state.sailor.successStatement,
      commission: state => state.directory.commission,
      commissionMembers: state => state.directory.allCommissioners,
      solutions: state => state.directory.solutions
    }),
    dateMeetingObject () {
      return this.dataForm.dateMeeting ? new Date(this.dataForm.dateMeeting) : null
    }
  },
  validations () {
    return {
      dataForm: {
        approvedApplications: { required },
        headCommission: { required },
        decision: { required },
        membersCommission: {
          required,
          length: {
            maxValue: maxValue(4),
            minValue: minValue(2)
          }
        }
      },
      dateMeetingObject: {
        required,
        minValue: minValue(new Date('1900-01-01')),
        maxValue: maxValue(new Date())
      }
    }
  },
  methods: {
    /** Check field validation */
    checkInfo () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else {
        this.saveNewProtocolSQC()
      }
    },

    /** Save new protocol SQC by Seafarer */
    saveNewProtocolSQC () {
      this.buttonLoader = true
      let membersCommission = this.dataForm.membersCommission.map(value => {
        return { signer: value.id, commissioner_type: 'CH' }
      })
      membersCommission.push({ signer: this.dataForm.headCommission.id, commissioner_type: 'HD' })

      const body = {
        sailor: parseInt(this.id),
        statement_dkk: this.dataForm.approvedApplications.id,
        date_meeting: this.dataForm.dateMeeting,
        branch_create: this.dataForm.headCommission.branch_office,
        decision: this.dataForm.decision.id,
        commissioner_sign: membersCommission
      }
      this.$api.post(`api/v2/sailor/${this.id}/protocol_sqc/`, body).then(response => {
        this.buttonLoader = false
        switch (response.status) {
          case 'created':
            const files = this.$refs.mediaContent.filesArray
            if (files.length) {
              this.$api.postPhoto(files, 'ProtoclsSQCDoc', response.data.id).then((response) => {
                if (response.status !== 'created' && response.status !== 'success') {
                  this.$notification.error(this, this.$i18n.t('errorAddFile'))
                }
              })
            }

            this.$notification.success(this, this.$i18n.t('addedProtocolSQC'))
            this.$store.commit('addDataSailor', { type: 'sailorSQCProtocols', value: response.data })
            this.$parent.viewAdd = false
            this.$store.commit('incrementBadgeCount', {
              child: 'sqcDocument',
              parent: 'sqcAll'
            })
            this.$store.commit('incrementUserNotification', 'documentsToSign')
            this.$data.dataForm = formFieldsInitialState()
            this.$v.$reset()
            break
          case 'error':
            if (response.data.statement_dkk[0] === 'This field must be unique.') {
              this.$notification.error(this, this.$i18n.t('existProtocolSQC'))
            }
            break
        }
      })
    }
  }
}
