import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { minLength, required, helpers } from 'vuelidate/lib/validators'
import { mapState } from 'vuex'

const pass = helpers.regex('', /^[\Wa-zA-Z\d_]*$/)

export default {
  name: 'Authorization',
  components: {
    ValidationAlert
  },
  data () {
    return {
      login: '',
      pass: '',
      locale: 'en',
      u2f: window.u2f,
      u2fActive: true,
      noAccount: false,
      firsAuth: false,
      passOld: null,
      passNew: null,
      passNewRepeat: null,
      errorOldPass: false,
      errorNewPass: false
    }
  },
  validations: {
    passNew: {
      required,
      pass,
      minLength: minLength(10)
    },
    passNewRepeat: { required },
    passOld: { required }
  },
  beforeCreate () {
    this.$store.commit('setActivePage', { name: 'authorization', access: false })
  },
  computed: {
    ...mapState({
      token: state => state.main.token,
      selfHost: state => state.main.selfHost
    })
  },
  mounted () {
    this.checkAuth()
  },
  methods: {
    checkAuth () {
      this.$api.post('accounts/check_authozation/')
        .then(resp => {
          switch (resp.data) {
            case true:
              this.$swal(this.$i18n.t('alreadyAuth'))
              window.location = '/'
              // this.$router.push({ name: 'home' })
              break
            case false:
              localStorage.removeItem('Token')
          }
        })
    },

    setLogin () {
      const body = {
        username: this.login,
        password: this.pass
      }
      localStorage.removeItem('Token')
      this.$api.post('accounts/login/', body)
        .then(response => {
          console.log(response)
          this.noAccount = false
          switch (response.status) {
            case 'success' :
              if (response.data.redirect === 'yubikey') {
                localStorage.removeItem('token')
                this.setLoginYubikey(response.data.tmpToken, response.data.sign_request)
              } else {
                localStorage.setItem('Token', response.data.token)
                if (response.data.must_change_password) {
                  this.firsAuth = true
                } else {
                  this.checkExistToken()
                }
              }
              break
            case 'not found':
            case 'error':
              this.noAccount = true
              break
            default:
              localStorage.setItem('Token', response.data.token)
              this.checkExistToken()
          }
        })
        .catch(() => {
          this.noAccount = true
        })
    },

    setLoginYubikey (token, dataSign) {
      if (dataSign) {
        this.$swal('Прикладіть палець до ключа!')
        this.u2f.sign(dataSign.appId, dataSign.challenge, dataSign.registeredKeys, (resp) => {
          const body = {
            tmp_key: token,
            response: JSON.stringify(resp)
          }

          this.$api.post('accounts/yubikeylogin/', body)
            .then(response => {
              switch (response.data.status) {
                case 'redirect_to_login' :
                  localStorage.removeItem('Token')
                  break
                case 'authorizated':
                  localStorage.setItem('Token', response.data.token)
                  if (response.data.err) {
                    this.$swal('Цей ключ не додано до облікового запису!')
                  } else {
                    if (response.data.must_change_password) {
                      this.firsAuth = true
                    } else {
                      this.checkExistToken()
                    }
                  }
              }
            })
        })
      }
    },

    checkExistToken () {
      if (this.$store.state.token !== '') {
        window.location = '/'
      }
    },

    checkNewPass () {
      if (this.$v.$invalid) {
        return this.$v.$touch()
      } else {
        this.errorOldPass = false
        this.errorNewPass = false
        if (this.pass !== this.passOld) {
          this.errorOldPass = true
        }
        if (this.passNew !== this.passNewRepeat) {
          this.errorNewPass = true
        }
        if ((this.pass === this.passOld) && (this.passNew === this.passNewRepeat)) {
          this.saveNewPass()
        }
      }
    },

    saveNewPass () {
      const body = {
        old_password: this.passOld,
        new_password: this.passNew
      }
      this.$api.post('accounts/change_password/', body)
        .then(() => this.checkExistToken())
    }
  }
}
