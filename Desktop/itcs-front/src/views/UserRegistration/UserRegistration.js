import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import AddUbikeyToLogin from '@/views/UserRegistration/AddUbikeyToLogin/AddUbikeyToLogin.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import PhoneMaskInput from 'vue-phone-mask-input'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'
import { required, helpers, maxLength, requiredIf, email } from 'vuelidate/lib/validators'

const alphaLang = helpers.regex('alpha', /^[a-zA-Zа-щА-ЩЬьЮюЯяЇїІіЄєҐґ'\-\s]*$/)
const validLogin = helpers.regex('alpha', /^[a-zA-Z0-9._-]*$/)

function formFieldsInitialState () {
  return {
    firstName: null,
    lastName: null,
    middleName: null,
    login: null,
    pass: null,
    repass: null,
    permission: null,
    city: null,
    region: null,
    country: null,
    affiliate: null,
    phoneNumber: null,
    telegramNumber: null,
    viberNumber: null,
    agentGroup: null,
    document: null,
    medical: null,
    doctor: null,
    institution: null,
    email: null,
    telegramFlag: false,
    viberFlag: false,
    addFingetTitle: false
  }
}

export default {
  name: 'UserRegistration',
  components: {
    ValidationAlert,
    AddUbikeyToLogin,
    PhoneMaskInput,
    FileDropZone
  },
  data () {
    return {
      u2f: window.u2f,
      dataForm: formFieldsInitialState(),
      buttonLoader: false,
      registrationVariant: false,
      withoutDoctor: false,
      checkAccess
    }
  },
  beforeCreate () {
    this.$store.commit('setActivePage', { name: 'userRegistration', access: checkAccess('menuItem-newUser') })
  },
  computed: {
    ...mapState({
      labelValue: state => (state.main.lang === 'en') ? 'value_eng' : 'value',
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      // mapping documents
      permissionsList: state => state.directory.registrationPermissionsList,
      mappingCountry: state => state.directory.country,
      mappingAffiliate: state => state.directory.affiliate,
      mappingAgentGroups: state => state.directory.agentGroups,
      mappingMedicalInstitutions: state => state.directory.medInstitution,
      mappingTrainingPlace: state => state.directory.educationTraining,
      cityList: state => state.directory.city
    }),
    mappingInstitutionList () {
      let institutions = this.$store.getters.institutionByType(2)
      institutions = institutions.sort((a, b) => (a.is_red < b.is_red) ? 1 : -1)
      return institutions
    },
    mediaFilesArray () {
      if (this.dataForm.permission === 'Довірена особа' || this.dataForm.permission === 'Керівник групи') {
        return this.$refs.mediaContent.filesArray
      } else return []
    }
  },
  validations: {
    dataForm: {
      lastName: {
        required: requiredIf(function () {
          return this.dataForm.permission !== 'Мед. працівник'
        }),
        alphaLang,
        maxLength: maxLength(200)
      },
      firstName: {
        required: requiredIf(function () {
          return this.dataForm.permission !== 'Мед. працівник'
        }),
        alphaLang,
        maxLength: maxLength(200)
      },
      middleName: {
        required: requiredIf(function () {
          return this.dataForm.permission !== 'Мед. працівник'
        }),
        alphaLang,
        maxLength: maxLength(200)
      },
      login: { required, validLogin },
      pass: { required },
      country: { required },
      region: { required },
      city: { required },
      affiliate: {
        required: requiredIf(function () {
          return this.dataForm.permission !== 'Мед. працівник'
        })
      },
      institution: {
        required: requiredIf(function () {
          return this.dataForm.permission === 'Представник НТЗ' || this.dataForm.permission === 'Секретар КПК'
        })
      },
      email: {
        required: requiredIf(function () {
          return this.dataForm.permission === 'Секретар КПК'
        }),
        email
      },
      permission: { required },
      agentGroup: {
        required: requiredIf(function () {
          return this.dataForm.permission === 'Довірена особа' ||
            this.dataForm.permission === 'Керівник групи' ||
            this.dataForm.permission === 'Секретар СЦ'
        })
      },
      phoneNumber: {
        required: requiredIf(function () {
          return this.dataForm.permission === 'Довірена особа' ||
            this.dataForm.permission === 'Керівник групи' ||
            this.dataForm.permission === 'Секретар КПК'
        })
      },
      telegramNumber: {
        required: requiredIf(function () {
          return (this.dataForm.permission === 'Довірена особа' || this.dataForm.permission === 'Керівник групи') &&
            this.dataForm.telegramFlag
        })
      },
      viberNumber: {
        required: requiredIf(function () {
          return (this.dataForm.permission === 'Довірена особа' || this.dataForm.permission === 'Керівник групи') &&
            this.dataForm.viberFlag
        })
      },
      medical: {
        required: requiredIf(function () {
          return this.dataForm.permission === 'Мед. працівник'
        })
      },
      doctor: {
        required: requiredIf(function () {
          return this.dataForm.permission === 'Мед. працівник'
        })
      }
    },
    mediaFilesArray: {
      required: requiredIf(function () {
        return this.dataForm.permission === 'Довірена особа' || this.dataForm.permission === 'Керівник групи'
      })
    }
  },
  methods: {
    /**
     * Mapping region by country
     * @param country
     * @returns {*|(function(*): *)|Function}
     */
    mappingRegion (country) {
      if (country !== null) {
        return this.$store.getters.regionById(country.id)
      } else {
        this.dataForm.region = null
        return []
      }
    },

    /**
     * Get cities list by region id
     * @param region
     */
    mappingCities (region) {
      this.dataForm.city = null
      if (region) this.$store.dispatch('getCity', region.id)
    },

    /**
     * Mapping doctors for medical worker
     * @param medInst
     * @returns {(function(*): T[])|*[]}
     */
    mappingDoctors (medInst) {
      if (medInst !== null) {
        if (this.dataForm.doctor !== null) {
          if (this.dataForm.doctor.medical_institution !== medInst.id) {
            this.dataForm.doctor = null
          }
        }
        return this.$store.getters.doctorsById(medInst.id)
      } else {
        this.dataForm.doctor = null
        return []
      }
    },

    /** Check user info validation before registration */
    checkUserInfo () {
      if (this.$v.$invalid) {
        return this.$v.$touch()
      } else this.registerUser()
    },

    registerUser () {
      this.buttonLoader = true

      const permission = []
      permission.push(this.dataForm.permission)

      let agentGroupsArr = []
      if (this.dataForm.agentGroup && this.dataForm.agentGroup[0]) {
        agentGroupsArr = this.dataForm.agentGroup.map(group => { return group.id })
      } else if (this.dataForm.agentGroup && !this.dataForm.agentGroup[0]) {
        agentGroupsArr.push(this.dataForm.agentGroup.id)
      }
      let body = {
        username: this.dataForm.login,
        password: this.dataForm.pass,
        is_active: true,
        userprofile: {
          middle_name: this.dataForm.middleName,
          city: this.dataForm.city.value,
          additional_data: '',
          language: 'UA',
          main_group: permission
        }
      }

      if (this.dataForm.permission === 'Мед. працівник') {
        body.userprofile.doctor_info = this.dataForm.doctor.id
        body.first_name = this.dataForm.doctor.FIO.split(' ')[0]
        body.last_name = this.dataForm.doctor.FIO.split(' ')[1]
        body.userprofile.middle_name = this.dataForm.doctor.FIO.split(' ')[2]
      } else {
        body.first_name = this.dataForm.firstName
        body.last_name = this.dataForm.lastName
        body.userprofile.middle_name = this.dataForm.middleName
        body.userprofile.branch_office = this.dataForm.affiliate.name_ukr
      }
      if (this.dataForm.permission === 'Довірена особа' || this.dataForm.permission === 'Керівник групи' || this.dataForm.permission === 'Секретар КПК') {
        body.userprofile.contact_info = []
        body.userprofile.agent_group = agentGroupsArr
        body.userprofile.contact_info.push({ type_contact: 'phone_number', value: this.dataForm.phoneNumber })
        if (this.dataForm.telegramFlag && this.dataForm.permission !== 'Секретар КПК') {
          body.userprofile.contact_info.push({ type_contact: 'telegram', value: this.dataForm.telegramNumber })
        }
        if (this.dataForm.viberFlag && this.dataForm.permission !== 'Секретар КПК') {
          body.userprofile.contact_info.push({ type_contact: 'viber', value: this.dataForm.viberNumber })
        }
        if (this.dataForm.permission === 'Секретар КПК') {
          body.userprofile.contact_info.push({ type_contact: 'email', value: this.dataForm.email })
        }
      }
      if (this.dataForm.permission === 'Секретар СЦ') {
        body.userprofile.agent_group = agentGroupsArr
      }
      if (this.dataForm.permission === 'Представник НТЗ') {
        body.userprofile.eti_institution = this.dataForm.institution.id
      }
      if (this.dataForm.permission === 'Секретар КПК') {
        body.userprofile.education_institution = this.dataForm.institution.id
      }
      this.$api.post('api/v1/auth/users/', body).then(response => {
        this.buttonLoader = false
        switch (response.status) {
          case 'created':
            if (this.dataForm.permission === 'Довірена особа' || this.dataForm.permission === 'Керівник групи') {
              let agentFormData = new FormData()
              for (const file of this.$refs.mediaContent.filesArray) {
                agentFormData.append('photo', file)
                agentFormData.append('user', response.data.id)
              }
              this.$api.fetchPhoto('api/v1/auth/users/upload_seaman_photo/', { method: 'POST' }, agentFormData)
            }
            if (this.registrationVariant) {
              this.registerFingerFirst(response.data.id)
            } else {
              this.$swal(this.$i18n.t('userWasCreated'))
              this.dataForm = formFieldsInitialState()
              this.$v.$reset()
            }
            break
          case 'error':
            if (response.data.username[0] === 'A user with that username already exists.') {
              this.dataForm.login = null
              this.$notification.error(this, this.$i18n.t('userExist'))
            }
        }
      })
    },

    registerFingerFirst (id = null) {
      this.$api.get('accounts/add_key/').then(response => {
        switch (response.status) {
          case 'success':
            this.$swal(this.$i18n.t('putFingerOnKey'))
            this.registerFingerSec(response.data.register_request, id)
            break
          case 'server error':
            this.$notification.error(this, this.$i18n.t('error'))
            break
        }
      })
    },
    registerFingerSec (reg, id) {
      const regReq = {
        challenge: reg.registerRequests[0].challenge,
        version: reg.registerRequests[0].version
      }
      this.u2f.register(reg.appId, [regReq], [], (keyAuthResponse) => {
        if (!keyAuthResponse.errorCode) {
          keyAuthResponse.user_id = id
          this.$api.post('accounts/add_key/', keyAuthResponse).then(response => {
            switch (response.data.status) {
              case 'created':
                this.$swal(this.$i18n.t('userWasCreated'))
                this.dataForm = formFieldsInitialState()
                this.$v.$reset()
                break
              case 'device exist':
                this.$notification.error(this, this.$i18n.t('userExist'))
                break
            }
          })
        } else {
          this.$notification.error(this, this.$i18n.t('errorRegKey'))
        }
      })
    }
  }
}
