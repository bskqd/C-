import Vue from 'vue'
import VueRouter from 'vue-router'
import Main from '@/views/Main/Main.vue'

Vue.use(VueRouter)

const routes = [
  { path: '*',
    redirect: '/404'
  },
  {
    path: '/404',
    name: '404',
    component: () => import('../views/PageNotFound.vue')
  },
  {
    path: '/',
    name: 'home',
    component: Main
  },
  {
    path: '/registration',
    name: 'register',
    component: () => import('@/views/UserRegistration/UserRegistration.vue')
  },
  {
    path: '/login',
    name: 'authorization',
    component: () => import('@/views/Authorization/Authorization.vue')
  },
  {
    path: '/sailor/:id',
    name: 'sailor',
    props: {
      id: [Number, String]
    },
    component: () => import('@/views/Sailor/Sailor.vue'),
    children: [
      {
        path: '',
        name: '',
        component: () => import('@/views/Sailor/SailorPassport/SailorPassport.vue')
      },
      {
        path: 'passports/sailors',
        name: 'passports-sailors',
        component: () => import('@/views/Sailor/SailorPassport/SailorPassport.vue')
      },
      {
        path: 'passports/sailors/:documentID',
        name: 'passports-sailors-info',
        component: () => import('@/views/Sailor/SailorPassport/SailorPassportDocument/SailorPassportDocument.vue')
      },
      {
        path: 'passports/citizen',
        name: 'passports-citizen',
        component: () => import('@/views/Sailor/SailorCitizenPassport/SailorCitizenPassport.vue')
      },
      {
        path: 'passports/changes',
        name: 'passports-changes',
        component: () => import('@/views/Sailor/SailorFullNameChanges/SailorFullNameChanges.vue')
      },
      {
        path: 'passports/changes/:documentID',
        name: 'passports-changes-info',
        component: () => import('@/views/Sailor/SailorFullNameChanges/SailorFullNameChangesDocument/SailorFullNameChangesDocument.vue')
      },
      {
        path: 'passports/statements',
        name: 'passports-statements',
        component: () => import('@/views/Sailor/SailorPassportStatement/SailorPassportStatement.vue')
      },
      {
        path: 'passports/statements/:documentID',
        name: 'passports-statements-info',
        component: () => import('@/views/Sailor/SailorPassportStatement/SailorPassportStatementDocument/SailorPassportStatementDocument.vue')
      },
      {
        path: 'education/documents',
        name: 'education-documents',
        component: () => import('@/views/Sailor/SailorEducation/SailorEducation.vue')
      },
      {
        path: 'education/documents/:documentID',
        name: 'education-documents-info',
        component: () => import('@/views/Sailor/SailorEducation/SailorEducationDocument/SailorEducationDocument.vue')
      },
      {
        path: 'education/student',
        name: 'education-student',
        component: () => import('@/views/Sailor/SailorStudent/SailorStudent.vue')
      },
      {
        path: 'education/student/:documentID',
        name: 'education-student-info',
        component: () => import('@/views/Sailor/SailorStudent/SailorStudentDocument/SailorStudentDocument.vue')
      },
      {
        path: 'education/statements',
        name: 'education-statements',
        component: () => import('@/views/Sailor/SailorEducationStatement/SailorEducationStatement.vue')
      },
      {
        path: 'education/statements/:documentID',
        name: 'education-statements-info',
        component: () => import('@/views/Sailor/SailorEducationStatement/SailorEducationStatementDocument/SailorEducationStatementDocument.vue')
      },
      {
        path: 'qualification/documents',
        name: 'qualification-documents',
        component: () => import('@/views/Sailor/SailorQualification/SailorQualification.vue')
      },
      {
        path: 'qualification/documents/:documentID',
        name: 'qualification-documents-info',
        component: () => import('@/views/Sailor/SailorQualification/SailorQualificationDocument/SailorQualificationDocument.vue')
      },
      {
        path: 'qualification/statements',
        name: 'qualification-statements',
        component: () => import('@/views/Sailor/SailorQualificationStatement/SailorQualificationStatement.vue')
      },
      {
        path: 'qualification/statements/:documentID',
        name: 'qualification-statements-info',
        component: () => import('@/views/Sailor/SailorQualificationStatement/SailorQualificationStatementDocument/SailorQualificationStatementDocument.vue')
      },
      {
        path: 'certification/certificates',
        name: 'certification-certificates',
        component: () => import('@/views/Sailor/SailorCertification/SailorCertification.vue')
      },
      {
        path: 'certification/certificates/:documentID',
        name: 'certification-certificates-info',
        component: () => import('@/views/Sailor/SailorCertification/SailorCertificationDocument/SailorCertificationDocument.vue')
      },
      {
        path: 'certification/statements',
        name: 'certification-statements',
        component: () => import('@/views/Sailor/SailorCertificationStatement/SailorCertificationStatement.vue')
      },
      {
        path: 'certification/statements/:documentID',
        name: 'certification-statements-info',
        component: () => import('@/views/Sailor/SailorCertificationStatement/SailorCertificationStatementDocument/SailorCertificationStatementDocument.vue')
      },
      {
        path: 'experience/records',
        name: 'experience-records',
        component: () => import('@/views/Sailor/SailorRecordBook/SailorRecordBook.vue')
      },
      {
        path: 'experience/records/:documentID',
        name: 'experience-records-info',
        component: () => import('@/views/Sailor/SailorRecordBook/SailorRecordBookDocument/SailorRecordBookDocument.vue')
      },
      {
        path: 'experience/records/:documentID/line/',
        redirect: { name: 'experience-records-info' }
      },
      {
        path: 'experience/records/:documentID/line/:lineID',
        name: 'experience-records-line-info',
        component: () => import('@/views/Sailor/SailorRecordBook/SailorRecordBookLine/SailorRecordBookLineDocument/SailorRecordBookLineDocument.vue')
      },
      {
        path: 'experience/reference',
        name: 'experience-reference',
        component: () => import('@/views/Sailor/SailorExperience/SailorExperience.vue')
      },
      {
        path: 'experience/reference/:documentID',
        name: 'experience-reference-info',
        component: () => import('@/views/Sailor/SailorExperience/SailorExperienceDocument/SailorExperienceDocument.vue')
      },
      {
        path: 'experience/statements',
        name: 'experience-statements',
        component: () => import('@/views/Sailor/SailorRecordBookStatement/SailorRecordBookStatement.vue')
      },
      {
        path: 'experience/statements/:documentID',
        name: 'experience-statements-info',
        component: () => import('@/views/Sailor/SailorRecordBookStatement/SailorRecordBookStatementDocument/SailorRecordBookStatementDocument.vue')
      },
      {
        path: 'sqc/statements',
        name: 'sqc-statements',
        component: () => import('@/views/Sailor/SailorSQCStatement/SailorSQCStatement.vue')
      },
      {
        path: 'sqc/statements/:documentID',
        name: 'sqc-statements-info',
        component: () => import('@/views/Sailor/SailorSQCStatement/SailorSQCStatementDocument/SailorSQCStatementDocument.vue')
      },
      {
        path: 'sqc/protocols',
        name: 'sqc-protocols',
        component: () => import('@/views/Sailor/SailorSQCProtocols/SailorSQCProtocols.vue')
      },
      {
        path: 'sqc/protocols/:documentID',
        name: 'sqc-protocols-info',
        component: () => import('@/views/Sailor/SailorSQCProtocols/SailorSQCProtocolsDocument/SailorSQCProtocolsDocument.vue')
      },
      {
        path: 'sqc/wishes',
        name: 'sqc-wishes',
        component: () => import('@/views/Sailor/SailorSQCWishes/SailorSQCWishes.vue')
      },
      {
        path: 'sqc/wishes/:documentID',
        name: 'sqc-wishes-info',
        component: () => import('@/views/Sailor/SailorSQCWishes/SailorSQCWishesDocument/SailorSQCWishesDocument.vue')
      },
      {
        path: 'medical/certificates',
        name: 'medical-certificates',
        component: () => import('@/views/Sailor/SailorMedical/SailorMedical.vue')
      },
      {
        path: 'medical/certificates/:documentID',
        name: 'medical-certificates-info',
        component: () => import('@/views/Sailor/SailorMedical/SailorMedicalDocument/SailorMedicalDocument.vue')
      },
      {
        path: 'medical/statements',
        name: 'medical-statements',
        component: () => import('../views/Sailor/SailorMedicalStatement/SailorMedicalStatement.vue')
      },
      {
        path: 'medical/statements/:documentID',
        name: 'medical-statements-info',
        component: () => import('@/views/Sailor/SailorMedicalStatement/SailorMedicalStatementDocument/SailorMedicalStatementDocument.vue')
      },
      {
        path: 'position/statements',
        name: 'position-statements',
        component: () => import('../views/Sailor/SailorPositionStatement/SailorPositionStatement.vue')
      },
      {
        path: 'position/statements/:documentID',
        name: 'position-statements-info',
        component: () => import('@/views/Sailor/SailorPositionStatement/SailorPositionStatementDocument/SailorPositionStatementDocument.vue')
      }
    ]
  },
  {
    path: '/new-sailor',
    name: 'new-sailor',
    component: () => import('@/views/AddSailor/AddSailor.vue')
  },
  // {
  //   path: '/verification',
  //   name: 'verification',
  //   component: () => import('@/views/VerificationDocuments.vue')
  // },
  {
    path: '/processing-documents',
    name: 'processing-documents',
    component: () => import('@/views/PostVerification.vue')
  },
  {
    path: '/statement',
    name: 'statement',
    component: () => import('@/views/StatementSQC/StatementSQC.vue'),
    children: [
      {
        path: '/statement/sqc/approved',
        name: 'approved',
        props: () => ({ status: 24 }),
        component: () => import('@/views/StatementSQC/StatementSQCTable.vue')
      },
      {
        path: '/statement/sqc/processing',
        name: 'processing',
        props: () => ({ status: 25 }),
        component: () => import('@/views/StatementSQC/StatementSQCTable.vue')
      },
      {
        path: '/statement/sqc/from-PA',
        name: 'fromPA',
        props: () => ({ status: 42 }),
        component: () => import('@/views/StatementSQC/StatementSQCTable.vue')
      }
    ]
  },
  {
    path: '/directory',
    name: 'directory',
    component: () => import('@/views/Directory/Directory.vue'),
    children: [
      {
        path: '/directory/address',
        name: 'directory-address',
        component: () => import('@/views/Directory/DirectoryAddress/DirectoryAddress.vue')
      }
    ]
  },
  {
    path: '/upload-documents',
    name: 'upload-documents',
    component: () => import('@/views/UploadDocs.vue')
  },
  {
    path: '/new-accounts',
    name: 'new-accounts',
    component: () => import('@/views/NewAccounts/NewAccounts.vue')
  },
  {
    path: '/new-accounts/:documentID',
    name: 'new-accounts-info',
    component: () => import('@/views/NewAccounts/NewAccountsDocument.vue')
  },
  {
    path: '/report',
    name: 'report',
    component: () => import('@/views/Report/Report.vue'),
    children: [
      {
        path: '/report/sqc',
        name: 'sqc-report',
        component: () => import('@/views/Report/ReportSQC/ReportSQC.vue')
      },
      {
        path: '/report/cadet',
        name: 'cadet-report',
        component: () => import('@/views/Report/ReportCadet/ReportCadet.vue')
      },
      {
        path: '/report/education',
        name: 'education-report',
        component: () => import('@/views/Report/ReportEducation/ReportEducation.vue')
      },
      {
        path: '/report/qualification',
        name: 'qualification-report',
        component: () => import('@/views/Report/ReportQualification/ReportQualification.vue')
      },
      {
        path: '/report/certificate',
        name: 'certificates-report',
        component: () => import('@/views/Report/ReportETI/ReportETI.vue')
      },
      {
        path: '/report/sailorPassport',
        name: 'sailorPassport-report',
        component: () => import('@/views/Report/ReportSailorPassport/ReportSailorPassport.vue')
      },
      {
        path: '/report/financial',
        name: 'financial-report',
        component: () => import('@/views/Report/ReportFinance/ReportFinance.vue')
      },
      {
        path: '/report/excel',
        name: 'excel-report',
        component: () => import('@/views/Report/ReportExcel/ReportExcel.vue')
      },
      {
        path: '/report/debtor',
        name: 'debtor-report',
        component: () => import('@/views/Report/ReportDebtor/ReportDebtor.vue')
      },
      {
        path: '/report/debtor/group/:groupId',
        name: 'debtor-report-group',
        props (route) {
          return { search: route.query.search }
        },
        component: () => import('@/views/Report/ReportDebtor/ReportDebtorGroup.vue')
      },
      {
        path: '/report/debtor/group/:groupId/agent/:agentId',
        name: 'debtor-report-agent',
        props (route) {
          return { search: route.query.search }
        },
        component: () => import('@/views/Report/ReportDebtor/ReportDebtorAgent.vue')
      },
      {
        path: '/report/debtor/group/:groupId/agent/:agentId/sailor/:sailorId',
        name: 'debtor-report-sailor',
        props (route) {
          return { search: route.query.search }
        },
        component: () => import('@/views/Report/ReportDebtor/ReportDebtorSailor.vue')
      },
      {
        path: '/report/debtor/group/:groupId/agent/:agentId/sailor/:sailorId/packet/:packetId',
        name: 'debtor-report-packet',
        props (route) {
          return { search: route.query.search }
        },
        component: () => import('@/views/Report/ReportDebtor/ReportDebtorPacket.vue')
      },
      {
        path: '/report/distribution',
        name: 'distribution-report-group',
        component: () => import('@/views/Report/ReportDistribution/ReportDistributionGroup.vue')
      },
      {
        path: '/report/distribution/:typeDoc/seaman/:firstIdEntry',
        name: 'distribution-report-agent',
        props (route) {
          return { search: route.query.search }
        },
        component: () => import('@/views/Report/ReportDistribution/ReportDistributionAgent.vue')
      },
      {
        path: '/report/distribution/:typeDoc/seaman/:firstIdEntry/sailor/:secondIdEntry',
        name: 'distribution-report-sailor',
        props (route) {
          return { search: route.query.search }
        },
        component: () => import('@/views/Report/ReportDistribution/ReportDistributionSailor.vue')
      }
    ]
  },
  {
    path: '/statement/srb/all',
    name: 'srbAll',
    component: () => import('@/views/StatementSRB/StatementSRB.vue')
  },
  {
    path: '/documents-to-sign',
    name: 'documents-to-sign',
    component: () => import('@/views/DocumentsToSign.vue')
  },
  {
    path: '/package-qualification-statement',
    name: 'package-qualification-statement',
    component: () => import('@/views/QualificationStatementFromPackage.vue')
  },
  {
    path: '/back-office',
    name: 'back-office',
    component: () => import('@/views/BackOffice/BackOffice.vue'),
    children: [
      {
        path: '/back-office/coefficients',
        name: 'coefficients-backoffice',
        component: () => import('@/views/BackOffice/BackOfficeCoefficients/BackOfficeCoefficients.vue')
      },
      {
        path: '/back-office/coefficients/:documentID',
        name: 'coefficients-backoffice-info',
        component: () => import('@/views/BackOffice/BackOfficeCoefficients/BackOfficeCoefficientsDocument/BackOfficeCoefficientsDocument.vue')
      },
      {
        path: '/back-office/eti/courses',
        name: 'courses-backoffice',
        component: () => import('@/views/BackOffice/BackOfficeCourses/BackOfficeCourses.vue')
      },
      {
        path: '/back-office/eti/courses/:documentID',
        name: 'courses-backoffice-info',
        component: () => import('@/views/BackOffice/BackOfficeCourses/BackOfficeCoursesDocument/BackOfficeCoursesDocument.vue')
      },
      {
        path: '/back-office/eti/list',
        name: 'list-eti-backoffice',
        component: () => import('@/views/BackOffice/BackOfficeETIList/BackOfficeETIList.vue')
      },
      {
        path: '/back-office/eti/list/:documentID',
        name: 'list-eti-backoffice-info',
        component: () => import('../views/BackOffice/BackOfficeETIList/BackOfficeETIListDocument/BackOfficeETIListDocument.vue')
      },
      {
        path: '/back-office/eti/price-course',
        name: 'price-course-backoffice',
        component: () => import('@/views/BackOffice/BackOfficeCoursePrices/BackOfficeCoursePrices.vue')
      },
      {
        path: '/back-office/eti/price-course/:documentID',
        name: 'price-course-backoffice-info',
        component: () => import('@/views/BackOffice/BackOfficeCoursePrices/BackOfficeCoursePricesDocument/BackOfficeCoursePricesDocument.vue')
      },
      {
        path: '/back-office/eti/price',
        name: 'prices-eti-backoffice',
        component: () => import('@/views/BackOffice/BackOfficeDocumentsPrice/BackOfficeDocumentsPrice.vue')
      },
      {
        path: '/back-office/dealing',
        name: 'dealing-backoffice',
        component: () => import('@/views/BackOffice/BackOfficeDealing/BackOfficeDealing.vue')
      },
      {
        path: '/back-office/dealing/:documentID',
        name: 'dealing-backoffice-info',
        component: () => import('@/views/BackOffice/BackOfficeDealing/BackOfficeDealingDocument/BackOfficeDealingDocument.vue')
      },
      {
        path: '/back-office/agent-groups',
        name: 'agent-groups-backoffice',
        component: () => import('@/views/BackOffice/BackOfficeAgentGroups/BackOfficeAgentGroups.vue')
      }
    ]
  },
  {
    path: '/agent-statement-from-sailor',
    name: 'agent-statement-from-sailor',
    component: () => import('@/views/AgentStatements/AgentStatements.vue')
  },
  {
    path: '/agent-statement-from-sailor/:documentID',
    name: 'agent-statement-from-sailor-info',
    component: () => import('@/views/AgentStatements/AgentStatementsDocument/AgentStatementsDocument.vue')
  },
  {
    path: '/agent-statement',
    name: 'agent-statement',
    component: () => import('@/views/NewAgents/NewAgents.vue')
  },
  {
    path: '/agent-statement/:documentID',
    name: 'agent-statement-info',
    component: () => import('@/views/NewAgents/NewAgentsDocument/NewAgentsDocument.vue')
  },
  {
    path: '/agent-verification',
    name: 'agent-verification',
    component: () => import('@/views/AgentsDocument/AgentsDocument.vue')
  },
  {
    path: '/user-history',
    name: 'user-history',
    component: () => import('@/views/UserHistory/UserHistory.vue')
  },
  {
    path: '/user-notification',
    name: 'user-notification',
    component: () => import('@/views/UserNotification/UserNotification.vue')
  },
  {
    path: '/packet-qualification-statements',
    name: 'packet-qualification-statements',
    component: () => import('@/views/QualificationStatementFromPackage.vue')
  },
  {
    path: '/eti-statements',
    name: 'eti-statements',
    component: () => import('@/views/StatementETI/StatementETI.vue')
  },
  {
    path: '/documents-merging',
    name: 'documents-merging',
    props: true,
    component: () => import('@/components/molecules/DocumentsMerging/DocumentsMerging.vue')
  },
  {
    path: '/eti-payments',
    name: 'eti-payments',
    component: () => import('@/views/PaymentsETI/PaymentsETI.vue')
  },
  {
    path: '/advance-training-statements',
    name: 'advance-training-statements',
    component: () => import('@/views/StatementAdvanceTraining/StatementAdvanceTraining.vue')
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
