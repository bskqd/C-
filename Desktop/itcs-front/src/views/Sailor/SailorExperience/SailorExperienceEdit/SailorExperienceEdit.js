import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { hideDetailed } from '@/mixins/main'
import { maxLength, numeric, helpers, requiredIf, maxValue, minValue } from 'vuelidate/lib/validators'
import { mapState } from 'vuex'
const alphaUA = helpers.regex('alpha', /^[а-щА-ЩЬьЮюЯяЇїІіЄєҐґ'\-\s]*$/)
const alphaEN = helpers.regex('alpha', /^[a-zA-Z'\-\s]*$/)

export default {
  name: 'SailorExperienceEdit',
  props: {
    sailorDocument: Object
  },
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      hideDetailed,
      buttonLoader: false,
      readonlyInputs: false,
      readonlyDateNum: false,
      responsibility: null
    }
  },
  computed: {
    ...mapState({
      lang: state => state.main.lang,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      id: state => state.sailor.sailorId,
      // mapping documents
      mappingTypeShip: state => state.directory.typeShip,
      mappingModeShipping: state => state.directory.modeShipping,
      mappingTypeGEU: state => state.directory.typeGEU,
      mappingPorts: state => state.directory.ports,
      mappingResponsibility: state => state.directory.responsibility,
      mappingResponsibilityWorkBook: state => state.directory.responsibilityWorkBook,
      mappingPositionsShip: state => state.directory.positionsShip
    }),
    dateStartObject () {
      return this.sailorDocument.date_start ? new Date(this.sailorDocument.date_start) : null
    },
    dateEndObject () {
      return this.sailorDocument.date_end ? new Date(this.sailorDocument.date_end) : null
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
        number_vessel: {
          required: requiredIf(function () {
            return this.sailorDocument.record_type !== 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо'
          }),
          maxLength: maxLength(255)
        },
        name_vessel: {
          required: requiredIf(function () {
            return this.sailorDocument.record_type !== 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо'
          }),
          maxLength: maxLength(255)
        },
        port_of_registration: {
          required: requiredIf(function () {
            return this.sailorDocument.record_type !== 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо'
          })
        },
        ship_owner: { maxLength: maxLength(255) },
        gross_capacity: {
          required: requiredIf(function () {
            return this.sailorDocument.record_type !== 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо'
          }),
          numeric
        },
        propulsion_power: {
          required: requiredIf(function () {
            return this.sailorDocument.record_type !== 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо'
          }),
          numeric
        },
        refrigerating_power: { numeric },
        electrical_power: { numeric },
        trading_area: {
          required: requiredIf(function () {
            return this.sailorDocument.record_type !== 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо'
          })
        },
        ports_input: {
          required: requiredIf(function () {
            return this.sailorDocument.record_type !== 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо'
          })
        },
        full_name_master: { alphaUA },
        full_name_master_eng: {
          required: requiredIf(function () {
            return this.sailorDocument.record_type !== 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо'
          }),
          alphaEN
        },
        repair_date_from: {
          required: requiredIf(function () {
            return this.sailorDocument.record_type !== 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо' &&
              !this.sailorDocument.days_repair && this.sailorDocument.is_repaired && !this.readonlyInputs
          }),
          minValue: minValue(this.sailorDocument.date_start ? this.dateStartObject : new Date('1900-01-01')),
          maxValue: maxValue(this.sailorDocument.date_end ? this.dateEndObject : new Date('2200-01-01'))
        },
        repair_date_to: {
          required: requiredIf(function () {
            return this.sailorDocument.record_type !== 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо' &&
              !this.sailorDocument.days_repair && this.sailorDocument.is_repaired && !this.readonlyInputs
          }),
          minValue: minValue(this.sailorDocument.date_start ? this.dateStartObject : new Date('1900-01-01')),
          maxValue: maxValue(this.sailorDocument.date_end ? this.dateEndObject : new Date('2200-01-01'))
        },
        days_repair: {
          required: requiredIf(function () {
            return this.sailorDocument.record_type !== 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо' &&
              !this.sailorDocument.repair_date_to && !this.sailorDocument.repair_date_from && this.sailorDocument.is_repaired && !this.readonlyDateNum
          })
        },
        place_start: {
          required: requiredIf(function () {
            return this.sailorDocument.record_type !== 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо'
          }),
          maxLength: maxLength(255)
        },
        place_end: {
          required: requiredIf(function () {
            return this.sailorDocument.record_type !== 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо'
          }),
          maxLength: maxLength(255)
        },
        responsibility_work_book: {
          required: requiredIf(function () {
            return this.sailorDocument.record_type === 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо'
          })
        },
        place_work: {
          required: requiredIf(function () {
            return this.sailorDocument.record_type === 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо'
          })
        },
        days_work: {
          required: requiredIf(function () {
            return this.sailorDocument.record_type === 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо' &&
              !this.sailorDocument.date_start && !this.sailorDocument.date_end
          })
        },
        all_responsibility: {
          $each: {
            date_from: {
              required: requiredIf(function (value) {
                return this.sailorDocument.record_type !== 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо' &&
                  !this.readonlyInputs && value.responsibility
              })
              // TODO: responsibilities preiods date validation
              // minValue: minValue(this.sailorDocument.date_start ? this.dateStartObject : new Date('1900-01-01')),
              // maxValue: maxValue(this.sailorDocument.date_end ? this.dateEndObject : new Date('2200-01-01'))
            },
            date_to: {
              required: requiredIf(function (value) {
                return this.sailorDocument.record_type !== 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо' &&
                  !this.readonlyInputs && value.responsibility
              })
              // minValue: minValue(this.sailorDocument.date_start ? this.dateStartObject : new Date('1900-01-01')),
              // maxValue: maxValue(this.sailorDocument.date_end ? this.dateEndObject : new Date('2200-01-01'))
            },
            days_work: {
              required: requiredIf(function (value) {
                return this.sailorDocument.record_type !== 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо' &&
                  !this.readonlyDateNum && value.responsibility
              })
            }
          }
        }
      },
      dateStartObject: {
        required: requiredIf(function () {
          return (this.sailorDocument.record_type !== 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо') ||
            (this.sailorDocument.record_type === 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо' &&
              !this.sailorDocument.days_work)
        }),
        minValue: minValue(new Date('1900-01-01')),
        maxValue: maxValue(this.sailorDocument.date_end ? this.dateEndObject : new Date())
      },
      dateEndObject: {
        required: requiredIf(function () {
          return (this.sailorDocument.record_type !== 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо') ||
            (this.sailorDocument.record_type === 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо' &&
              !this.sailorDocument.days_work)
        }),
        minValue: minValue(this.sailorDocument.date_start ? this.dateStartObject : new Date('1900-01-01')),
        maxValue: maxValue(new Date())
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

    /**
     * Edit document
     * __________
     * @function checkEditedDocument - validation data for save edited document
     * ..........
     * @function saveEditDocument - save edited document
     */
    checkEditedDocument () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.saveEditDocument()
    },

    /** Save edit info in record */
    saveEditDocument () {
      this.buttonLoader = true
      const responsibilities = []
      this.sailorDocument.all_responsibility.forEach(value => {
        if (value.responsibility) {
          responsibilities.push({
            responsibility: value.responsibility.id,
            ua: value.ua,
            en: value.en,
            days_work: value.days_work ? parseInt(value.days_work) : null,
            date_from: value.date_from ? value.date_from : null,
            date_to: value.date_to ? value.date_to : null
          })
        }
      })

      let body = {}
      if (this.sailorDocument.record_type === 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо') {
        body = {
          responsibility_work_book: this.sailorDocument.responsibility_work_book.id,
          date_start: this.sailorDocument.date_start ? this.sailorDocument.date_start : null,
          date_end: this.sailorDocument.date_end ? this.sailorDocument.date_end : null,
          days_work: parseInt(this.sailorDocument.days_work),
          place_work: this.sailorDocument.place_work,
          book_registration_practical: Boolean(this.sailorDocument.book_registration_practical)
        }
      } else {
        body = {
          number_vessel: this.sailorDocument.number_vessel,
          name_vessel: this.sailorDocument.name_vessel,
          type_vessel: this.sailorDocument.type_vessel.id,
          mode_of_navigation: this.sailorDocument.mode_of_navigation.id,
          date_start: this.sailorDocument.date_start,
          date_end: this.sailorDocument.date_end,
          gross_capacity: parseInt(this.sailorDocument.gross_capacity),
          propulsion_power: parseInt(this.sailorDocument.propulsion_power),
          type_geu: this.sailorDocument.type_geu.id,
          trading_area: this.sailorDocument.trading_area,
          ports_input: this.sailorDocument.ports_input,
          position: this.sailorDocument.position.id,
          place_start: this.sailorDocument.place_start,
          place_end: this.sailorDocument.place_end,
          full_name_master_eng: this.sailorDocument.full_name_master_eng,
          is_repaired: this.sailorDocument.is_repaired,
          repair_date_from: this.sailorDocument.repair_date_from || null,
          repair_date_to: this.sailorDocument.repair_date_to || null,
          days_repair: parseInt(this.sailorDocument.days_repair),
          // not required fields below
          ship_owner: this.sailorDocument.ship_owner || '',
          port_of_registration: this.sailorDocument.port_of_registration,
          equipment_gmzlb: this.sailorDocument.equipment_gmzlb,
          book_registration_practical: this.sailorDocument.book_registration_practical,
          levelRefrigerPlant: parseInt(this.sailorDocument.levelRefrigerPlant),
          full_name_master: this.sailorDocument.full_name_master,
          all_responsibility: responsibilities,
          electrical_power: this.sailorDocument.electrical_power ? parseInt(this.sailorDocument.electrical_power) : null,
          refrigerating_power: this.sailorDocument.refrigerating_power ? parseInt(this.sailorDocument.refrigerating_power) : null
        }
      }
      this.$api.patch(`api/v2/sailor/${this.id}/experience_certificate/${this.sailorDocument.id}/`, body).then(response => {
        this.buttonLoader = false
        switch (response.status) {
          case 'success':
            const files = this.$refs.mediaContent.filesArray
            if (files.length) {
              this.$api.postPhoto(files, 'ExperienceDoc', this.sailorDocument.id).then((response) => {
                if (response.status !== 'success' && response.status !== 'created') {
                  this.$notification.error(this, this.$i18n.t('errorAddFile'))
                }
              })
            }
            this.$notification.success(this, this.$i18n.t('infoExperienceDoc'))
            this.$store.commit('updateDataSailor', { type: 'experience', value: response.data })
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
