import { mapState } from 'vuex'
import { helpers, maxLength, minLength, required } from 'vuelidate/lib/validators'
import PhoneMaskInput from 'vue-phone-mask-input'
import { PlusIcon, Trash2Icon } from 'vue-feather-icons'
import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import SelectSex from '@/components/atoms/FormComponents/SelectSex/SelectSex.vue'
import Rating from '@/components/atoms/Rating.vue'
import SailorsMerging from '@/components/molecules/SailorsMerging/SailorsMerging.vue'
import { getFilesFromData } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'

const alphaEN = helpers.regex('alpha', /^[a-zA-Z'\- ]*$/)
const alphaUA = helpers.regex('alpha', /^[а-щА-ЩЬьЮюЯяЇїІіЄєҐґ'\- ]*$/)
const emailValid = helpers.regex('email', /(^$|^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z; ]{2,}))$)/)

export default {
  name: 'SeafarerMainInfo',
  components: {
    Rating,
    PhoneMaskInput,
    PlusIcon,
    Trash2Icon,
    ValidationAlert,
    SelectSex,
    SailorsMerging
  },
  data () {
    return {
      checkPhoneNumber: true,
      edit: false,
      readOnlyContact: true,
      mini: true,
      account: false,
      accountNumber: null,
      sailorPhoto: null,
      getFilesFromData,
      checkAccess
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      sailorInfo: state => state.sailor.sailorInfo,
      token: state => state.main.token,
      lang: state => state.main.lang,
      code: state => state.main.sendCode,
      rating: state => state.main.rating,
      labelValue: state => (state.main.lang === 'en') ? 'value_eng' : 'value_ukr',
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      langCountry: state => (state.main.lang === 'en') ? 'value_eng' : 'value',
      // mapping documents
      mappingSex: state => state.directory.sex
    })
  },
  watch: {
    sailorInfo: function (val) {
      if (val) this.sailorPhoto = getFilesFromData(this.sailorInfo.photo)
    }
  },
  validations () {
    return {
      sailorInfo: {
        last_name_ukr: { required, maxLength: maxLength(200), alphaUA },
        first_name_ukr: { required, maxLength: maxLength(200), alphaUA },
        middle_name_ukr: { maxLength: maxLength(200), alphaUA },
        last_name_eng: { required, alphaEN, maxLength: maxLength(200) },
        first_name_eng: { required, maxLength: maxLength(200), alphaEN },
        date_birth: { required },
        passport: {
          serial: { required, maxLength: maxLength(30) },
          inn: { required }
        },
        sex: { required },
        email: { emailValid },
        phoneNumber: { maxLength: maxLength(13), minLength: minLength(13) }
      }
    }
    // if (this.checkPhoneNumber) {
    //   return {
    //     sailorInfo: {
    //       last_name_ukr: { required, maxLength: maxLength(200), alphaUA },
    //       first_name_ukr: { required, maxLength: maxLength(200), alphaUA },
    //       middle_name_ukr: { maxLength: maxLength(200), alphaUA },
    //       last_name_eng: { required, alphaEN, maxLength: maxLength(200) },
    //       first_name_eng: { required, maxLength: maxLength(200), alphaEN },
    //       date_birth: { required },
    //       passport: {
    //         serial: { required, maxLength: maxLength(30) },
    //         inn: { numeric, minLength: minLength(10), maxLength: maxLength(10) }
    //       },
    //       sex: { required },
    //       email: { emailValid },
    //       phoneNumber: { required, maxLength: maxLength(13), minLength: minLength(13) }
    //     }
    //   }
    // } else {
    //   return {
    //     sailorInfo: {
    //       last_name_ukr: { required, maxLength: maxLength(200), alphaUA },
    //       first_name_ukr: { required, maxLength: maxLength(200), alphaUA },
    //       middle_name_ukr: { maxLength: maxLength(200), alphaUA },
    //       last_name_eng: { required, alphaEN, maxLength: maxLength(200) },
    //       first_name_eng: { required, maxLength: maxLength(200), alphaEN },
    //       date_birth: { required },
    //       passport: {
    //         serial: { required, maxLength: maxLength(30) },
    //         inn: { numeric, minLength: minLength(10), maxLength: maxLength(10) }
    //       },
    //       sex: { required },
    //       email: { emailValid }
    //     }
    //   }
    // }
  },
  mounted () {
    this.$store.dispatch('getRating', this.id)
  },
  methods: {
    showAllInfo () {
      this.mini = false
    },

    closeAllInfo () {
      this.mini = true
      this.readonly = true
    },

    startEdit () {
      this.readOnlyContact = false
      this.edit = true
    },

    cancelEdit () {
      this.readOnlyContact = true
      this.edit = false
      this.$store.dispatch('getSailorInformation', this.id)
    },

    updatePhoneList (value, phone) {
      switch (value) {
        case 'add':
          this.checkPhoneNumber = true
          if (!this.$v.sailorInfo.phoneNumber.$invalid && !this.sailorInfo.phoneList.includes(phone)) {
            this.sailorInfo.phoneList.push(phone)
          } else {
            this.$v.sailorInfo.phoneNumber.$touch()
          }
          break
        case 'delete':
          this.sailorInfo.phoneList = this.sailorInfo.phoneList.filter(val => val !== phone)
          break
      }
    },

    /** Check field validation */
    validateForm () {
      // this.updatePhoneList('add', this.phoneNumber)
      // this.checkPhoneNumber = false
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.saveInfo()
    },

    saveInfo () {
      const contactInfo = []
      this.sailorInfo.phoneList.forEach(phoneNumber => {
        contactInfo.push({
          type_contact: 'phone_number',
          value: phoneNumber
        })
      })

      const email = this.sailorInfo.email.split(';')
      email.forEach(email => {
        if (email) {
          contactInfo.push({
            type_contact: 'email',
            value: email
          })
        }
      })

      // let positions = this.position.map(val => val.id)

      const body = {
        first_name_ukr: this.sailorInfo.first_name_ukr,
        first_name_eng: this.sailorInfo.first_name_eng,
        last_name_ukr: this.sailorInfo.last_name_ukr,
        last_name_eng: this.sailorInfo.last_name_eng,
        middle_name_ukr: this.sailorInfo.middle_name_ukr,
        sex: this.sailorInfo.sex.id,
        passport: {
          serial: this.sailorInfo.passport.serial.replace(/\s/g, ''),
          user_id: this.id, // this.sailorInfo.passport.id,
          inn: this.sailorInfo.passport.inn
        },
        contact_info: contactInfo,
        // position: positions,
        date_birth: this.sailorInfo.date_birth
      }

      this.$api.patch(`api/v2/sailor/${this.id}/`, body).then(response => {
        if (response.code === 200) {
          this.$notification.success(this, this.$i18n.t('changedInfo'))
          this.readOnlyContact = true
          this.edit = false
          this.$store.dispatch('getSailorInformation', this.id)
        } else {
          if (response.data[0] === 'The sailor with such passport data is exist') {
            this.$notification.error(this, this.$i18n.t('sailorExist'))
          }
        }
      })
    },

    /** Account number registration */
    registerSailorAccount (phone) {
      const body = {
        sailor_id: this.id,
        phone: phone
      }

      this.$api.post('api/v1/sms_auth/registration/', body).then(response => {
        if (response.code === 200) {
          this.accountNumber = phone
          this.$notification.success(this, this.$i18n.t('codeSent'))
          this.$store.commit('setViewRegisterCode', { status: true, code: null })
        } else {
          if (response.data[0] === 'Sailor is registered') {
            this.$notification.error(this, this.$i18n.t('registeredSailor'))
          }
        }
      })
    },

    registerCode () {
      const body = {
        sailor_id: this.id,
        phone: this.accountNumber,
        security_code: this.code.code
      }
      this.$api.post('api/v1/sms_auth/registration/', body).then(response => {
        if (response.code === 200) {
          this.$notification.success(this, this.$i18n.t('doneRegistered'))
          this.$store.commit('setViewRegisterCode', { status: false, code: null })
        }
      })
    }
  }
}
