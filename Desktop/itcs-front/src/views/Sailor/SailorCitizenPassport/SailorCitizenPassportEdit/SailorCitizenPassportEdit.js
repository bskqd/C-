import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { mapState } from 'vuex'
import { required, maxLength, requiredIf, minLength, helpers, maxValue, minValue } from 'vuelidate/lib/validators'

const validPlaceIssued = helpers.regex('alpha', /^[a-zA-Z0-9а-щА-ЩЬьЮюЯяЇїІіЄєҐґ.'\-\s]*$/)

export default {
  name: 'SailorCitizenPassportEdit',
  props: {
    dataInfo: {
      type: Object,
      default: {}
    },
    finishEdit: Function
  },
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      registrationCitiesList: [],
      residentCitiesList: [],
      absentITN: false,
      sameResidentPlace: true
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      lang: state => state.main.lang,
      labelValue: state => (state.main.lang === 'en') ? 'value_eng' : 'value',
      // mapping documents
      mappingCountry: state => state.directory.country
    }),
    dateObject () {
      return this.dataInfo.date ? new Date(this.dataInfo.date) : null
    }
  },
  mounted () {
    if (Object.keys(this.dataInfo).length) {
      delete this.dataInfo.resident.id
      delete this.dataInfo.city_registration.id
      this.sameResidentPlace = JSON.stringify(this.dataInfo.city_registration) === (JSON.stringify(this.dataInfo.resident))
    } else {
      this.dataInfo = {
        city_registration: {
          city: {
            city: null,
            country: null,
            region: null
          }
        },
        resident: {
          city:
            {
              city: null,
              country: null,
              region: null
            }
        }
      }
    }
    if (!this.dataInfo.city_registration) {
      this.dataInfo.city_registration = {
        city: {
          city: null,
          country: null,
          region: null
        }
      }
    }
    if (!this.dataInfo.resident) {
      this.dataInfo.resident = {
        city: {
          city: null,
          country: null,
          region: null
        }
      }
    }
  },
  validations () {
    return {
      dateObject: {
        required,
        minValue: minValue(new Date('1900-01-01')),
        maxValue: maxValue(new Date())
      },
      dataInfo: {
        country: { required },
        serial: {
          required,
          maxLength: maxLength(30)
        },
        inn: {
          required: requiredIf(function () {
            return !this.absentITN
          })
        },
        issued_by: { required, validPlaceIssued },
        city_registration: {
          index: {
            required: requiredIf(function () {
              return this.dataInfo.country.id === 2
            }),
            maxLength: maxLength(7),
            minLength: minLength(4)
          },
          city: {
            country: {
              required: requiredIf(function () {
                return this.dataInfo.country.id === 2
              })
            },
            region: {
              required: requiredIf(function () {
                return this.dataInfo.country.id === 2
              })
            },
            city: {
              required: requiredIf(function () {
                return this.dataInfo.country.id === 2
              })
            }
          },
          street: {
            required: requiredIf(function () {
              return this.dataInfo.country.id === 2
            })
          },
          house: {
            required: requiredIf(function () {
              return this.dataInfo.country.id === 2
            })
          }
        },
        resident: {
          index: {
            required: requiredIf(function () {
              return !this.sameResidentPlace && this.dataInfo.country.id === 2
            }),
            maxLength: maxLength(7),
            minLength: minLength(4)
          },
          city: {
            country: {
              required: requiredIf(function () {
                return !this.sameResidentPlace && this.dataInfo.country.id === 2
              })
            },
            region: {
              required: requiredIf(function () {
                return !this.sameResidentPlace && this.dataInfo.country.id === 2
              })
            },
            city: {
              required: requiredIf(function () {
                return !this.sameResidentPlace && this.dataInfo.country.id === 2
              })
            }
          },
          street: {
            required: requiredIf(function () {
              return !this.sameResidentPlace && this.dataInfo.country.id === 2
            })
          },
          house: {
            required: requiredIf(function () {
              return !this.sameResidentPlace && this.dataInfo.country.id === 2
            })
          }
        }
      },
      photo: {
        $each: {
          size: { maxValue: maxValue(41943040) }
        }
      }
    }
  },
  methods: {
    mappingRegion (country) {
      if (country) {
        return this.$store.getters.regionById(country.id)
      } else return []
    },

    /** Search city by region id */
    mappingCityList (region, type) {
      this.dataInfo[type].city.city = []
      if (region) {
        const params = new URLSearchParams({ region: region.id })
        this.$api.get(`api/v1/directory/city/?${params}`).then(response => {
          if (type === 'city_registration') {
            this.registrationCitiesList = response.data
          } else {
            this.residentCitiesList = response.data
          }
        })
      } else return []
    },

    /**
     * check field validation
     */
    checkInfo () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.saveInfo()
    },

    /**
     * Save new info in edit passport info
     */
    saveInfo () {
      console.log(this.dataInfo)
      const body = {
        serial: this.dataInfo.serial.replace(/\s/g, ''),
        date: this.dataInfo.date,
        issued_by: this.dataInfo.issued_by,
        country: this.dataInfo.country.id,
        inn: this.absentITN ? '' : this.dataInfo.inn,
        city_registration: (this.dataInfo.city_registration)
          ? {
            city: this.dataInfo.city_registration.city.city.id,
            index: this.dataInfo.city_registration.index,
            street: this.dataInfo.city_registration.street,
            house: this.dataInfo.city_registration.house,
            flat: this.dataInfo.city_registration.flat
          }
          : null
        // resident: (this.dataInfo.resident)
        //   ? {
        //     city: this.dataInfo.resident.city.city.id,
        //     index: this.dataInfo.resident.index,
        //     street: this.dataInfo.resident.street,
        //     house: this.dataInfo.resident.house,
        //     flat: this.dataInfo.resident.flat
        //   }
        //   : null
      }
      if (this.sameResidentPlace) {
        body.resident = body.city_registration
      } else {
        body.resident = {
          city: this.dataInfo.resident.city.city.id,
          index: this.dataInfo.resident.index,
          street: this.dataInfo.resident.street,
          house: this.dataInfo.resident.house,
          flat: this.dataInfo.resident.flat
        }
      }

      let method, url

      if (!this.dataInfo.id) {
        method = 'post'
        url = `api/v2/sailor/${this.id}/citizen_passport/`
        body.sailor = this.id
      } else {
        method = 'patch'
        url = `api/v2/sailor/${this.id}/citizen_passport/${this.dataInfo.id}/`
        body.sailor = null
      }

      this.$api[method](url, body)
        .then(response => {
          switch (response.status) {
            case 'success':
            case 'created':
              this.$notification.success(this, this.$i18n.t('editCivilPassport'))

              const files = this.$refs.mediaContent.filesArray
              if (files.length) {
                this.$api.postPhoto(files, 'passport', this.id).then((response) => {
                  if (response.status === 'success' || response.status === 'created') {
                    this.finishEdit()
                  } else {
                    this.$notification.error(this, this.$i18n.t('errorAddFile'))
                  }
                })
              } else {
                this.finishEdit()
              }
              this.$store.dispatch('getSailorInformation', this.id)
              break
            case 'error':
              if (response.data.non_field_errors[0] === 'The fields serial, inn, country must make a unique set.') {
                this.$notification.error(this, this.$i18n.t('sailorExist'))
              } else if (response.data[0] === 'The sailor with such passport data is exist') {
                this.$notification.error(this, this.$i18n.t('sailorExist'))
              }
              break
          }
        })
    }
  }
}
