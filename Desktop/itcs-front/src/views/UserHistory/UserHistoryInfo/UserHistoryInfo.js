import ChangedField from '@/components/atoms/ChangedField.vue'
import { hideDetailed, getDateFormat } from '@/mixins/main'
import { mapState } from 'vuex'

export default {
  name: 'UserHistoryInfo',
  props: {
    row: Object
  },
  components: {
    ChangedField
  },
  data () {
    return {
      arrayDifference: [],
      hideDetailed,
      getDateFormat
    }
  },
  computed: {
    ...mapState({
      langFields: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      langCountry: state => (state.main.lang === 'en') ? 'value_eng' : 'value',
      langRegion: state => (state.main.lang === 'en') ? 'value_eng' : 'name',
      langSex: state => (state.main.lang === 'en') ? 'value_eng' : 'value_ukr',
      langETI: state => (state.main.lang === 'en') ? 'name_en' : 'name'
    })
  },
  mounted () {
    console.log(this.row.item)
    this.arrayChanges()
  },
  methods: {
    /** Set short property name (ex. full name/registration place etc.) */
    setPriceForm (objectValue) {
      if (this.row.item[objectValue]) {
        return this.row.item[objectValue].type_of_form === 'First' ? this.$i18n.t('firstForm') : this.$i18n.t('secondForm')
      } else return null
    },
    setUserFullName (objectValue) {
      if (this.row.item[objectValue]) {
        return `${this.row.item[objectValue].last_name} ${this.row.item[objectValue].first_name}
         ${this.row.item[objectValue].userprofile.middle_name}`
      } else return null
    },
    setPassportPlace (objectValue, type) {
      if (this.row.item[objectValue] && this.row.item[objectValue][type]) {
        return `${this.row.item[objectValue][type].index}, ${this.row.item[objectValue][type].city.country[this.langCountry]},
        ${this.row.item[objectValue][type].city.region[this.langCountry]}, ${this.row.item[objectValue][type].city.city[this.langCountry]},
        ${this.row.item[objectValue][type].street}, ${this.row.item[objectValue][type].house}`
      } else return null
    },
    setAgentFullName (objectValue) {
      if ((this.row.item.content_type === 'agentsailor' || this.row.item.content_type === 'statementagentsailor') &&
        this.row.item[objectValue]) {
        return `${this.row.item[objectValue].agent.last_name} ${this.row.item[objectValue].agent.first_name}
         ${this.row.item[objectValue].agent.userprofile.middle_name}`
      } else if ((this.row.item.content_type === 'statementagent' || this.row.item.content_type === 'userstatementverification') &&
        this.row.item[objectValue]) {
        return `${this.row.item[objectValue].last_name} ${this.row.item[objectValue].first_name} ${this.row.item[objectValue].middle_name}`
      } else return null
    },
    setFullName (objectValue, lang) {
      if (this.row.item[objectValue] && lang === 'ua') {
        return `${this.row.item[objectValue].last_name_ukr} ${this.row.item[objectValue].first_name_ukr}
         ${this.row.item[objectValue].middle_name_ukr}`
      } else if (this.row.item[objectValue] && lang === 'en') {
        return `${this.row.item[objectValue].last_name_eng} ${this.row.item[objectValue].first_name_eng}`
      } else return null
    },

    /** Check content type before call array checking methods */
    arrayChanges () {
      const positionChanges = ['qualitifcationdocument', 'proofofworkdiploma', 'statemenetqualificationdocument',
        'sailorstatementdkk', 'demandpositiondkk', 'protocolsqc', 'packetitem', 'statementsqc', 'qualificationdocument']
      if (positionChanges.includes(this.row.item.content_type) && this.row.item.old_obj_json && this.row.item.new_obj_json) {
        this.positionChanges()
      }
      if (this.row.item.content_type === 'lineinservicerecord' && (!this.row.item.new_obj_json.record_type ||
        this.row.item.new_obj_json.record_type === 'Довідка про стаж плавання') &&
        this.row.item.old_obj_json && this.row.item.new_obj_json) {
        this.responsibilitiesChanges()
      }
      const contactInfoChanges = ['statementagent', 'user', 'profile']
      if (contactInfoChanges.includes(this.row.item.content_type) && this.row.item.old_obj_json && this.row.item.new_obj_json) {
        this.contactInfoChanges()
      }
    },

    /** Detect position changes */
    positionChanges () {
      // Change "position" property name
      let positionProperyName = ''
      if (this.row.item.content_type === 'protocolsqc' || this.row.item.content_type === 'packetitem') {
        positionProperyName = 'position'
      } else positionProperyName = 'list_positions'

      // Get "added" and "exist" positions
      const addedPositionsArray = this.row.item.new_obj_json[positionProperyName].map(addedPositions => {
        if (this.row.item.old_obj_json[positionProperyName].some(value => value.id === addedPositions.id)) {
          return {
            id: addedPositions.id,
            name: addedPositions[this.langFields],
            status: 'exists'
          }
        } else {
          return {
            id: addedPositions.id,
            name: addedPositions[this.langFields],
            status: 'added'
          }
        }
      })
      // Get "deleted" and "exist" positions
      const deletedPositionsArray = this.row.item.old_obj_json[positionProperyName].map(deletedPositions => {
        if (this.row.item.new_obj_json[positionProperyName].some(value => value.id === deletedPositions.id)) {
          return {
            id: deletedPositions.id,
            name: deletedPositions[this.langFields],
            status: 'exists'
          }
        } else {
          return {
            id: deletedPositions.id,
            name: deletedPositions[this.langFields],
            status: 'deleted'
          }
        }
      })
      const positionsArray = addedPositionsArray.concat(deletedPositionsArray)
      this.clearArrayDuplicates(positionsArray)
    },

    /** Detect responsibilities changes */
    responsibilitiesChanges () {
      // Get "added" and "exist" responsibility
      const addedResponsibilitiesArray = this.row.item.new_obj_json.all_responsibility.reduce((result, addedResponsibility) => {
        if (addedResponsibility.responsibility) {
          if (this.row.item.old_obj_json.all_responsibility.some(value => value.responsibility &&
            value.responsibility.id === addedResponsibility.responsibility.id &&
            value.date_from === addedResponsibility.date_from &&
            value.date_to === addedResponsibility.date_to &&
            value.days_work === addedResponsibility.days_work)) {
            result.push({
              status: 'exists'
            })
          } else {
            result.push({
              status: 'added'
            })
          }
          result.name = addedResponsibility.responsibility[this.langFields]
          result.dateFrom = addedResponsibility.date_from ? getDateFormat(addedResponsibility.date_from) : null
          result.dateTo = addedResponsibility.date_to ? getDateFormat(addedResponsibility.date_to) : null
          result.totalDays = addedResponsibility.days_work
        }
        return result
      }, [])
      // Get "deleted" and "exist" responsibility
      const deletedResponsibilitiesArray = this.row.item.old_obj_json.all_responsibility.reduce((result, deletedResponsibility) => {
        if (deletedResponsibility.responsibility) {
          if (this.row.item.new_obj_json.all_responsibility.some(value => value.responsibility &&
            value.responsibility.id === deletedResponsibility.responsibility.id &&
            value.date_from === deletedResponsibility.date_from &&
            value.date_to === deletedResponsibility.date_to &&
            value.days_work === deletedResponsibility.days_work)) {
            result.push({
              status: 'exists'
            })
          } else {
            result.push({
              status: 'deleted'
            })
          }
          result.name = deletedResponsibility.responsibility[this.langFields]
          result.dateFrom = deletedResponsibility.date_from ? getDateFormat(deletedResponsibility.date_from) : null
          result.dateTo = deletedResponsibility.date_to ? getDateFormat(deletedResponsibility.date_to) : null
          result.totalDays = deletedResponsibility.days_work
        }
        return result
      }, [])
      const responsibilitiesArray = addedResponsibilitiesArray.concat(deletedResponsibilitiesArray)
      this.clearArrayDuplicates(responsibilitiesArray)
    },

    /** Detect contact info changes */
    contactInfoChanges () {
      // Change way to 'contact_info' array
      const contactArrayPropNew = this.row.item.content_type === 'user'
        ? this.row.item.new_obj_json.userprofile.contact_info
        : this.row.item.new_obj_json.contact_info
      const contactArrayPropOld = this.row.item.content_type === 'user'
        ? this.row.item.old_obj_json.userprofile.contact_info
        : this.row.item.old_obj_json.contact_info

      // Get "added" and "exist" contact info
      let addedContactArray = []
      if (contactArrayPropNew) {
        addedContactArray = contactArrayPropNew.map(addedContact => {
          if (contactArrayPropOld && contactArrayPropOld.some(value => value.type_contact === addedContact.type_contact &&
            value.value === addedContact.value)) {
            return {
              type_contact: this.setContactName(addedContact.type_contact),
              value: addedContact.value,
              status: 'exists'
            }
          } else {
            return {
              type_contact: this.setContactName(addedContact.type_contact),
              value: addedContact.value,
              status: 'added'
            }
          }
        })
      }
      // Get "deleted" and "exist" responsibility
      let deletedContactArray = []
      if (contactArrayPropOld) {
        deletedContactArray = contactArrayPropOld.map(deletedContact => {
          if (contactArrayPropNew.some(value => value.type_contact === deletedContact.type_contact && value.value === deletedContact.value)) {
            return {
              type_contact: this.setContactName(deletedContact.type_contact),
              value: deletedContact.value,
              status: 'exists'
            }
          } else {
            return {
              type_contact: this.setContactName(deletedContact.type_contact),
              value: deletedContact.value,
              status: 'deleted'
            }
          }
        })
      }
      const contactArray = addedContactArray.concat(deletedContactArray)
      this.clearArrayDuplicates(contactArray)
    },

    /** Clear duplicate object with status "exist" */
    clearArrayDuplicates (array) {
      this.arrayDifference = array.filter((value, index) => {
        const item = JSON.stringify(value)
        return (
          index === array.findIndex((obj) => {
            return JSON.stringify(obj) === item
          })
        )
      })
    },

    /** Correct date format view for new and old value */
    dateNewValue (prop) {
      if (this.row.item.new_obj_json[prop]) {
        return this.getDateFormat(this.row.item.new_obj_json[prop])
      } else return null
    },
    dateOldValue (prop) {
      if (this.row.item.old_obj_json && this.row.item.old_obj_json[prop]) {
        return this.getDateFormat(this.row.item.old_obj_json[prop])
      } else return null
    },

    /** Set contact name label depend on "type_contact" */
    setContactName (prop) {
      switch (prop) {
        case 'email':
        case '2':
          return this.$i18n.t('email')
        case 'phone_number':
        case '1':
          return this.$i18n.t('phoneNumber')
        case 'telegram':
        case '4':
          return 'Telegram'
        case 'viber':
        case '5':
          return 'Viber'
      }
    }
  }
}
