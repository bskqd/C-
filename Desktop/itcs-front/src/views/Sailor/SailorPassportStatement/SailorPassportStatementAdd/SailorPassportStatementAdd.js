import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { mapGetters, mapState } from 'vuex'
import { required } from 'vuelidate/lib/validators'

function formFieldsInitialState () {
  return {
    port: null,
    processingMethod: null
  }
}

export default {
  name: 'SailorPassportStatementAdd',
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      dataForm: formFieldsInitialState(),
      buttonLoader: false
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    }),
    ...mapGetters({
      ports: 'notDisabledPorts',
      processingOptionsList: 'validSailorPassportProcessing'
    })
  },
  validations: {
    dataForm: {
      port: { required },
      processingMethod: { required }
    }
  },
  methods: {
    /** Check fields entries */
    checkFields () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.addSeafarerPassportApplication()
    },

    /** Add new seafarer passport application */
    addSeafarerPassportApplication () {
      this.buttonLoader = true
      const body = {
        sailor: this.id,
        port: this.dataForm.port.id,
        type_receipt: this.dataForm.processingMethod.id
      }
      this.$api.post(`api/v2/sailor/${this.id}/statement/sailor_passport/`, body).then(response => {
        this.buttonLoader = false
        switch (response.status) {
          case 'created':
            const files = this.$refs.mediaContent.filesArray
            if (files.length) {
              this.$api.postPhoto(files, 'StatementSailorPassport', response.data.id).then((response) => {
                if (response.status !== 'created' && response.status !== 'success') {
                  this.$notification.error(this, this.$i18n.t('errorAddFile'))
                }
              })
            }
            this.$notification.success(this, this.$i18n.t('sailorPassportStatementAdded'))
            this.$store.commit('addDataSailor', { type: 'sailorPassportStatement', value: response.data })
            this.$store.commit('incrementBadgeCount', {
              child: 'passportStatement',
              parent: 'passportAll'
            })
            this.$parent.viewAdd = false
            this.$data.dataForm = formFieldsInitialState()
            this.$v.$reset()
            break
          case 'error':
            if (response.data[0] === 'Statement exists') {
              this.$notification.error(this, this.$i18n.t('courseExist'))
            } else if (response.data[0] === 'No sailor passport to renew') {
              this.$notification.error(this, this.$i18n.t('noPassportsToRenew'))
            }
            break
        }
      })
    }
  }
}
