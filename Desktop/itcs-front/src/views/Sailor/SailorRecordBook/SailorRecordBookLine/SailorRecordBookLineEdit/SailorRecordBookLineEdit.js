import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { hideDetailed } from '@/mixins/main'
import { required, maxLength, helpers, maxValue, requiredIf, minValue } from 'vuelidate/lib/validators'
import { mapState } from 'vuex'

const alphaUA = helpers.regex('alpha', /^[а-щА-ЩЬьЮюЯяЇїІіЄєҐґ'\-\s ]*$/)
const alphaEN = helpers.regex('alpha', /^[a-zA-Z'\- ]*$/)

export default {
  name: 'SailorRecordBookLineEdit',
  props: {
    sailorDocument: Object
  },
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      responsibility: null,
      buttonLoader: false,
      readonlyInputs: false,
      readonlyDateNum: false,
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
    dateStartObject () {
      return this.sailorDocument.date_start ? new Date(this.sailorDocument.date_start) : null
    },
    dateEndObject () {
      return this.sailorDocument.date_end ? new Date(this.sailorDocument.date_end) : null
    },
    repairedDateFromObject () {
      return this.sailorDocument.repair_date_from ? new Date(this.sailorDocument.repair_date_from) : null
    },
    repairedDateToObject () {
      return this.sailorDocument.repair_date_to ? new Date(this.sailorDocument.repair_date_to) : null
    }
  },
  mounted () {
    if (this.sailorDocument.all_responsibility) {
      this.displayDateInputs('responsibility')
    }
    if (this.sailorDocument.is_repaired) {
      this.displayDateInputs('repairing')
    }
  },
  validations () {
    return {
      sailorDocument: {
        number_vessel: { required, maxLength: maxLength(255) },
        name_vessel: { required, maxLength: maxLength(255) },
        port_of_registration: { required },
        ship_owner: { maxLength: maxLength(255) },
        gross_capacity: { required },
        propulsion_power: { required },
        trading_area: { required },
        ports_input: { required },
        full_name_master: { maxLength: maxLength(300), alphaUA },
        full_name_master_eng: { required, maxLength: maxLength(300), alphaEN },
        place_start: { required, maxLength: maxLength(255) },
        place_end: { required, maxLength: maxLength(255) },
        number_page_book: { required },
        days_repair: {
          required: requiredIf(function () {
            return !this.sailorDocument.repair_date_to && !this.sailorDocument.repair_date_from && this.sailorDocument.is_repaired && !this.readonlyDateNum
          })
        },
        all_responsibility: {
          $each: {
            date_from: {
              required: requiredIf(function (value) {
                return !this.readonlyInputs && value.responsibility
              })
            },
            date_to: {
              required: requiredIf(function (value) {
                return !this.readonlyInputs && value.responsibility
              })
            },
            days_work: {
              required: requiredIf(function (value) {
                return !this.readonlyDateNum && value.responsibility
              })
            }
          }
        }
      },
      dateStartObject: {
        required,
        minValue: minValue(new Date('1900-01-01')),
        maxValue: maxValue(this.sailorDocument.date_end ? this.dateEndObject : new Date())
      },
      dateEndObject: {
        required,
        minValue: minValue(this.sailorDocument.date_start ? this.dateStartObject : new Date('1900-01-01')),
        maxValue: maxValue(new Date())
      },
      repairedDateFromObject: {
        required: requiredIf(function () {
          return !this.sailorDocument.days_repair && this.sailorDocument.is_repaired && !this.readonlyInputs
        }),
        minValue: minValue(this.sailorDocument.date_start ? this.dateStartObject : new Date('1900-01-01')),
        maxValue: maxValue(this.sailorDocument.repair_date_to ? this.repairedDateToObject : this.sailorDocument.date_end)
      },
      repairedDateToObject: {
        required: requiredIf(function () {
          return !this.sailorDocument.days_repair && this.sailorDocument.is_repaired && !this.readonlyInputs
        }),
        minValue: minValue(this.sailorDocument.repair_date_from ? this.repairedDateFromObject : this.sailorDocument.date_start),
        maxValue: maxValue(this.sailorDocument.date_end ? this.dateEndObject : new Date())
      }
    }
  },
  methods: {
    /** Change readonly/disable property depends on which date format was entered first */
    displayDateInputs (element) {
      switch (element) {
        case 'responsibility':
          this.sailorDocument.all_responsibility.forEach(record => {
            if (record.responsibility && !this.sailorDocument.repair_date_to && !this.sailorDocument.repair_date_from && !this.sailorDocument.days_repair) {
              if ((record.date_to || record.date_from) && !record.days_work) {
                this.readonlyInputs = false
                this.readonlyDateNum = true
              } else if (record.days_work && (!record.date_from || !record.date_to)) {
                this.readonlyInputs = true
                this.readonlyDateNum = false
              } else if (!record.days_work && !record.date_from && !record.date_to) {
                this.readonlyInputs = false
                this.readonlyDateNum = false
              }
            }
          })
          break
        case 'repairing':
          if ((this.sailorDocument.repair_date_to || this.sailorDocument.repair_date_from) && !this.sailorDocument.days_repair) {
            this.readonlyInputs = false
            this.readonlyDateNum = true
          } else if ((!this.sailorDocument.repair_date_to || !this.sailorDocument.repair_date_from) && this.sailorDocument.days_repair) {
            this.readonlyInputs = true
            this.readonlyDateNum = false
          } else if (!this.sailorDocument.repair_date_to && !this.sailorDocument.repair_date_from && !this.sailorDocument.days_repair) {
            this.readonlyInputs = false
            this.readonlyDateNum = false
          }
          break
      }
    },

    /** Adding and removing periods date */
    addResponsibility (resp) {
      if (resp) {
        this.sailorDocument.all_responsibility.push({
          responsibility: {
            id: resp.id,
            name_ukr: resp.name_ukr,
            name_eng: resp.name_eng
          },
          days_work: null,
          date_from: null,
          date_to: null
        })
      }
    },
    deleteResponsibility (index) {
      this.sailorDocument.all_responsibility.splice(index, 1)
    },

    /** Check fields validation before submit */
    checkEditedDocumentLine () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.saveEditDocumentLine()
    },

    /** Save edited line in record */
    saveEditDocumentLine () {
      this.buttonLoader = true
      const responsibilities = []
      this.sailorDocument.all_responsibility.forEach(value => {
        if (value.responsibility) {
          responsibilities.push({
            responsibility: value.responsibility.id,
            days_work: value.days_work ? parseInt(value.days_work) : null,
            date_from: value.date_from ? value.date_from : null,
            date_to: value.date_to ? value.date_to : null
          })
        }
      })
      const body = {
        number_vessel: this.sailorDocument.number_vessel,
        name_vessel: this.sailorDocument.name_vessel,
        type_vessel: this.sailorDocument.type_vessel.id,
        mode_of_navigation: this.sailorDocument.mode_of_navigation.id,
        port_of_registration: this.sailorDocument.port_of_registration,
        ship_owner: this.sailorDocument.ship_owner,
        gross_capacity: parseInt(this.sailorDocument.gross_capacity),
        propulsion_power: parseInt(this.sailorDocument.propulsion_power),
        type_geu: this.sailorDocument.type_geu.id,
        trading_area: this.sailorDocument.trading_area,
        ports_input: this.sailorDocument.ports_input,
        full_name_master_eng: this.sailorDocument.full_name_master_eng,
        all_responsibility: responsibilities,
        position: this.sailorDocument.position.id,
        date_start: this.sailorDocument.date_start,
        date_end: this.sailorDocument.date_end,
        place_start: this.sailorDocument.place_start,
        place_end: this.sailorDocument.place_end,
        number_page_book: this.sailorDocument.number_page_book,
        is_repaired: this.sailorDocument.is_repaired,
        repair_date_from: this.sailorDocument.repair_date_from || null,
        repair_date_to: this.sailorDocument.repair_date_to || null,
        days_repair: parseInt(this.sailorDocument.days_repair),
        // not required fields below
        equipment_gmzlb: this.sailorDocument.equipment_gmzlb,
        book_registration_practical: this.sailorDocument.book_registration_practical,
        levelRefrigerPlant: parseInt(this.sailorDocument.levelRefrigerPlant),
        full_name_master: this.sailorDocument.full_name_master,
        electrical_power: parseInt(this.sailorDocument.electrical_power),
        refrigerating_power: parseInt(this.sailorDocument.refrigerating_power)
      }
      this.$api.patch(`api/v2/sailor/${this.id}/service_record/${this.sailorDocument.service_record}/line/${this.sailorDocument.id}/`, body)
        .then(response => {
          this.buttonLoader = false
          switch (response.status) {
            case 'success':
              const files = this.$refs.mediaContent.filesArray
              if (files.length) {
                this.$api.postPhoto(files, 'ExperienceDoc', response.data.id).then((response) => {
                  if (response.status !== 'created' && response.status !== 'success') {
                    this.$notification.error(this, this.$i18n.t('errorAddFile'))
                  }
                })
              }
              this.$notification.success(this, this.$i18n.t('editInfoRecordBook'))
              this.$store.commit('updateDataSailor', { type: 'serviceRecordBookLine', value: response.data })
              break
            case 'error':
              if (response.data[0] === 'days longer') {
                this.$notification.warning(this, this.$i18n.t('daysLonger'))
              } else if (response.data[0] === 'wrong date intervals') {
                this.$notification.warning(this, this.$i18n.t('wrongIntervals'))
              } else if (response.data[0] === 'Must be only interval or days') {
                this.$notification.warning(this, this.$i18n.t('usePeriodsOrTotal'))
              }
              break
          }
        })
    }
  }
}
