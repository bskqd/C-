import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import { hideDetailed } from '@/mixins/main'
import { required, numeric, helpers, minValue, maxValue } from 'vuelidate/lib/validators'
import { mapState } from 'vuex'

const alphaUA = helpers.regex('alpha', /^[а-щА-ЩЬьЮюЯяЇїІіЄєҐґ'.\-\s]*$/)
const alphaEN = helpers.regex('alpha', /^[a-zA-Z'.\-\s]*$/)

export default {
  name: 'SailorRecordBookEdit',
  props: {
    sailorDocument: Object
  },
  components: {
    ValidationAlert,
    FileDropZone
  },
  data () {
    return {
      number: this.sailorDocument.number,
      dateIssued: this.sailorDocument.date_issued,
      agentNameUkr: this.sailorDocument.auth_agent_ukr,
      agentNameEng: this.sailorDocument.auth_agent_eng,
      branchOffice: this.sailorDocument.branch_office,
      waybillNumber: this.sailorDocument.waibill_number,
      strictBlank: this.sailorDocument.blank_strict_report,
      buttonLoader: false,
      hideDetailed
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      lang: state => state.main.lang,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      // mapping documents
      mappingAffiliate: state => state.directory.affiliate
    }),
    dateIssueObject () {
      return this.dateIssued ? new Date(this.dateIssued) : null
    }
  },
  validations () {
    return {
      number: { required, numeric },
      agentNameUkr: { required, alphaUA },
      agentNameEng: { required, alphaEN },
      dateIssueObject: {
        required,
        minValue: minValue(new Date('1900-01-01')),
        maxValue: maxValue(new Date())
      }
    }
  },
  methods: {
    /** Record book edited fields validation */
    checkSaveEditRecord () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.saveEditRecord()
    },

    /** Save edited record info */
    saveEditRecord () {
      this.buttonLoader = true
      const body = {
        number: this.number,
        date_issued: this.dateIssued,
        branch_office: this.branchOffice.id,
        auth_agent_ukr: this.agentNameUkr,
        auth_agent_eng: this.agentNameEng,
        blank_strict_report: this.strictBlank,
        waibill_number: this.waybillNumber
      }
      this.$api.patch(`api/v2/sailor/${this.id}/service_record/${this.sailorDocument.id}/`, body).then(response => {
        this.buttonLoader = false
        if (response.status === 'success') {
          const files = this.$refs.mediaContent.filesArray
          if (files.length) {
            this.$api.postPhoto(files, 'RecordBookDoc', response.data.id).then((response) => {
              if (response.status !== 'created' && response.status !== 'success') {
                this.$notification.error(this, this.$i18n.t('errorAddFile'))
              }
            })
          }
          this.$notification.success(this, this.$i18n.t('editInfoRecordBook'))
          this.$store.commit('updateDataSailor', { type: 'serviceRecordBook', value: response.data })
        }
      })
    }
  }
}
