import { api } from '@/mixins/api'
import { mapState } from 'vuex'

export default {
  name: 'Signature',
  props: {
    protocolData: Object,
    signAccess: Boolean
  },
  inject: ['getUpdatedProtocols'],
  data () {
    return {
      API: process.env.VUE_APP_API,
      eu: null,
      file: '',
      loadKey: false,
      loadStamp: false,
      signatureButtonLoader: null,
      signatureDataSign: null,
      signatureDataStamp: null,
      typeSignatureSign: false,
      typeSignatureStamp: false
    }
  },
  computed: {
    ...mapState({
      token: state => state.main.token,
      userId: state => state.main.user.id,
      id: state => state.sailor.sailorId
    })
  },
  mounted () {
    // eslint-disable-next-line no-undef
    this.eu = new DigitalSign()
    setTimeout(this.eu.init.bind(this.eu), 100)

    this.getFile()
  },
  methods: {
    setSignature () {
      this.$store.commit('setViewSignatureKey', { status: true, key: null, signAccess: this.signAccess })
    },

    getFile () {
      const body = {
        doc_id: this.protocolData.id
      }
      api.post('api/v1/docs/auth_protocol_dkk/', body)
        .then(resp => {
          console.log(resp)
          switch (resp.status) {
            case 'success':
              api.getFiles('api/v1/docs/generate_protocol_with_conclusion/' + resp.data.token)
                .then(resp => {
                  this.file = resp
                })
              break
          }
        })
    },

    readKey (files, password, server, typeSignatureBySign) {
      let _onError = (e) => {
        this.$notification.error(this, this.$i18n.t('errorReadKey'))
      }

      try {
        let _onSuccess = (keyName, key) => {
          this.eu.loadAndApprovePrivateKey(key, password, server.address, (data) => {
            if (typeSignatureBySign) {
              this.signatureDataSign = data
              this.loadKey = true
            } else {
              this.signatureDataStamp = data
              this.loadStamp = true
            }
          })
        }

        let _onFileRead = (readedFile) => {
          _onSuccess(readedFile.file.name, readedFile.data)
        }

        // eslint-disable-next-line no-undef
        this.eu.signLib.ReadFile(files, _onFileRead.bind(this), _onError.bind(this))
      } catch (e) {
        this.$notification.error(this, this.$i18n.t('errorReadKey'))
      }
    },

    signFile (typeSignatureBySign) {
      if (typeSignatureBySign) {
        this.signFileByKey()
      }
      if (!typeSignatureBySign) {
        this.signFileByStamp()
      }
    },

    signFileByKey () {
      this.eu.signFile(this, this.token, this.API, this.file, this.protocolData.number, this.protocolData.id,
        true, false)
    },

    signFileByStamp () {
      this.eu.signFile(this, this.token, this.API, this.file, this.protocolData.number, this.protocolData.id,
        false, true)
    },

    respStatus (data) {
      switch (data.status) {
        case 'success':
        case 'created':
          if (this.loadKey && this.loadStamp) {
            break
          } else {
            this.$notification.success(this, this.$i18n.t('successSignDoc'))
            // this.getUpdatedProtocols()
            this.$store.dispatch('getProtocolsSQC', this.id)
            this.$store.commit('setViewSignatureKey', { status: false, key: null, signAccess: null })
            this.file = ''
            this.loadKey = null
            this.signatureData = null
            break
          }
        case 'error':
          if (data && data.data[0] === 'Protocol was signed') {
            this.$notification.error(this, this.$i18n.t('warningSignExist'))
          } else {
            this.$notification.error(this, this.$i18n.t('errorSignDoc'))
          }
      }
    }
  }
}
