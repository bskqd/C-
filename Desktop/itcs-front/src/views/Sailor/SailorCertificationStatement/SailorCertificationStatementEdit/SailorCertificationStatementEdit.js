import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { mapState } from 'vuex'
import { maxValue, minValue, required } from 'vuelidate/lib/validators'

export default {
  name: 'SeafarerCertApplicationEdit',
  props: {
    sailorDocument: Object
  },
  components: {
    ValidationAlert
  },
  data () {
    return {
      city: null,
      dateMeeting: this.sailorDocument.date_meeting,
      eti: this.sailorDocument.institution,
      buttonLoader: false,
      certApplicationInstitution: [],
      institutionsCity: [
        'Чорноморськ',
        'Одеса',
        'Миколаїв',
        'Херсон',
        'Маріуполь',
        'Ізмаїл'
      ]
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      lang: state => state.main.lang,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      // mapping documents
      filteredInstitutionsList: state => state.directory.filteredETI
    }),
    dateMeetingObject () {
      return this.dateMeeting ? new Date(this.dateMeeting) : null
    }
  },
  validations: {
    eti: { required },
    city: { required },
    dateMeetingObject: {
      required,
      minValue: minValue(new Date('1900-01-01')),
      maxValue: maxValue(new Date('2200-01-01'))
    }
  },
  methods: {
    /** Custom label for getting embedded ETI name */
    customLabelView (label) {
      if (label.ntz) {
        return label.ntz[this.labelName]
      } else {
        return label[this.labelName]
      }
    },

    /** Check field entries for validation */
    checkEditedRecord () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.editCertApplication()
    },

    /** Edit certificating application */
    editCertApplication () {
      this.buttonLoader = true
      const body = {
        date_meeting: this.dateMeeting
      }

      if (this.eti.ntz) {
        body.institution = this.eti.ntz.id
      } else body.institution = this.eti.id

      this.$api.patch(`api/v2/sailor/${this.id}/statement/certificate/${this.sailorDocument.id}/`, body).then(response => {
        this.buttonLoader = false
        if (response.status === 'success') {
          this.$notification.success(this, this.$i18n.t('etiStatementEdited'))
          this.$store.commit('clearFilteredEtiList')
          this.$store.commit('updateDataSailor', { type: 'certificationStatement', value: response.data })
        }
      })
    },

    /** Mapping available ETI for adding application by city and course */
    mappingCertApplicationInstitution () {
      if (this.city) {
        const searchQueries = {
          course: this.sailorDocument.course,
          city: this.city,
          arrayIndex: 0,
          labelName: this.labelName
        }
        this.$store.dispatch('getFilteredETI', searchQueries).then(() => {
          this.eti = this.filteredInstitutionsList[0][0]
        })
      }
    }
  }
}
