import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { mapState } from 'vuex'
import { hideDetailed, showDetailed } from '@/functions/main'
import { required, maxLength, numeric, helpers, maxValue, minValue, requiredIf } from 'vuelidate/lib/validators'

const alphaUA = helpers.regex('alpha', /^[а-щА-ЩЬьЮюЯяЇїІіЄєҐґ'\-\s ]*$/)
const alphaEN = helpers.regex('alpha', /^[a-zA-Z'\- ]*$/)

function formFieldsInitialState () {
  return {
    nameShip: null,
    typeShip: null,
    numShip: null,
    modeShipping: null,
    portShip: null,
    ownerShip: null,
    grossCapacity: '',
    powerGEU: '',
    coldProductivity: '',
    elEquipmentPower: '',
    countLevelRefrigerPlant: '',
    typeGEU: null,
    aparatusGMLZB: true,
    swimArea: null,
    swimPorts: null,
    nameCap: null,
    responsibility: null,
    bookPractical: false,
    positionOnShip: null,
    hirePlace: null,
    hireDate: null,
    firePlace: null,
    fireDate: null,
    lastNameCapEN: null,
    firstNameCapEN: null,
    numberPageBook: null,
    repairedDateFrom: null,
    repairedDateTo: null,
    repairedTotalDays: null,
    responsibilityPeriods: [],
    repairedShip: false,
    readonlyInputs: false,
    readonlyDateNum: false
  }
}

export default {
  name: 'SailorRecordBookLineAdd',
  props: {
    sailorDocument: Object
  },
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      dataForm: formFieldsInitialState(),
      buttonLoader: false,
      showDetailed,
      hideDetailed
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      lang: state => state.main.lang,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      // mapping documents
      mappingTypeShip: state => state.directory.typeShip,
      mappingModeShipping: state => state.directory.modeShipping,
      mappingTypeGEU: state => state.directory.typeGEU,
      mappingResponsibility: state => state.directory.responsibility,
      mappingPositionsShip: state => state.directory.positionsShip
    }),
    hireDateObject () {
      return this.dataForm.hireDate ? new Date(this.dataForm.hireDate) : null
    },
    fireDateObject () {
      return this.dataForm.fireDate ? new Date(this.dataForm.fireDate) : null
    },
    repairedDateFromObject () {
      return this.dataForm.repairedDateFrom ? new Date(this.dataForm.repairedDateFrom) : null
    },
    repairedDateToObject () {
      return this.dataForm.repairedDateTo ? new Date(this.dataForm.repairedDateTo) : null
    }
  },
  validations () {
    return {
      dataForm: {
        typeShip: { required },
        nameShip: { required, maxLength: maxLength(255) },
        numShip: { required, maxLength: maxLength(255) },
        modeShipping: { required },
        portShip: { required },
        ownerShip: { maxLength: maxLength(255) },
        grossCapacity: { required, numeric },
        powerGEU: { required, numeric },
        coldProductivity: { numeric },
        elEquipmentPower: { numeric },
        typeGEU: { required },
        swimArea: { required },
        swimPorts: { required },
        nameCap: { maxLength: maxLength(300), alphaUA },
        firstNameCapEN: { required, maxLength: maxLength(200), alphaEN },
        lastNameCapEN: { required, maxLength: maxLength(200), alphaEN },
        positionOnShip: { required },
        hirePlace: { required, maxLength: maxLength(255) },
        firePlace: { required, maxLength: maxLength(255) },
        numberPageBook: { required },
        repairedTotalDays: {
          required: requiredIf(function () {
            return !this.dataForm.repairedDateTo && !this.dataForm.repairedDateFrom &&
              this.dataForm.repairedShip && !this.dataForm.readonlyDateNum
          })
        },
        responsibilityPeriods: {
          $each: {
            date_from: {
              required: requiredIf(function () {
                return !this.dataForm.readonlyInputs
              })
            },
            date_to: {
              required: requiredIf(function () {
                return !this.dataForm.readonlyInputs
              })
            },
            days_work: {
              required: requiredIf(function () {
                return !this.dataForm.readonlyDateNum
              })
            }
          }
        }
      },
      hireDateObject: {
        required,
        minValue: minValue(new Date('1900-01-01')),
        maxValue: maxValue(this.dataForm.fireDate ? this.fireDateObject : new Date())
      },
      fireDateObject: {
        required,
        minValue: minValue(this.dataForm.hireDate ? this.hireDateObject : new Date('1900-01-01')),
        maxValue: maxValue(new Date())
      },
      repairedDateFromObject: {
        required: requiredIf(function () {
          return !this.dataForm.repairedTotalDays && this.dataForm.repairedShip && !this.dataForm.readonlyInputs
        }),
        minValue: minValue(this.dataForm.hireDate ? this.hireDateObject : new Date('1900-01-01')),
        maxValue: maxValue(this.dataForm.repairedDateTo ? this.repairedDateToObject : this.dataForm.fireDate)
      },
      repairedDateToObject: {
        required: requiredIf(function () {
          return !this.dataForm.repairedTotalDays && this.dataForm.repairedShip && !this.dataForm.readonlyInputs
        }),
        minValue: minValue(this.dataForm.repairedDateFrom ? this.repairedDateFromObject : this.hireDateObject),
        maxValue: maxValue(this.dataForm.fireDate ? this.fireDateObject : new Date())
      }
    }
  },
  methods: {
    /** Change readonly/disable property depends on which date format was entered first */
    displayDateInputs (element) {
      switch (element) {
        case 'responsibility':
          this.dataForm.responsibilityPeriods.forEach(record => {
            if ((record.date_to || record.date_from) && !record.days_work) {
              this.dataForm.readonlyInputs = false
              this.dataForm.readonlyDateNum = true
            } else if (record.days_work && (!record.date_from || !record.date_to)) {
              this.dataForm.readonlyInputs = true
              this.dataForm.readonlyDateNum = false
            } else if (!record.days_work && !record.date_from && !record.date_to) {
              this.dataForm.readonlyInputs = false
              this.dataForm.readonlyDateNum = false
            }
          })
          break
        case 'repairing':
          if ((this.dataForm.repairedDateTo || this.dataForm.repairedDateFrom) && !this.dataForm.repairedTotalDays) {
            this.dataForm.readonlyInputs = false
            this.dataForm.readonlyDateNum = true
          } else if ((!this.dataForm.repairedDateTo || !this.dataForm.repairedDateFrom) && this.dataForm.repairedTotalDays) {
            this.dataForm.readonlyInputs = true
            this.dataForm.readonlyDateNum = false
          } else if (!this.dataForm.repairedDateTo && !this.dataForm.repairedDateFrom && !this.dataForm.repairedTotalDays) {
            this.dataForm.readonlyInputs = false
            this.dataForm.readonlyDateNum = false
          }
          break
      }
    },

    /** Adding and removing periods date */
    addResponsibility (resp) {
      if (resp) {
        this.dataForm.responsibilityPeriods.push({
          responsibility: resp.id,
          ua: resp.name_ukr,
          en: resp.name_eng,
          days_work: null,
          date_from: null,
          date_to: null,
          is_repaired: false
        })
      }
    },
    deleteResponsibility (index) {
      this.dataForm.responsibilityPeriods.splice(index, 1)
    },

    /** Check newEntry fields validation before submit */
    checkSavingNewEntry () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.saveNewEntry()
    },

    /** Save newEntry in record book */
    saveNewEntry () {
      this.buttonLoader = true
      const body = {
        service_record: this.sailorDocument.id,
        name_vessel: this.dataForm.nameShip,
        type_vessel: this.dataForm.typeShip.id,
        port_of_registration: this.dataForm.portShip,
        mode_of_navigation: this.dataForm.modeShipping.id,
        type_geu: this.dataForm.typeGEU.id,
        ship_owner: this.dataForm.ownerShip,
        number_vessel: this.dataForm.numShip,
        propulsion_power: parseInt(this.dataForm.powerGEU),
        electrical_power: parseInt(this.dataForm.elEquipmentPower),
        all_responsibility: this.dataForm.responsibilityPeriods,
        refrigerating_power: parseInt(this.dataForm.coldProductivity),
        book_registration_practical: Boolean(this.dataForm.bookPractical),
        position: this.dataForm.positionOnShip.id,
        date_start: this.dataForm.hireDate,
        place_start: this.dataForm.hirePlace,
        place_end: this.dataForm.firePlace,
        date_end: this.dataForm.fireDate,
        full_name_master: this.dataForm.nameCap,
        full_name_master_eng: this.dataForm.lastNameCapEN + ' ' + this.dataForm.firstNameCapEN,
        equipment_gmzlb: Boolean(this.dataForm.aparatusGMLZB),
        trading_area: this.dataForm.swimArea,
        ports_input: this.dataForm.swimPorts,
        status_line: 5,
        gross_capacity: parseInt(this.dataForm.grossCapacity),
        levelRefrigerPlant: parseInt(this.dataForm.countLevelRefrigerPlant),
        number_page_book: this.dataForm.numberPageBook,
        is_repaired: this.dataForm.repairedShip,
        repair_date_from: this.dataForm.repairedDateFrom,
        repair_date_to: this.dataForm.repairedDateTo,
        days_repair: parseInt(this.dataForm.repairedTotalDays)
      }
      this.$api.post(`api/v2/sailor/${this.id}/service_record/${this.sailorDocument.id}/line/`, body).then(response => {
        this.buttonLoader = false
        switch (response.status) {
          case 'created':
            const files = this.$refs.mediaContent.filesArray
            if (files.length) {
              this.$api.postPhoto(files, 'ExperienceDoc', response.data.id).then((response) => {
                if (response.status !== 'created' && response.status !== 'success') {
                  this.$notification.error(this, this.$i18n.t('errorAddFile'))
                }
              })
            }

            this.$notification.success(this, this.$i18n.t('addedRecordBook'))
            this.$store.commit('addDataSailor', { type: 'serviceRecordBookLine', value: response.data })
            this.$store.commit('incrementUserNotification', 'documents_on_verification')
            this.$data.dataForm = formFieldsInitialState()
            this.$v.$reset()
            break
          case 'error':
            if (response.data[0] === 'days longer') {
              this.$notification.warning(this, this.$i18n.t('daysLonger'))
            } else if (response.data[0] === 'wrong date intervals') {
              this.$notification.warning(this, this.$i18n.t('wrongIntervals'))
            }
            break
        }
      })
    }
  }
}
