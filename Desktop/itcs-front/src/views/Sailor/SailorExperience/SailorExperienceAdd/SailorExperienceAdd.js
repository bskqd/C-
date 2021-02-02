import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { hideDetailed } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { maxLength, numeric, helpers, maxValue, minValue, requiredIf } from 'vuelidate/lib/validators'
import { mapState } from 'vuex'

const alphaUA = helpers.regex('alpha', /^[а-щА-ЩЬьЮюЯяЇїІіЄєҐґ'\-\s ]*$/)
const alphaEN = helpers.regex('alpha', /^[a-zA-Z'\- ]*$/)

function formFieldsInitialState () {
  return {
    typeDoc: null,
    // employment history fields (typeDoc.id = 2)
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
    swimArea: null,
    swimPorts: null,
    nameCap: null,
    firstNameCapEN: null,
    lastNameCapEN: null,
    responsibility: null,
    repairedDateFrom: null,
    repairedDateTo: null,
    repairedTotalDays: null,
    positionOnShip: null,
    hirePlace: null,
    hireDate: null,
    firePlace: null,
    fireDate: null,
    dateMax: null,
    dateMin: null,
    responsibilityPeriods: [],
    bookPractical: false,
    repairedShip: false,
    aparatusGMLZB: true,
    readonlyInputs: false,
    readonlyDateNum: false,
    // swimming experience docs fields below (typeDoc.id = 1)
    responsibilityWorkBook: null,
    workPlace: null,
    dateStart: null,
    dateEnd: null,
    totalDays: null,
    bookPracticalWorkBook: false,
    buttonLoader: false,
    mappingTypeDoc: [
      {
        id: 1,
        ua: 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо',
        en: 'Employment record book, certificate of professional experience, repairs, practice, etc.'
      },
      {
        id: 2,
        ua: 'Довідка про стаж плавання',
        en: 'Certificate of swimming experience'
      }
    ],
    mappingConventionalTypeDoc: [
      {
        id: 1,
        ua: 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо',
        en: 'Employment record book, certificate of professional experience, repairs, practice, etc.'
      }
    ]
  }
}

export default {
  name: 'SailorExperienceAdd',
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      dataForm: formFieldsInitialState(),
      hideDetailed,
      checkAccess
    }
  },
  computed: {
    ...mapState({
      lang: state => state.main.lang,
      id: state => state.sailor.sailorId,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      // mapping documents
      mappingTypeShip: state => state.directory.typeShip,
      mappingModeShipping: state => state.directory.modeShipping,
      mappingTypeGEU: state => state.directory.typeGEU,
      mappingPorts: state => state.directory.ports,
      mappingResponsibility: state => state.directory.responsibility,
      mappingResponsibilityWorkBook: state => state.directory.responsibilityWorkBook,
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
        typeShip: {
          required: requiredIf(function () {
            return this.dataForm.typeDoc.id === 2
          })
        },
        nameShip: {
          required: requiredIf(function () {
            return this.dataForm.typeDoc.id === 2
          }),
          maxLength: maxLength(255)
        },
        numShip: {
          required: requiredIf(function () {
            return this.dataForm.typeDoc.id === 2
          }),
          maxLength: maxLength(255)
        },
        modeShipping: {
          required: requiredIf(function () {
            return this.dataForm.typeDoc.id === 2
          })
        },
        portShip: {
          required: requiredIf(function () {
            return this.dataForm.typeDoc.id === 2
          })
        },
        ownerShip: { maxLength: maxLength(255) },
        grossCapacity: {
          required: requiredIf(function () {
            return this.dataForm.typeDoc.id === 2
          }),
          numeric
        },
        powerGEU: {
          required: requiredIf(function () {
            return this.dataForm.typeDoc.id === 2
          }),
          numeric
        },
        coldProductivity: { numeric },
        elEquipmentPower: { numeric },
        typeGEU: {
          required: requiredIf(function () {
            return this.dataForm.typeDoc.id === 2
          })
        },
        swimArea: {
          required: requiredIf(function () {
            return this.dataForm.typeDoc.id === 2
          })
        },
        swimPorts: {
          required: requiredIf(function () {
            return this.dataForm.typeDoc.id === 2
          })
        },
        nameCap: { maxLength: maxLength(300), alphaUA },
        firstNameCapEN: {
          required: requiredIf(function () {
            return this.dataForm.typeDoc.id === 2
          }),
          maxLength: maxLength(200),
          alphaEN
        },
        lastNameCapEN: {
          required: requiredIf(function () {
            return this.dataForm.typeDoc.id === 2
          }),
          maxLength: maxLength(200),
          alphaEN
        },
        positionOnShip: {
          required: requiredIf(function () {
            return this.dataForm.typeDoc.id === 2
          })
        },
        hirePlace: {
          required: requiredIf(function () {
            return this.dataForm.typeDoc.id === 2
          }),
          maxLength: maxLength(255)
        },
        firePlace: {
          required: requiredIf(function () {
            return this.dataForm.typeDoc.id === 2
          }),
          maxLength: maxLength(255)
        },
        responsibilityWorkBook: {
          required: requiredIf(function () {
            return this.dataForm.typeDoc.id === 1
          })
        },
        workPlace: {
          required: requiredIf(function () {
            return this.dataForm.typeDoc.id === 1
          })
        },
        dateStart: {
          required: requiredIf(function () {
            return this.dataForm.typeDoc.id === 1 && !this.dataForm.totalDays
          })
        },
        dateEnd: {
          required: requiredIf(function () {
            return this.dataForm.typeDoc.id === 1 && !this.dataForm.totalDays
          })
        },
        totalDays: {
          required: requiredIf(function () {
            return this.dataForm.typeDoc.id === 1 && !this.dataForm.dateStart && !this.dataForm.dateEnd
          })
        },
        repairedTotalDays: {
          required: requiredIf(function () {
            return this.dataForm.typeDoc.id === 2 && !this.dataForm.repairedDateTo &&
              !this.dataForm.repairedDateFrom && this.dataForm.repairedShip && !this.dataForm.readonlyDateNum
          })
        },
        responsibilityPeriods: {
          $each: {
            date_from: {
              required: requiredIf(function () {
                return this.dataForm.typeDoc.id === 2 && !this.dataForm.readonlyInputs
              })
            },
            date_to: {
              required: requiredIf(function () {
                return this.dataForm.typeDoc.id === 2 && !this.dataForm.readonlyInputs
              })
            },
            days_work: {
              required: requiredIf(function () {
                return this.dataForm.typeDoc.id === 2 && !this.dataForm.readonlyDateNum
              })
            }
          }
        }
      },
      hireDateObject: {
        required: requiredIf(function () {
          return this.dataForm.typeDoc.id === 2
        }),
        minValue: minValue(new Date('1900-01-01')),
        maxValue: maxValue(this.dataForm.fireDate ? this.fireDateObject : new Date())
      },
      fireDateObject: {
        required: requiredIf(function () {
          return this.dataForm.typeDoc.id === 2
        }),
        minValue: minValue(this.dataForm.hireDate ? this.hireDateObject : new Date('1900-01-01')),
        maxValue: maxValue(new Date())
      },
      repairedDateFromObject: {
        required: requiredIf(function () {
          return this.dataForm.typeDoc.id === 2 && !this.dataForm.repairedTotalDays &&
            this.dataForm.repairedShip && !this.dataForm.readonlyInputs
        }),
        minValue: minValue(this.dataForm.hireDate ? this.hireDateObject : new Date('1900-01-01')),
        maxValue: maxValue(this.dataForm.repairedDateTo ? this.repairedDateToObject : this.dataForm.fireDate)
      },
      repairedDateToObject: {
        required: requiredIf(function () {
          return this.dataForm.typeDoc.id === 2 && !this.dataForm.repairedTotalDays &&
            this.dataForm.repairedShip && !this.dataForm.readonlyInputs
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

    /** Check valid form field */
    checkInfo () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.saveNewExperienceDocument()
    },

    /** Save new experience document */
    saveNewExperienceDocument () {
      this.dataForm.buttonLoader = true
      const body = {
        sailor: parseInt(this.id),
        status_line: 5,
        record_type: this.dataForm.typeDoc.ua
      }
      if (this.dataForm.typeDoc.id === 1) {
        body.responsibility_work_book = this.dataForm.responsibilityWorkBook.id
        body.place_work = this.dataForm.workPlace
        body.date_start = this.dataForm.dateStart || null
        body.date_end = this.dataForm.dateEnd || null
        body.days_work = parseInt(this.dataForm.totalDays)
        body.book_registration_practical = Boolean(this.dataForm.bookPracticalWorkBook)
      } else {
        body.name_vessel = this.dataForm.nameShip
        body.type_vessel = this.dataForm.typeShip.id
        body.mode_of_navigation = this.dataForm.modeShipping.id
        body.port_of_registration = this.dataForm.portShip
        body.type_geu = this.dataForm.typeGEU.id
        body.ship_owner = this.dataForm.ownerShip
        body.number_vessel = this.dataForm.numShip
        body.propulsion_power = parseInt(this.dataForm.powerGEU)
        body.electrical_power = parseInt(this.dataForm.elEquipmentPower)
        body.all_responsibility = this.dataForm.responsibilityPeriods
        body.refrigerating_power = parseInt(this.dataForm.coldProductivity)
        body.book_registration_practical = Boolean(this.dataForm.bookPractical)
        body.position = this.dataForm.positionOnShip.id
        body.date_start = this.dataForm.hireDate
        body.place_start = this.dataForm.hirePlace
        body.place_end = this.dataForm.firePlace
        body.date_end = this.dataForm.fireDate
        body.full_name_master = this.dataForm.nameCap
        body.full_name_master_eng = `${this.dataForm.lastNameCapEN} ${this.dataForm.firstNameCapEN}`
        body.equipment_gmzlb = Boolean(this.dataForm.aparatusGMLZB)
        body.trading_area = this.dataForm.swimArea
        body.ports_input = this.dataForm.swimPorts
        body.gross_capacity = parseInt(this.dataForm.grossCapacity)
        body.levelRefrigerPlant = parseInt(this.dataForm.countLevelRefrigerPlant)
        body.is_repaired = this.dataForm.repairedShip
        body.repair_date_from = this.dataForm.repairedDateFrom
        body.repair_date_to = this.dataForm.repairedDateTo
        body.days_repair = parseInt(this.dataForm.repairedTotalDays)
      }

      this.$api.post(`api/v2/sailor/${this.id}/experience_certificate/`, body).then(response => {
        this.dataForm.buttonLoader = false
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

            this.$notification.success(this, this.$i18n.t('addedExperienceDoc'))
            this.$store.commit('addDataSailor', { type: 'experience', value: response.data })
            this.$parent.viewAdd = false
            this.$store.commit('incrementBadgeCount', {
              child: 'experienceDocument',
              parent: 'experienceAll'
            })
            this.$store.commit('incrementUserNotification', 'documents_on_verification')
            this.$data.dataForm = formFieldsInitialState()
            this.$v.$reset()
            break
          case 'error':
            if (response.data[0] === 'days longer') {
              this.$notification.warning(this, this.$i18n.t('daysLonger'))
            } else if (response.data[0] === 'wrong date intervals') {
              this.$notification.error(this, this.$i18n.t('wrongIntervals'))
            }
            break
        }
      })
    }
  }
}
