import { getStatus, getDateFormat, viewDetailedBlock, showDetailed, hideDetailed, getPaymentStatus } from '@/mixins/main'
import { mapState } from 'vuex'
import { checkAccess } from '@/mixins/permissions'
import SearchInTable from '@/components/atoms/SearchInTable.vue'
import Popover from '@/components/atoms/Popover.vue'

import UserHistoryInfo from '@/views/UserHistory/UserHistoryInfo/UserHistoryInfo.vue'

import SailorRecordBookLineShortInfo from '@/views/Sailor/SailorRecordBook/SailorRecordBookLine/SailorRecordBookLineShortInfo/SailorRecordBookLineShortInfo.vue'

import ReportFinanceInfo from '@/views/Report/ReportFinance/ReportFinanceInfo'
import BackOfficeCoursesList from '@/views/BackOffice/BackOfficeCourses/BackOfficeCoursesList/BackOfficeCoursesList.vue'
import BackOfficeDocumentPriceInfo from '@/views/BackOffice/BackOfficeDocumentsPrice/BackOfficeDocumentsPriceInfo/BackOfficeDocumentsPriceInfo.vue'
import BackOfficeDocumentPriceEdit from '@/views/BackOffice/BackOfficeDocumentsPrice/BackOfficeDocumentsPriceEdit/BackOfficeDocumentsPriceEdit.vue'
import BackOfficeAgentGroupsList from '@/views/BackOffice/BackOfficeAgentGroups/BackOfficeAgentGroupsList/BackOfficeAgentGroupsList.vue'
import BackOfficeGroupAgentInfo from '@/views/BackOffice/BackOfficeAgentGroups/BackOfficeAgentGroupsList/BackOfficeAgentGroupsInfo/BackOfficeAgentGroupsInfo.vue'
import BackOfficeAgentGroupsListEdit from '@/views/BackOffice/BackOfficeAgentGroups/BackOfficeAgentGroupsEdit/BackOfficeAgentGroupsEdit.vue'
import BackOfficeGroupAgentEdit from '@/views/BackOffice/BackOfficeAgentGroups/BackOfficeAgentGroupsList/BackOfficeAgentGroupsInfoEdit/BackOfficeAgentGroupsInfoEdit.vue'

export default {
  name: 'Table',
  components: {
    Popover,
    SearchInTable,
    SailorRecordBookLineShortInfo,
    UserHistoryInfo,
    ReportFinanceInfo,
    BackOfficeCoursesList,
    BackOfficeDocumentPriceInfo,
    BackOfficeDocumentPriceEdit,
    BackOfficeAgentGroupsList,
    BackOfficeGroupAgentInfo,
    BackOfficeAgentGroupsListEdit,
    BackOfficeGroupAgentEdit
  },
  props: {
    viewNewDoc: Boolean,
    labelKeyAdd: String,
    loader: Boolean,
    fields: Array,
    items: Array,
    sortBy: String,
    sortAcs: Boolean,
    sortDesc: Boolean,
    deleteRow: Function,
    getDocuments: Function,
    saveExcel: Function,
    type: String,
    link: String,
    componentInfo: String,
    componentEdit: String,
    componentStatus: String,
    componentFiles: String,
    componentShortInfo: String
  },
  data () {
    return {
      getStatus,
      getDateFormat,
      viewDetailedBlock,
      showDetailed,
      hideDetailed,
      getPaymentStatus,
      checkAccess,
      currentItems: [],
      selectedItems: [],
      checkedItems: [],
      filter: null,
      sortName: null,
      viewAdd: this.viewNewDoc,
      sortAcsBack: this.sortAcs,
      sortDescBack: this.sortDesc,
      documentMerging: false,
      allowContinueMerge: false,
      btnAdd: ['statementSRB', 'sailorPassport', 'education', 'student', 'qualification',
        'qualificationStatement', 'certification', 'certificationStatement', 'backOfficeCoefficient', 'backOfficeCourse',
        'sailorMedical', 'medicalStatement', 'experience', 'recordBookStatement', 'serviceRecordBook', 'educationStatement',
        'positionStatement', 'sailorFullNameChanges', 'sailorPassportStatement', 'sailorSQCStatement', 'sailorSQCProtocols',
        'sailorSQCWishes', 'backOfficeETIList', 'backOfficeCoursePrice', 'backOfficeDocumentPrices'],
      btnToSailor: ['reportBOAgent', 'documentSign', 'userHistory', 'reportDistributionSailor', 'reportBOPacket',
        'etiPayments', 'reportFinance', 'agentStatements'],
      btnToSailorDocument: ['statementSRB', 'qualificationPackageStatement', 'report', 'reportFinance', 'reportExcel',
        'reportDistributionGroup', 'reportBO', 'reportBOAgent', 'reportBOPacket', 'reportDistributionSailor',
        'backOfficeCourse', 'backOfficeDocumentPrices', 'backOfficeFutureDocumentPrices', 'backOfficePastDocumentPrices',
        'backOfficeAgentGroups', 'agentDocuments', 'statementETI', 'etiPayments', 'userHistory', 'menuStatementSQC',
        'statementAdvanceTraining'],
      btnToDocumentWithSailorId: ['statementSRB', 'qualificationPackageStatement', 'report', 'statementETI', 'menuStatementSQC',
        'statementAdvanceTraining', 'agentDocuments'],
      btnToReport: ['reportBO', 'reportBOAgent', 'reportDistributionGroup'],

      btnInfo: ['backOfficeCourse', 'backOfficeDocumentPrices', 'backOfficeAgentGroups', 'userHistory', 'reportFinance'],
      btnEdit: ['backOfficeFutureDocumentPrices', 'backOfficePastDocumentPrices', 'backOfficeAgentGroups'],
      btnDelete: ['backOfficeFutureDocumentPrices', 'backOfficePastDocumentPrices'],
      btnMerge: ['education', 'qualification'],
      btnToShortInfo: ['serviceRecordBookLine']
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr',
      labelValue: state => state.main.lang === 'en' ? 'value_eng' : 'value',
      isTrained: state => state.main.isTrained
    })
  },
  mounted () {
  },
  methods: {
    sorting (value, sortName) {
      this.sortName = sortName
      this.sortDescBack = this.sortAcsBack
      this.sortAcsBack = !this.sortDescBack
      let sort = this.sortDescBack ? '-' + sortName : sortName
      if (this.type === 'agentStatements' || this.type === 'etiPayments') {
        this.getDocuments(null, sort)
      } else {
        this.getDocuments(sort)
      }
    },

    tableRowClass (item) {
      switch (this.type) {
        case 'agentStatements':
          if (!item.date_end_proxy && checkAccess('agentStatements', 'highlightDocument')) {
            return 'empty-contract-date-end'
          }
          break
        case 'backOfficeETIList':
          if (item.is_disable) {
            return 'disable-table-row'
          } else if (item.is_red) {
            return 'red-table-row'
          }
          break
      }
    },

    startMergingDocuments () {
      this.documentMerging = !this.documentMerging
      if (this.documentMerging) {
        this.fields.unshift({ key: 'selectColumn', label: '' })
      } else {
        this.fields.splice(0, 1)
        this.selectedItems = []
        this.checkedItems = []
      }
    },

    selectDocument (row) {
      const documentIndex = this.selectedItems.findIndex(item => item.index === row.index)
      if (documentIndex === -1) {
        this.selectedItems.push(row)
      } else {
        this.selectedItems.splice(documentIndex, 1)
      }

      if (this.type === 'education') {
        this.allowContinueMerge = this.selectedItems && this.selectedItems.length === 2 &&
          this.selectedItems[0].item.type_document.id === this.selectedItems[1].item.type_document.id
      } else {
        const countDiplomaProof = this.selectedItems.filter(value => value.item.type_document.id === 16)
        this.allowContinueMerge = this.selectedItems && this.selectedItems.length === 2 &&
          (countDiplomaProof.length === 2 || !countDiplomaProof.length)
      }
    }
  }
}
