import { mapState } from 'vuex'
import { required } from 'vuelidate/lib/validators'
import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'

function formFieldsInitialState () {
  return {
    login: null,
    pass: null
  }
}

export default {
  name: 'AddUbikeyToLogin',
  components: {
    ValidationAlert
  },
  props: {
    fingerRegistration: Function
  },
  data () {
    return {
      dataForm: formFieldsInitialState(),
      buttonLoader: false
    }
  },
  computed: {
    ...mapState({
      mappingLogin: state => state.directory.userList
    })
  },
  validations: {
    dataForm: {
      login: { required },
      pass: { required }
    }
  },
  methods: {
    checkUserInfo () {
      if (this.$v.$invalid) {
        return this.$v.$touch()
      } else this.fingerRegistration(this.dataForm.login.id)
    }
  }
}
