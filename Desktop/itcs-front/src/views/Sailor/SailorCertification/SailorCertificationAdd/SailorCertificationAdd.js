import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { required, numeric, minValue, maxValue } from 'vuelidate/lib/validators'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

function formFieldsInitialState () {
  return {
    number: null,
    eti: null,
    course: null,
    dateStart: null,
    dateEnd: null,
    status: null,
    onlyForDPD: false
  }
}

export default {
  name: 'SailorCertificationAdd',
  components: {
    ValidationAlert
  },
  data () {
    return {
      dataForm: formFieldsInitialState(),
      buttonLoader: false,
      checkAccess
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      lang: state => state.main.lang,
      labelNameShort: state => (state.main.lang === 'en') ? 'name_en' : 'name',
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      // mapping documents
      mappingETI: state => state.directory.educationTraining,
      mappingCourses: state => state.directory.courses,
      // permissions
      permissionSuperAdmin: state => state.main.permissions.superAdmin,
      permissionAddCertificatesETI: state => state.main.permissions.addCertificatesETI
    }),
    mappingStatuses () {
      if (this.permissionAddCertificatesETI && !this.permissionSuperAdmin) {
        return this.$store.getters.statusChoose('ETI')
      } else {
        return this.$store.getters.statusChoose('ServiceRecord')
      }
    },
    dateStartObject () {
      return this.dataForm.dateStart ? new Date(this.dataForm.dateStart) : null
    },
    dateEndObject () {
      return this.dataForm.dateEnd ? new Date(this.dataForm.dateEnd) : null
    }
  },
  validations () {
    return {
      dataForm: {
        number: { required, numeric },
        eti: { required },
        course: { required },
        status: { required }
      },
      dateStartObject: {
        required,
        minValue: minValue(new Date('1900-01-01')),
        maxValue: maxValue(new Date())
      },
      dateEndObject: {
        required,
        minValue: minValue(this.dataForm.dateStart ? this.dateStartObject : new Date('1900-01-01')),
        maxValue: maxValue(new Date('2200-12-31'))
      }
    }
  },
  methods: {
    validateForm () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.saveNewCertificate()
    },

    saveNewCertificate () {
      this.buttonLoader = true
      const body = {
        sailor: parseInt(this.id),
        ntz: this.dataForm.eti.id,
        ntz_number: this.dataForm.number,
        course_traning: this.dataForm.course.id,
        date_start: this.dataForm.dateStart,
        date_end: this.dataForm.dateEnd,
        status_document: this.dataForm.status.id
      }
      if (checkAccess('backOffice')) body.is_only_dpd = this.dataForm.onlyForDPD

      this.$api.post(`api/v2/sailor/${this.id}/certificate/`, body).then(response => {
        this.buttonLoader = false
        if (response.code === 201) {
          this.$notification.success(this, this.$i18n.t('addedETI'))
          this.$store.commit('addDataSailor', { type: 'certification', value: response.data })
          this.$parent.viewAdd = false
          this.$store.commit('incrementBadgeCount', {
            child: 'certificateDocument',
            parent: 'certificateAll'
          })

          this.$store.dispatch('getQualificationStatements', this.id)
          this.$store.dispatch('getSQCStatements', this.id)
          this.$data.dataForm = formFieldsInitialState()
          this.$v.$reset()
        }
      })
    }
  }
}
