import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { helpers, maxLength, minLength, required, requiredIf } from 'vuelidate/lib/validators'
import { hideDetailed } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'
const phoneNumber = helpers.regex('numeric', /^[+0-9]*$/)

export default {
  name: 'BackOfficeAgentGroupsInfoEdit',
  components: {
    ValidationAlert
  },
  props: {
    row: Object,
    getDocuments: Function
  },
  data () {
    return {
      firstName: this.row.item.first_name,
      lastName: this.row.item.last_name,
      middleName: this.row.item.userprofile.middle_name,
      agentGroup: this.row.item.agent_group,
      affiliate: this.$store.getters.affiliateByName(this.row.item.userprofile.branch_office)[0],
      phoneNumber: '',
      telegram: '',
      viber: '',
      buttonLoader: false,
      hideDetailed,
      checkAccess
    }
  },
  computed: {
    ...mapState({
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      // mapping documents
      affiliatesList: state => state.directory.affiliate.filter(value => !value.is_disable),
      agentGroupsList: state => state.directory.agentGroups
    })
  },
  validations: {
    lastName: { required },
    firstName: { required },
    middleName: { required },
    agentGroup: {
      required: requiredIf(function () {
        return !checkAccess('headAgent')
      })
    },
    affiliate: { required },
    phoneNumber: {
      required: requiredIf(function () {
        return this.row.item.userprofile.type_user !== 'secretary_service'
      }),
      maxLength: maxLength(13),
      minLength: minLength(13),
      phoneNumber
    },
    telegram: { maxLength: maxLength(13), minLength: minLength(13), phoneNumber },
    viber: { maxLength: maxLength(13), minLength: minLength(13), phoneNumber }
  },
  mounted () {
    this.setContactData()
  },
  methods: {
    /** Set contact models depends on value type */
    setContactData () {
      if (this.row.item.userprofile.contact_info && this.row.item.userprofile.contact_info.length) {
        for (const contact of this.row.item.userprofile.contact_info) {
          switch (contact.type_contact) {
            case 'telegram':
            case '4':
              this.telegram = contact.value.replace(/[()\-\s]/g, '')
              break
            case 'viber':
            case '5':
              this.viber = contact.value.replace(/[()\-\s]/g, '')
              break
            case 'phone_number':
            case '1':
              this.phoneNumber = contact.value.replace(/[()\-\s]/g, '')
              break
          }
        }
      }
    },

    /** Check field entries before submit */
    validationCheck () {
      if (this.$v.$invalid) {
        return this.$v.$touch()
      } else this.editAgentInfo()
    },

    /** Edit agent information */
    editAgentInfo () {
      this.buttonLoader = true
      let agentGroupsArr = []
      if (this.agentGroup[0]) {
        agentGroupsArr = this.agentGroup.map(group => { return group.id })
      } else {
        agentGroupsArr.push(this.agentGroup.id)
      }
      const body = {
        last_name: this.lastName,
        first_name: this.firstName,
        userprofile: {
          agent_group: agentGroupsArr,
          middle_name: this.middleName,
          branch_office: this.affiliate.name_ukr,
          contact_info: [
            { type_contact: 1, value: this.phoneNumber },
            { type_contact: 4, value: this.telegram },
            { type_contact: 5, value: this.viber }
          ]
        }
      }

      this.$api.patch(`api/v1/auth/users/${this.row.item.id}/`, body).then(response => {
        this.buttonLoader = false
        if (response.status === 'success') {
          this.$notification.success(this, this.$i18n.t('editedAgentInfo'))
          this.getDocuments()
        }
      })
    }
  }
}
