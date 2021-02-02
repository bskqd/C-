import { mapState } from 'vuex'
import { helpers } from 'vuelidate/lib/validators'
import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { getDateFormat, setSearchDelay } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'

const regexpNumber = helpers.regex('alpha', /^[\d]{5}\/[\d]{4}/)

const initialData = () => {
  return {
    periodStart: null,
    periodEnd: null,
    numberProtocol: null,
    affiliate: null,
    statementAffiliate: null,
    numberStatement: null,
    fullName: null,
    dateBorn: null,
    dateNow: null,
    rank: null,
    position: null,
    solution: null,
    status: null,
    specialty: null,
    profession: null,
    experience: null,
    protocolAvailability: null,
    statementAvailability: null,
    resultEQC: null,
    educPassedExam: null,
    certificateNumber: null,
    certificateCourse: null,
    educationInstitution: null,
    dateIssue: null,
    dateTerminate: null,
    registrationNumber: null,
    serial: null,
    graduationNumber: null,
    educationExtent: null,
    institution: null,
    qualification: null,
    specialization: null,
    cadetFaculty: null,
    typeQualDoc: null,
    country: null,
    port: null,
    otherPort: null,
    number: null,
    isCadet: null,
    headCommissioner: null,
    memberCommissioner: null,
    accrualTypeDoc: null,
    sailorId: null,
    exactDate: null,
    firstFormParams: 'equal',
    firstFormSum: null,
    secondFormParams: 'equal',
    secondFormSum: null,
    dateMeetingFrom: null,
    dateMeetingTo: null,
    withoutDate: null,
    typeDoc: null,
    // way: null,
    protocolWay: null,
    agentFullName: null,
    dateEndProxy: null,
    dateEndProxyFrom: null,
    dateEndProxyTo: null,
    payment: null,
    distributionType: null,
    getDocumentStatus: null,
    periodStartReceipt: null,
    periodEndReceipt: null,
    meetingDateFrom: null,
    meetingDateTo: null,
    meetingDateEndFrom: null,
    meetingDateEndTo: null,
    user: null,
    sailor: null,
    qualificationLevel: null,
    newDocument: null,
    statementType: null,
    sailorsSearchList: []
  }
}

export default {
  name: 'ReportSearch',
  components: {
    ValidationAlert
  },
  props: {
    sqcProtocol: Boolean,
    sqcApplication: Boolean,
    etiCertificate: Boolean,
    qualDocDiploma: Boolean,
    qualDocCert: Boolean,
    qualDocument: Boolean,
    qualApplication: Boolean,
    graduationCert: Boolean,
    education: Boolean,
    medical: Boolean,
    seafarerPassport: Boolean,
    citizenPassport: Boolean,
    reportCadet: Boolean,
    finance: Boolean,
    agentStatements: Boolean,
    srbStatements: Boolean,
    statementETI: Boolean,
    etiPayments: Boolean,
    userHistory: Boolean,
    statementAdvanceTraining: Boolean,
    newAccounts: Boolean,
    sailorPassport: Boolean,
    report: String,
    getReport: Function,
    getExcel: Function
  },
  data () {
    return {
      viewSearch: true,
      allowSaveExcel: true,
      withProtocol: true,
      // viewPortString: false,
      checkAccess,
      setSearchDelay,

      params: null,
      delaySearch: null,

      dataForm: initialData(),
      resultSearchTitle: [],

      mappingBooleanOptions: [
        { id: 0, name: this.$i18n.t('yes'), value: true },
        { id: 1, name: this.$i18n.t('no'), value: false }
      ],
      mappingStatementTypes: [
        { id: 0, name: this.$i18n.t('continuing'), value: true },
        { id: 1, name: this.$i18n.t('creatingNew'), value: false }
      ],
      formParams: [
        { text: this.$i18n.t('equalSum'), value: 'equal' },
        { text: this.$i18n.t('moreOrEqual'), value: 'more' },
        { text: this.$i18n.t('lessOrEqual'), value: 'less' }
      ],
      mappingExperience: [
        { name_eng: 'None', name_ukr: 'Немає', value: false },
        { name_eng: 'Exist', name_ukr: 'Існує', value: true }
      ],
      mappingWay: [
        { name_eng: '-', name_ukr: 'С' },
        { name_eng: '-', name_ukr: 'М' },
        { name_eng: '-', name_ukr: 'РК' },
        { name_eng: '-', name_ukr: 'Р' },
        { name_eng: '-', name_ukr: 'Т' },
        { name_eng: '-', name_ukr: 'ПФ' }
      ],
      mappingSolution: [
        { value: 'assign', name: this.$i18n.t('assign') },
        { value: 'not_assign', name: this.$i18n.t('not_assign') },
        { value: 'confirm', name: this.$i18n.t('confirm') },
        { value: 'not_confirm', name: this.$i18n.t('not_confirm') },
        { value: 'give', name: this.$i18n.t('give') },
        { value: 'not_give', name: this.$i18n.t('not_give') }
      ],
      mappingProtocolAvailability: [
        { id: 1, name: this.$i18n.t('orProtocol'), value: null },
        { id: 2, name: this.$i18n.t('withProtocol'), value: true },
        { id: 3, name: this.$i18n.t('withoutProtocol'), value: false }
      ],
      mappingApplicationAvailability: [
        { id: 1, name: this.$i18n.t('orStatement'), value: null },
        { id: 2, name: this.$i18n.t('withStatement'), value: true },
        { id: 3, name: this.$i18n.t('withoutStatement'), value: false }
      ],
      mappingResultsEQC: [
        { id: 1, name: this.$i18n.t('orPassedEducationExam'), value: null },
        { id: 2, name: this.$i18n.t('passedEducationExam'), value: true },
        { id: 3, name: this.$i18n.t('noPassedEducationExam'), value: false }
      ],
      mappingEducExamPass: [
        { id: 1, name: this.$i18n.t('orEducationWithSQC'), value: null },
        { id: 2, name: this.$i18n.t('educationWithSQC'), value: true },
        { id: 3, name: this.$i18n.t('noEducationWithSQC'), value: false }
      ],
      mappingCadetType: [
        { id: 1, name: this.$i18n.t('orCadet'), value: null },
        { id: 2, name: this.$i18n.t('cadet'), value: true },
        { id: 3, name: this.$i18n.t('notCadet'), value: false }
      ],
      mappingDistributionType: [
        { id: 0, name: this.$i18n.t('sqcWithExp'), value: 'sqc', experience: true },
        { id: 1, name: this.$i18n.t('sqcWithoutExp'), value: 'sqc', experience: false },
        { id: 2, name: this.$i18n.t('sqcCadet'), value: 'sqc', cadet: true },
        { id: 3, name: this.$i18n.t('medicalInstitution'), value: 'medical' },
        { id: 4, name: this.$i18n.t('eti'), value: 'eti' },
        { id: 5, name: this.$i18n.t('diplomasQualification'), value: 'dpd' },
        { id: 6, name: this.$i18n.t('portal'), value: 'portal' },
        { id: 7, name: this.$i18n.t('agents'), value: 'seaman', cadet: false },
        { id: 8, name: this.$i18n.t('agentCadet'), value: 'seaman', cadet: true },
        { id: 9, name: this.$i18n.t('serviceCenter'), value: 'sc' },
        { id: 10, name: this.$i18n.t('advanceTrainingCourse'), value: 'adv_training' }
      ],
      listGetDocumentStatus: [
        { id: 0, name: this.$i18n.t('allDocs'), value: 'true,false' },
        { id: 1, name: this.$i18n.t('got'), value: true },
        { id: 2, name: this.$i18n.t('notGot'), value: false }
      ]
    }
  },
  validations: {
    dataForm: {
      numberProtocol: { regexpNumber },
      numberStatement: { regexpNumber }
    }
  },
  computed: {
    ...mapState({
      lang: state => state.main.lang,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      labelValue: state => (state.main.lang === 'en') ? 'value_eng' : 'value',
      label: state => (state.main.lang === 'en') ? 'name_en' : 'name',
      userId: state => state.main.user.id,
      // mapping documents
      mappingRank: state => state.directory.ranks,
      mappingCourses: state => state.directory.courses,
      mappingTrainingPlace: state => state.directory.educationTraining,
      mappingTypeDoc: state => state.directory.typeDoc,
      mappingExtent: state => state.directory.extent,
      mappingInstitution: state => state.directory.institution,
      mappingSpecialization: state => state.directory.specialization,
      mappingProfession: state => state.directory.profession,
      mappingQualification: state => state.directory.qualificationLevels,
      mappingFaculties: state => state.directory.faculties,
      mappingTypeDocQualification: state => state.directory.typeDocQualification,
      mappingCountry: state => state.directory.country,
      mappingPorts: state => state.directory.ports,
      affiliateAll: state => state.directory.affiliate,
      allCommissioners: state => state.directory.allCommissioners,
      allAccrualTypeDoc: state => state.directory.allAccrualTypeDoc,
      paymentStatus: state => state.directory.paymentStatus,
      usersList: state => state.directory.userList,
      // permissions
      permissionsReport: state => state.main.permissionsReport
    }),
    viewPortSelect () {
      return !this.dataForm.country || (this.dataForm.country && !this.dataForm.country.length) ||
        (this.dataForm.country && this.dataForm.country.length && this.dataForm.country.find(value => value.id === 2))
    },
    mappingQualificationLevels () {
      return this.$store.getters.qualificationById(2)
    },
    mappingStatuses () {
      // assembled array of statuses for back office
      let assembledStatusesArr = []
      const backOfficeStatusServices = ['Other', 'PacketDelete', 'BackOffice']
      assembledStatusesArr = backOfficeStatusServices.reduce((result, service) => {
        result = result.concat(this.$store.getters.statusChoose(service))
        return result
      }, [])

      let statusesArray = []
      switch (this.report) {
        case 'educationReport':
        case 'diplomasQualification':
          statusesArray = this.$store.getters.statusChoose(this.report === 'educationReport' ? 'ServiceRecord' : 'QualificationDoc')
          if (checkAccess('backOffice')) statusesArray = statusesArray.concat(assembledStatusesArr) // concat statuses for back office
          if (this.userId === 106 || this.userId === 107) statusesArray.push(this.$store.getters.statusById(34)) // add verification status for 2 users
          return statusesArray
        case 'statementETI':
          statusesArray = this.$store.getters.statusChoose('StatementETI')
          statusesArray.push(this.$store.getters.statusById(84))
          return statusesArray
        case 'agentStatements':
          statusesArray = this.$store.getters.statusChoose('StatementAgentSailor')
          return statusesArray
        case 'srbStatements':
          statusesArray = this.$store.getters.statusChoose('StatementServRecord').filter(status => status.id !== 47)
          statusesArray.push(this.$store.getters.statusById(42))
          return statusesArray
        case 'statementAdvanceTraining':
          statusesArray = this.$store.getters.statusChoose('StatementAdvancedTraining')
          return statusesArray
        case 'sailorPassportReport':
          statusesArray = this.$store.getters.statusChoose('QualificationDoc')
          return statusesArray
        default:
          statusesArray = this.$store.getters.statusChoose('StatementDKK&Qual')
          if (checkAccess('backOffice')) statusesArray = statusesArray.concat(assembledStatusesArr) // concat statuses for back office
          if (!statusesArray.find(status => status.id === 42)) statusesArray.push(this.$store.getters.statusById(42)) // add status "created from PA"
          return statusesArray
      }
    },
    mappingAffiliate () {
      switch (this.report) {
        case 'protocolSQC':
          if (this.permissionsReport && this.permissionsReport.length) {
            const branches = []
            const branchIds = this.permissionsReport.filter(value => value.permission === 'reportSqcProtocol')
            branchIds[0].branch_office.forEach(branchId => {
              branches.push(this.$store.getters.affiliateById(branchId))
            })
            return branches
          } else return []
        case 'statementSQC':
          return this.affiliateAll
      }
    }
  },
  watch: {
    report () {
      this.dataForm = initialData()
      this.resultSearchTitle = []
    }
  },
  methods: {
    changeRank (rank) {
      this.allowSaveExcel = true
      let selectedPositions = []
      if (this.position) {
        selectedPositions = this.position.filter(val => {
          for (let r of rank) {
            if (val.rank === r.id) {
              return val
            }
          }
        })
      }
      this.position = selectedPositions
    },

    mappingPosition (rank) {
      if (rank) {
        let positions = []
        for (let r of rank) {
          positions = positions.concat(this.$store.getters.noSortedPositionsById(r.id))
        }
        return positions
        // return rank.map(item => {
        //   return this.$store.getters.noSortedPositionsById(item.id)
        // })
      } else return []
    },

    // checkCountry (country) {
    //   this.allowSaveExcel = true
    //   this.viewPortString = country.id !== 2
    // },

    setParams (type) {
      this.resultSearchTitle = []
      this.params = new URLSearchParams({
        page_size: 20
      })

      if (this.dataForm.periodStart) {
        if (this.newAccounts || this.userHistory) this.params.set('date_from', this.dataForm.periodStart)
        if (this.srbStatements || this.statementETI || this.statementAdvanceTraining ||
          this.sailorPassport) this.params.set('from_date', this.dataForm.periodStart)
        if (this.etiPayments) this.params.set('from_pay_date', this.dataForm.periodStart)
        if (this.sqcProtocol || this.sqcApplication || this.education || this.qualDocument ||
          this.etiCertificate) this.params.set('from_date', this.dataForm.periodStart)
        if (this.agentStatements) this.params.set('date_create_from', this.dataForm.periodStart)
        if (this.finance) this.params.set('payment_date_from', this.dataForm.periodStart)
        if (this.report === 'debtor' || this.report === 'distribution') {
          this.params.set('created_from_date', this.dataForm.periodStart)
          this.params.set('payment_from_date', this.dataForm.periodStart)
        }
        this.resultSearchTitle.push(`${this.$i18n.t('periodStart')}: ${this.dataForm.periodStart}`)
      }
      if (this.dataForm.periodEnd) {
        if (this.newAccounts || this.userHistory) this.params.set('date_to', this.dataForm.periodEnd)
        if (this.srbStatements || this.statementETI || this.statementAdvanceTraining ||
          this.sailorPassport) this.params.set('to_date', this.dataForm.periodEnd)
        if (this.etiPayments) this.params.set('to_pay_date', this.dataForm.periodEnd)
        if (this.sqcProtocol || this.sqcApplication || this.education || this.qualDocument ||
          this.etiCertificate) this.params.set('to_date', this.dataForm.periodEnd)
        if (this.agentStatements) this.params.set('date_create_to', this.dataForm.periodEnd)
        if (this.finance) this.params.set('payment_date_to', this.dataForm.periodEnd)
        if (this.report === 'debtor' || this.report === 'distribution') {
          this.params.set('created_to_date', this.dataForm.periodEnd)
          this.params.set('payment_to_date', this.dataForm.periodEnd)
        }
        this.resultSearchTitle.push(`${this.$i18n.t('periodEnd')}: ${this.dataForm.periodEnd}`)
      }
      if (this.dataForm.fullName) {
        this.params.set('sailor_name', this.dataForm.fullName)
        this.resultSearchTitle.push(`${this.$i18n.t('sailor')}: ${this.dataForm.fullName}`)
      }
      if (this.dataForm.agentFullName) {
        this.params.set('agent_name', this.dataForm.agentFullName)
        this.resultSearchTitle.push(`${this.$i18n.t('agentFullName')}: ${this.dataForm.agentFullName}`)
      }
      if (this.dataForm.dateBorn) {
        this.params.set('sailor_birth', this.dataForm.dateBorn)
        this.resultSearchTitle.push(`${this.$i18n.t('dateBorn')}: ${this.dataForm.dateBorn}`)
      }
      if (this.dataForm.dateEndProxy) {
        this.params.set('date_end_proxy', this.dataForm.dateEndProxy)
        this.resultSearchTitle.push(`${this.$i18n.t('contractDateEnd')}: ${this.dataForm.dateEndProxy}`)
      }
      if (this.dataForm.dateEndProxyFrom) {
        this.params.set('date_end_proxy_from', this.dataForm.dateEndProxyFrom)
        this.resultSearchTitle.push(`${this.$i18n.t('periodStart')}: ${this.dataForm.dateEndProxyFrom}`)
      }
      if (this.dataForm.dateEndProxyTo) {
        this.params.set('date_end_proxy_to', this.dataForm.dateEndProxyTo)
        this.resultSearchTitle.push(`${this.$i18n.t('periodEnd')}: ${this.dataForm.dateEndProxyTo}`)
      }
      if ((this.dataForm.numberProtocol && this.report === 'protocolSQC') ||
        (this.dataForm.numberProtocol && this.report === 'statementSQC' &&
          this.dataForm.protocolAvailability.value !== false)) {
        this.params.set('protocol_number', this.dataForm.numberProtocol.split('/')[0])
        this.params.set('protocol_year', this.dataForm.numberProtocol.split('/')[1])
        this.resultSearchTitle.push(`${this.$i18n.t('numberProtocol')}/${this.$i18n.t('year')}: ${this.dataForm.numberProtocol}`)
      }
      if (this.dataForm.affiliate && ((this.dataForm.affiliate.length && this.report === 'protocolSQC') ||
        (this.dataForm.affiliate.length && this.report === 'statementSQC' && this.dataForm.protocolAvailability.value !== false))) {
        // let affiliate = this.dataForm.affiliate.map(value => value.id)
        let affiliateID = []
        let affiliateName = []
        this.dataForm.affiliate.map(value => {
          affiliateID.push(value.id)
          affiliateName.push(value[this.labelName])
        })
        this.params.set('branch', affiliateID.join(', '))
        this.resultSearchTitle.push(`${this.$i18n.t('affiliate')}: ${affiliateName.join(', ')}`)
      }
      if ((this.dataForm.protocolAvailability && this.dataForm.protocolAvailability.value !== null &&
      this.report === 'statementSQC') ||
        (this.dataForm.protocolAvailability && this.dataForm.protocolAvailability.value !== null &&
        this.dataForm.statementAvailability && this.dataForm.statementAvailability.id === 2)) {
        this.params.set('have_protocol', this.dataForm.protocolAvailability.value)
        this.resultSearchTitle.push(`${this.$i18n.t('statementType')}: ${this.dataForm.protocolAvailability.name}`)
      }
      if (this.dataForm.statementAvailability && this.dataForm.statementAvailability.value !== null) {
        this.params.set('have_statement', this.dataForm.statementAvailability.value)
        this.resultSearchTitle.push(`${this.$i18n.t('statementAvailability')}: ${this.dataForm.statementAvailability.name}`)
      }
      if (this.dataForm.specialty && this.dataForm.specialty.length && this.report === 'statementSQC') {
        let specialty = this.dataForm.specialty.map(value => value.name_ukr)
        this.params.set('direction_abbr', specialty.join(', '))
        this.resultSearchTitle.push(`${this.$i18n.t('specialty')}: ${specialty.join(', ')}`)
      }
      if (this.dataForm.protocolWay && this.dataForm.protocolWay.length) {
        let way = this.dataForm.protocolWay.map(value => value.name_ukr)
        this.params.set('direction_abbr', way.join(', '))
        this.resultSearchTitle.push(`${this.$i18n.t('way')}: ${way.join(', ')}`)
      }
      if (this.dataForm.status && this.dataForm.status.length) {
        let statusID = []
        let statusName = []
        this.dataForm.status.map(value => {
          statusID.push(value.id)
          statusName.push(value[this.labelName])
        })
        this.params.set('status_document', statusID.join(', '))
        this.resultSearchTitle.push(`${this.$i18n.t('status')}: ${statusName.join(', ')}`)
      }
      if (this.dataForm.solution && this.report === 'protocolSQC') {
        let solutionID = []
        let solutionName = []
        this.dataForm.solution.map(value => {
          solutionID.push(value.value)
          solutionName.push(value.name)
        })
        this.params.set('document_property', solutionID.join(','))
        this.resultSearchTitle.push(`${this.$i18n.t('solution')}: ${solutionName.join(', ')}`)
      }
      if (this.dataForm.rank && this.dataForm.rank.length) {
        let rankID = []
        let rankName = []
        this.dataForm.rank.map(value => {
          rankID.push(value.id)
          rankName.push(value[this.labelName])
        })
        this.params.set('rank', rankID.join(', '))
        this.resultSearchTitle.push(`${this.$i18n.t('rank')}: ${rankName.join(', ')}`)
      }
      if (this.dataForm.position && this.dataForm.position.length) {
        let positionID = []
        let positionName = []
        this.dataForm.position.map(value => {
          positionID.push(value.id)
          positionName.push(value[this.labelName])
        })
        this.params.set('position', positionID.join(', '))
        this.resultSearchTitle.push(`${this.$i18n.t('position')}: ${positionName.join(', ')}`)
      }
      if (this.dataForm.numberStatement) {
        this.params.set('statement_number', this.dataForm.numberStatement.split('/')[0])
        this.params.set('statement_year', this.dataForm.numberStatement.split('/')[1])
        this.resultSearchTitle.push(`${this.$i18n.t('numberApplication')}/${this.$i18n.t('year')}: ${this.dataForm.numberStatement}`)
      }
      if (this.dataForm.statementAffiliate && this.dataForm.statementAffiliate.length) {
        let statementAffiliate = this.dataForm.statementAffiliate.map(value => {
          return value.id
        })
        this.params.set('branch', statementAffiliate.join(', '))
        this.resultSearchTitle.push(`${this.$i18n.t('affiliate')}: ${statementAffiliate.join(', ')}`)
      }
      if (this.dataForm.experience && this.dataForm.experience.length) {
        let experienceID = []
        let experienceName = []
        this.dataForm.experience.map(value => {
          experienceID.push(value.value)
          experienceName.push(value[this.labelName])
        })
        this.params.set('experience_required', experienceID.join(', '))
        this.resultSearchTitle.push(`${this.$i18n.t('requirementExperience')}: ${experienceName.join(', ')}`)
      }
      if (this.dataForm.isCadet && this.dataForm.isCadet.value !== null) {
        this.params.set('is_cadet', this.dataForm.isCadet.value)
        this.resultSearchTitle.push(`${this.dataForm.isCadet.name}`)
      }
      if (this.dataForm.headCommissioner && this.dataForm.headCommissioner.length && this.report === 'protocolSQC') {
        // let headCommissioners = this.dataForm.headCommissioner.map(value => {
        //   return value
        // })
        let headCommissionersID = []
        let headCommissionersName = []
        this.dataForm.headCommissioner.map(value => {
          headCommissionersID.push(value.value)
          headCommissionersName.push(value.fullName)
        })
        this.params.set('committe_head', headCommissionersID.join(', '))
        this.resultSearchTitle.push(`${this.$i18n.t('headCommission')}: ${headCommissionersName.join(', ')}`)
      }
      if (this.dataForm.memberCommissioner && this.dataForm.memberCommissioner.length && this.report === 'protocolSQC') {
        // let memberCommissioner = this.dataForm.memberCommissioner.map(value => {
        //   return value
        // })
        let memberCommissionerID = []
        let memberCommissionerName = []
        this.dataForm.memberCommissioner.map(value => {
          memberCommissionerID.push(value.value)
          memberCommissionerName.push(value.fullName)
        })
        this.params.set('commissioner', memberCommissionerID.join(', '))
        this.resultSearchTitle.push(`${this.$i18n.t('membersCommission')}: ${memberCommissionerName.join(', ')}`)
      }
      if (this.dataForm.dateMeetingFrom && this.report === 'statementSQC') {
        this.params.set('from_date_meeting', this.dataForm.dateMeetingFrom)
        this.resultSearchTitle.push(`${this.$i18n.t('dateEventFrom')}: ${this.dataForm.dateMeetingFrom}`)
      }
      if (this.dataForm.dateMeetingTo && this.report === 'statementSQC') {
        this.params.set('to_date_meeting', this.dataForm.dateMeetingTo)
        this.resultSearchTitle.push(`${this.$i18n.t('dateEventTo')}: ${this.dataForm.dateMeetingTo}`)
      }
      if (this.dataForm.withoutDate && (this.report === 'statementSQC' || this.report === 'protocolSQC' || this.sailorPassport)) {
        this.params.set('with_agent', this.dataForm.withoutDate.value)
        this.resultSearchTitle.push(`${this.$i18n.t('agentsDocument')}: ${this.dataForm.withoutDate.name}`)
      }
      if (this.dataForm.resultEQC && this.dataForm.resultEQC.value !== null) {
        this.params.set('passed_educ_exam', this.dataForm.resultEQC.value)
        this.resultSearchTitle.push(`${this.$i18n.t('resultEKK')}: ${this.dataForm.resultEQC.name}`)
      }
      if (this.dataForm.educPassedExam && this.dataForm.educPassedExam.value !== null) {
        this.params.set('educ_with_dkk', this.dataForm.educPassedExam.value)
        this.resultSearchTitle.push(`${this.$i18n.t('decisionEKK')}: ${this.dataForm.educPassedExam.name}`)
      }
      if (this.dataForm.institution && this.dataForm.institution.length) {
        let institutionID = []
        let institutionName = []

        this.dataForm.institution.map(value => {
          institutionID.push(value.id)
          institutionName.push(value[this.labelName])
        })
        if (this.statementAdvanceTraining) {
          this.params.set('education_institution', institutionID.join(', '))
        } else {
          this.params.set('id_nz', institutionID.join(', '))
        }
        this.resultSearchTitle.push(`${this.$i18n.t('nameInstitution')}: ${institutionName.join(', ')}`)
      }
      if (this.dataForm.cadetFaculty && this.dataForm.cadetFaculty.length) {
        let facultyID = []
        let facultyName = []

        this.dataForm.cadetFaculty.map(value => {
          facultyID.push(value.id)
          facultyName.push(value[this.labelName])
        })
        this.params.set('faculty', facultyID.join(', '))
        this.resultSearchTitle.push(`${this.$i18n.t('way')}: ${facultyName.join(', ')}`)
      }
      if (this.dataForm.typeDoc) {
        this.params.set('type_document', this.dataForm.typeDoc.id)
        this.resultSearchTitle.push(`${this.$i18n.t('typeDoc')}: ${this.dataForm.typeDoc[this.langFields]}`)
      }
      if (this.dataForm.registrationNumber) {
        this.params.set('registry_number', this.dataForm.registrationNumber)
        this.resultSearchTitle.push(`${this.$i18n.t('registrationNumber')}: ${this.dataForm.registrationNumber}`)
      }
      if (this.dataForm.serial) {
        this.params.set('serial', this.dataForm.serial)
        this.resultSearchTitle.push(`${this.$i18n.t('serial')}: ${this.dataForm.serial}`)
      }
      if (this.dataForm.graduationNumber) {
        this.params.set('number_document', this.dataForm.graduationNumber)
        this.resultSearchTitle.push(`${this.$i18n.t('number')}: ${this.dataForm.graduationNumber}`)
      }
      if (this.dataForm.educationExtent && this.dataForm.educationExtent.length) {
        let extentsID = []
        let extentsName = []
        this.dataForm.educationExtent.map(value => {
          extentsID.push(value.id)
          extentsName.push(value[this.labelName])
        })
        this.params.set('extent', extentsID.join(', '))
        this.resultSearchTitle.push(`${this.$i18n.t('educationExtent')}: ${extentsName.join(', ')}`)
      }
      if (this.dataForm.qualification && this.dataForm.qualification.length) {
        let qualificationID = []
        let qualificationName = []
        this.dataForm.qualification.map(value => {
          qualificationID.push(value.id)
          qualificationName.push(value[this.labelName])
        })
        this.params.set('qualification', qualificationID.join(', '))
        this.resultSearchTitle.push(`${this.$i18n.t('qualification')}: ${qualificationName.join(', ')}`)
      }
      if (this.dataForm.qualificationLevel && this.dataForm.qualificationLevel.length) {
        let qualificationID = []
        let qualificationName = []
        this.dataForm.qualificationLevel.map(value => {
          qualificationID.push(value.id)
          qualificationName.push(value[this.labelName])
        })
        this.params.set('level_qualification', qualificationID.join(', '))
        this.resultSearchTitle.push(`${this.$i18n.t('qualification')}: ${qualificationName.join(', ')}`)
      }
      if (this.dataForm.specialty && this.dataForm.specialty.length && this.report !== 'statementSQC') {
        let specialtyID = []
        let specialtyName = []
        this.dataForm.specialty.map(value => {
          specialtyID.push(value.id)
          specialtyName.push(value[this.labelName])
        })
        this.params.set('speciality', specialtyID.join(', '))
        this.resultSearchTitle.push(`${this.$i18n.t('specialty')}: ${specialtyName.join(', ')}`)
      }
      if (this.dataForm.specialization && this.dataForm.specialization.length) {
        let specializationID = []
        let specializationName = []
        this.dataForm.specialization.map(value => {
          specializationID.push(value.id)
          specializationName.push(value[this.labelName])
        })
        this.params.set('specialization', specializationID.join(', '))
        this.resultSearchTitle.push(`${this.$i18n.t('specialization')}: ${specializationName.join(', ')}`)
      }
      if (this.dataForm.dateIssue) {
        this.params.set('date_issue_document', this.dataForm.dateIssue)
        this.resultSearchTitle.push(`${this.$i18n.t('dateIssue')}: ${this.dataForm.dateIssue}`)
      }
      if (this.dataForm.dateTerminate) {
        this.params.set('experied_date', this.dataForm.dateTerminate)
        this.params.set('date_end', this.dataForm.dateTerminate)
        this.resultSearchTitle.push(`${this.$i18n.t('dateTermination')}: ${this.dataForm.dateTerminate}`)
      }
      if (this.dataForm.number) {
        this.params.set('number', this.dataForm.number)
        if (this.dataForm.number.split('/')[1]) {
          this.params.set('number_document', this.dataForm.number.split('/')[0])
          this.params.set('document_year', this.dataForm.number.split('/')[1])
        } else {
          this.params.set('other_number', this.dataForm.number.split('/')[0])
        }
        this.resultSearchTitle.push(`${this.$i18n.t('number')}: ${this.dataForm.number}`)
      }
      if (this.dataForm.typeQualDoc) {
        this.params.set('type_document', this.dataForm.typeQualDoc.id)
        this.resultSearchTitle.push(`${this.$i18n.t('typeDoc')}: ${this.dataForm.typeQualDoc.name_ukr}`)
      }
      if (this.dataForm.country && this.dataForm.country.length) {
        let countryID = []
        let countryName = []
        this.dataForm.country.map(value => {
          countryID.push(value.id)
          countryName.push(value[this.labelValue])
        })
        this.params.set('country', countryID.join(', '))
        this.resultSearchTitle.push(`${this.$i18n.t('country')}: ${countryName.join(', ')}`)
      }
      if (this.dataForm.port && this.dataForm.port.length && !this.dataForm.otherPort) {
        let portID = []
        let portName = []
        this.dataForm.port.map(value => {
          portID.push(value.id)
          portName.push(value[this.labelName])
        })
        this.params.set('port', portID.join(', '))
        this.resultSearchTitle.push(`${this.$i18n.t('port')}: ${portName.join(', ')}`)
      }
      if (this.dataForm.otherPort && (!this.dataForm.port || (this.dataForm.port && !this.dataForm.port.length))) {
        this.params.set('other_port', this.dataForm.otherPort)
        this.resultSearchTitle.push(`${this.$i18n.t('port')}: ${this.dataForm.otherPort}`)
      }
      if (this.dataForm.certificateNumber) {
        this.params.set('number', this.dataForm.certificateNumber)
        this.resultSearchTitle.push(`${this.$i18n.t('number')}: ${this.dataForm.certificateNumber}`)
      }
      if (this.dataForm.certificateCourse && this.dataForm.certificateCourse.length) {
        let courseID = []
        let courseName = []
        this.dataForm.certificateCourse.map(value => {
          courseID.push(value.id)
          courseName.push(value[this.labelName])
        })
        if (this.report === 'statementETI' || this.report === 'etiPayments') {
          this.params.set('course', courseID.join(', '))
        } else {
          this.params.set('course_traning', courseID.join(', '))
        }
        this.resultSearchTitle.push(`${this.$i18n.t('course')}: ${courseName.join(', ')}`)
      }
      if (this.dataForm.educationInstitution && this.dataForm.educationInstitution.length) {
        let institutionID = []
        let institutionName = []
        this.dataForm.educationInstitution.map(value => {
          institutionID.push(value.id)
          institutionName.push(value[this.labelName])
        })
        this.params.set('institution', institutionID.join(', '))
        this.resultSearchTitle.push(`${this.$i18n.t('nameInstitution')}: ${institutionName.join(', ')}`)
      }
      if (this.dataForm.exactDate) {
        this.params.set('payment_date_eq', this.dataForm.exactDate)
        this.params.set('date_create', this.dataForm.exactDate)
        this.resultSearchTitle.push(`${this.$i18n.t('exactDate')}: ${getDateFormat(this.dataForm.exactDate)}`)
      }
      if (this.dataForm.payment) {
        this.params.set('is_payed', this.dataForm.payment.status)
        this.resultSearchTitle.push(`${this.$i18n.t('payment')}: ${this.dataForm.payment.status ? this.$i18n.t('isPayed') : this.$i18n.t('notPayed')}`)
      }
      if (this.dataForm.accrualTypeDoc && this.dataForm.accrualTypeDoc.length) {
        let typeDocumentID = []
        let typeDocumentName = []
        this.dataForm.accrualTypeDoc.map(value => {
          typeDocumentID.push(value.id)
          typeDocumentName.push(value.value)
        })
        this.params.set('type_document', typeDocumentID.join(', '))
        this.resultSearchTitle.push(`${this.$i18n.t('typeDoc')}: ${typeDocumentName.join(', ')}`)
      }
      if (this.dataForm.sailorId) {
        this.params.set('sailor_id', this.dataForm.sailorId)
        this.params.set('sailor_key', this.dataForm.sailorId)
        this.resultSearchTitle.push(`${this.$i18n.t('sailorId')}: ${this.dataForm.sailorId}`)
      }
      if (this.dataForm.firstFormSum) {
        switch (this.dataForm.firstFormParams) {
          case 'equal':
            this.params.set('price_f1_eq', this.dataForm.firstFormSum)
            break
          case 'more':
            this.params.set('price_f1_gte', this.dataForm.firstFormSum)
            break
          case 'less':
            this.params.set('price_f1_lte', this.dataForm.firstFormSum)
            break
        }
        this.resultSearchTitle.push(`${this.$i18n.t('price')} ${this.$i18n.t('firstForm')}: ${this.dataForm.firstFormSum}`)
      }
      if (this.dataForm.secondFormSum) {
        switch (this.dataForm.secondFormParams) {
          case 'equal':
            this.params.set('price_f1_eq', this.dataForm.secondFormSum)
            break
          case 'more':
            this.params.set('price_f1_gte', this.dataForm.secondFormSum)
            break
          case 'less':
            this.params.set('price_f1_lte', this.dataForm.secondFormSum)
            break
        }
        this.resultSearchTitle.push(`${this.$i18n.t('price')} ${this.$i18n.t('secondForm')}: ${this.dataForm.secondFormSum}`)
      }
      if (this.dataForm.periodStartReceipt) {
        this.params.set('receipt_from_date', this.dataForm.periodStartReceipt)
        this.resultSearchTitle.push(`${this.$i18n.t('periodStartReceipt')}: ${this.dataForm.periodStartReceipt}`)
      }
      if (this.dataForm.periodEndReceipt) {
        this.params.set('receipt_to_date', this.dataForm.periodEndReceipt)
        this.resultSearchTitle.push(`${this.$i18n.t('periodEndReceipt')}: ${this.dataForm.periodEndReceipt}`)
      }
      if (this.dataForm.getDocumentStatus) {
        this.params.set('item_status', this.dataForm.getDocumentStatus.value)
        this.resultSearchTitle.push(`${this.$i18n.t('getDocStatus')}: ${this.dataForm.getDocumentStatus.name}`)
      }
      if (this.dataForm.distributionType) {
        if (this.dataForm.distributionType.hasOwnProperty('experience')) {
          this.params.set(`with_exp`, this.dataForm.distributionType.experience)
        }
        if (this.dataForm.distributionType.hasOwnProperty('cadet')) {
          this.params.set(`is_cadet`, this.dataForm.distributionType.cadet)
        }
        this.resultSearchTitle.push(`${this.$i18n.t('type')}: ${this.dataForm.distributionType.name}`)
      }
      if (this.dataForm.meetingDateFrom) {
        this.params.set('from_date_meeting', this.dataForm.meetingDateFrom)
        this.resultSearchTitle.push(`${this.$i18n.t('dateStartEduFrom')}: ${this.dataForm.meetingDateFrom}`)
      }
      if (this.dataForm.meetingDateTo) {
        this.params.set('to_date_meeting', this.dataForm.meetingDateTo)
        this.resultSearchTitle.push(`${this.$i18n.t('dateStartEduTo')}: ${this.dataForm.meetingDateTo}`)
      }
      if (this.dataForm.meetingDateEndFrom) {
        this.params.set('from_date_end_meeting', this.dataForm.meetingDateEndFrom)
        this.resultSearchTitle.push(`${this.$i18n.t('dateEndEduFrom')}: ${this.dataForm.meetingDateEndFrom}`)
      }
      if (this.dataForm.meetingDateEndTo) {
        this.params.set('to_date_end_meeting', this.dataForm.meetingDateEndTo)
        this.resultSearchTitle.push(`${this.$i18n.t('dateEndEduTo')}: ${this.dataForm.meetingDateEndTo}`)
      }
      if (this.dataForm.user) {
        this.params.set('user', this.dataForm.user.id)
        this.resultSearchTitle.push(`${this.$i18n.t('user')}: ${this.dataForm.user.userFullName}`)
      }
      if (this.dataForm.sailor) {
        this.params.set('sailor_key', this.dataForm.sailor.id)
        this.resultSearchTitle.push(`${this.$i18n.t('sailor')}: ${this.dataForm.sailor.sailorFullName}`)
      }
      if (this.dataForm.newDocument) {
        this.params.set('is_new_document', this.dataForm.newDocument.value)
        this.resultSearchTitle.push(`${this.$i18n.t('newDocument')}: ${this.dataForm.newDocument.name}`)
      }
      if (this.dataForm.statementType) {
        this.params.set('is_continue', this.dataForm.statementType.value)
        this.resultSearchTitle.push(`${this.$i18n.t('statementType')}: ${this.dataForm.statementType.name}`)
      }

      if (type === 'report') {
        this.viewSearch = false
        this.getReport('', this.params)
      } else this.getExcel('', this.params)
    },

    startSearch (searchQuery) {
      setSearchDelay(this, searchQuery, 'delaySearch')
    },

    goSearch (searchQuery) {
      if (searchQuery.length >= 3) {
        const body = {
          query: searchQuery
        }
        this.$api.post('api/v1/sailor/search_sailor/', body).then(response => {
          this.dataForm.sailorsSearchList = []
          if (response.status === 'success' && response.data.length) {
            response.data.map(item => {
              item.sailorFullName = `${item['last_' + this.labelName]} ${item['first_' + this.labelName]} ${item['middle_' + this.labelName] || ''}`
            })
            this.dataForm.sailorsSearchList = response.data
          }
        })
      }
    }
  }
}
