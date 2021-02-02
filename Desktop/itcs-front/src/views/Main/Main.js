import MainSailorHistory from './MainSailorHistory/MainSailorHistory.vue'
import MainAgentHistory from './MainForAgent/MainForAgent.vue'
import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { required, maxLength, minLength, requiredIf } from 'vuelidate/lib/validators'
import { myFetch } from '@/functions/main'
import { mapState } from 'vuex'
import { PlusCircleIcon } from 'vue-feather-icons'
import { checkAccess } from '@/mixins/permissions'

export default {
  name: 'Main',
  components: {
    PlusCircleIcon,
    MainSailorHistory,
    MainAgentHistory,
    ValidationAlert
  },
  data () {
    return {
      checkAccess,
      GOOGLE_KEY: process.env.VUE_APP_GOOGLE_MAP_KEY,
      latitude: null,
      longitude: null,
      ipAddress: null,
      locationAddress: null,
      agentQR: null,
      linkForSailor: null,
      timeout: null,
      timeLeft: 60,
      sailorPhone: null,
      code: null,
      codeSent: false,
      phoneNumberRegexp: {
        F: {
          pattern: /[6,5,7,9]/
        },
        T: {
          pattern: /[0-9]/
        }
      }
    }
  },
  computed: {
    ...mapState({
      userInfo: state => state.main.user
    })
  },
  beforeCreate () {
    this.$store.commit('setActivePage', { name: 'home', access: true })
  },
  mounted () {
    this.getLocationInfo()
    if (checkAccess('main-agent')) this.getQrCode()
  },
  validations: {
    sailorPhone: {
      required,
      maxLength: maxLength(9),
      minLength: minLength(9)
    },
    code: {
      required: requiredIf(function () { return this.codeSent }),
      maxLength: maxLength(4),
      minLength: minLength(4)
    }
  },
  methods: {
    /** Get user geolocation */
    async getLocationInfo () {
      if (navigator.geolocation && !sessionStorage.getItem('GEOLOCATION')) {
        await navigator.geolocation.getCurrentPosition((position) => {
          this.latitude = position.coords.latitude
          this.longitude = position.coords.longitude
          this.getAddress()
        })
      }
    },

    /** Get user address by google maps */
    async getAddress () {
      let urlMaps = `https://maps.googleapis.com/maps/api/geocode/json?latlng=
        ${this.latitude},${this.longitude}&language=uk&key=${this.GOOGLE_KEY}`

      await myFetch('', urlMaps).then(response => {
        if (response.data.status === 'OK') {
          this.locationAddress = response.data.results[0].formatted_address
        } else {
          this.locationAddress = null
        }
        this.getIpAddress()
      })
    },

    /** Get user IP address */
    async getIpAddress () {
      await myFetch('', 'https://api.ipify.org/?format=json').then(response => {
        this.ipAddress = response.data.ip
        this.addGeolocation()
      })
    },

    /** Add user location and OS info */
    async addGeolocation () {
      const body = {
        longitude: this.longitude,
        latitude: this.latitude,
        address: this.locationAddress,
        ip_address: this.ipAddress,
        user_agent: navigator.appVersion
      }
      await this.$api.post('accounts/authorization_log/', body).then(response => {
        if (response.code === 201) {
          sessionStorage.setItem('GEOLOCATION', 'RECEIVED')
        }
      })
    },

    async getQrCode () {
      await this.$api.get('api/v1/seaman/qr_code/generate/').then(response => {
        switch (response.status) {
          case 'success':
            this.linkForSailor = response.data.url
            this.agentQR = response.data.qr
            break
          case 'error':
            if (response.data[0] === 'Agent has reached the limit for the current month') {
              this.$notification.info(this, this.$i18n.t('agentUserLimit'))
            }
            break
        }
      })
    },

    clipboardSuccessHandler () {
      this.$notification.success(this, this.$i18n.t('copied'))
    },

    validateForm (status) {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.sendCode(status)
    },

    sendCode (status) {
      setTimeout(() => {
        this.clearTime()
      }, 61000)
      this.timeLeft = 60
      this.setTime()
      const body = {
        phone: this.sailorPhone,
        security_code: this.code
      }
      this.$api.post('api/v1/seaman/phone/statement_seaman_sailor/', body).then(response => {
        if (response.code === 200 && status === 'code') {
          this.codeSent = true
          this.$notification.success(this, this.$i18n.t('codeSent'))
        } else if (response.code === 200 && status === 'confirm') {
          this.codeSent = false
          this.$notification.success(this, this.$i18n.t('codeSent'))
        }
      })
    },

    setTime () {
      this.timeout = setInterval(() => {
        if (this.timeLeft !== 0) {
          this.timeLeft--
        }
      }, 1000)
    },

    clearTime () {
      if (this.timeout) {
        clearInterval(this.timeout)
      }
    }
  }
}
