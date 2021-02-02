import store from '@/store'

const p = {}
const r = {}

export const setPermissions = () => {
  p.groupProfileId = store.state.main.user.group
  p.superAdmin = store.state.main.permissions.includes('superAdmin')
  p.mainInfoRO = store.state.main.permissions.includes('readMainInfo')
  p.mainInfoW = store.state.main.permissions.includes('writeMainInfo')
  p.newUserC = store.state.main.permissions.includes('createUsers')
  p.sailorC = store.state.main.permissions.includes('createSeafarer')
  p.ratingRO = store.state.main.permissions.includes('ratingSailor')
  p.ratingW = store.state.main.permissions.includes('changeRating')
  p.sailorWithoutTaxC = store.state.main.permissions.includes('createSeafarerWithoutTaxNumber')
  p.userHiystoryRO = store.state.main.permissions.includes('readUserHistory')
  p.packageQualificationStatementRO = store.state.main.permissions.includes('readListApplicationFromPacket')
  p.checkDocumentsW = store.state.main.permissions.includes('writeCheckDocuments')
  p.verificationAuthorRO = store.state.main.permissions.includes('readAuthorApprov')
  p.postVerificationW = store.state.main.permissions.includes('writePostVerificationDocuments')
  p.reportSqcProtocolRO = store.state.main.permissions.includes('reportSqcProtocol') || store.state.main.permissions.includes('reportProtocolSQC')
  p.reportSqcStatementRO = store.state.main.permissions.includes('readReportApplicationSQC')
  p.reportStudentRO = store.state.main.permissions.includes('readStudentReport')
  p.reportCertificateRO = store.state.main.permissions.includes('readCertificatesReport')
  p.reportSailorPassportRO = store.state.main.permissions.includes('readReportSailorPassport')
  p.reportEducationRO = store.state.main.permissions.includes('readGraduationReport')
  p.reportQualificationRO = store.state.main.permissions.includes('readReportQualificationDocument')
  p.reportListExcel = store.state.main.permissions.includes('readReportListOfFiles')
  p.reportFinanceRO = store.state.main.permissions.includes('readFinancialReport')
  p.postVerificationRO = store.state.main.permissions.includes('readPostVerification')
  p.agentStatementFromSailorRO = store.state.main.permissions.includes('readAgentApplicationFromSailor')
  p.agentStatementRO = store.state.main.permissions.includes('readAgentApplication')
  p.agentVerificationDocsRO = store.state.main.permissions.includes('readAgentVerificationDocs')
  p.agentsGroupRO = store.state.main.permissions.includes('readAgentGroups')
  p.agentsInGroupRO = store.state.main.permissions.includes('readMyAgents')
  p.packetPriceRO = store.state.main.permissions.includes('readPriceForPosition')
  p.agentInfoRO = store.state.main.permissions.includes('readAgentInfo')
  p.verificationCommentW = store.state.main.permissions.includes('writeCommentForVerification')
  p.etiStatementsRO = store.state.main.permissions.includes('readReportApplicationETI')
  p.mergeEducationDocuments = store.state.main.permissions.includes('merge_education_documents')
  p.mergeQualificationDocuments = store.state.main.permissions.includes('merge_qualification_documents')
  p.mergeSailors = store.state.main.permissions.includes('mergeSeafarer')
  p.etiPaymentsRO = store.state.main.permissions.includes('readPaymentsETI')
  p.advanceTrainingStatementsRO = store.state.main.permissions.includes('readReportApplicationATC')

  p.sailorPassportRO = store.state.main.permissions.includes('readSeafarerPassport')
  p.sailorPassportC = store.state.main.permissions.includes('createSeafarerPassport')
  p.newSailorPassportC = store.state.main.permissions.includes('createNewSailorPassport')
  p.sailorPassportW = store.state.main.permissions.includes('writeSeafarerPassport')
  p.sailorPassportWS = store.state.main.permissions.includes('writeSeafarerPassportStatus')
  p.sailorPassportD = store.state.main.permissions.includes('deleteSeafarerPassport')
  p.sailorPassportPreVerificationW = store.state.main.permissions.includes('writeSeafarerPassportPreVerification')
  p.sailorPassportPreVerificationWS = store.state.main.permissions.includes('writeSeafarerPassportPreVerificationStatus')
  p.civilPassportRO = store.state.main.permissions.includes('readCitizenPassport')

  p.civilPassportW = store.state.main.permissions.includes('writeCitizenPassportInfo')

  p.fullNameChangesRO = store.state.main.permissions.includes('readSurnameChanges')
  p.fullNameChangesC = store.state.main.permissions.includes('createSurnameChanges')
  p.fullNameChangesW = store.state.main.permissions.includes('writeSurnameChanges')
  p.fullNameChangesD = store.state.main.permissions.includes('deleteSurnameChanges')

  p.sailorPassportStatementRO = store.state.main.permissions.includes('readSeafarerPassportApplication')
  p.sailorPassportStatementC = store.state.main.permissions.includes('createSeafarerPassportApplication')
  p.sailorPassportStatementWS = store.state.main.permissions.includes('writeSeafarerPassportApplicationStatus')
  p.sailorPassportStatementD = store.state.main.permissions.includes('deleteSeafarerPassportApplication')

  p.educationRO = store.state.main.permissions.includes('readGraduation')
  p.educationC = store.state.main.permissions.includes('createGraduation')
  p.educationW = store.state.main.permissions.includes('writeGraduation')
  p.educationWS = store.state.main.permissions.includes('writeGraduationStatus')
  p.educationD = store.state.main.permissions.includes('deleteGraduation')
  p.educationPhotoC = store.state.main.permissions.includes('addPhotoGraduation')
  p.educationFromExcelC = store.state.main.permissions.includes('createEducationDocsFromExel')
  p.educationPreVerificationW = store.state.main.permissions.includes('writeGraduationPreVerification')
  p.educationPreVerificationWS = store.state.main.permissions.includes('writeGraduationPreVerificationStatus')

  p.studentRO = store.state.main.permissions.includes('readStudentsID')
  p.studentC = store.state.main.permissions.includes('createStudentsID')
  p.studentW = store.state.main.permissions.includes('writeStudentsID')
  p.studentWS = store.state.main.permissions.includes('writeStudentsIDStatus')
  p.studentD = store.state.main.permissions.includes('deleteStudentsID')

  p.educationStatementRO = store.state.main.permissions.includes('readStatementAdvancedTraining')
  p.educationStatementC = store.state.main.permissions.includes('createStatementAdvancedTraining')
  p.educationStatementW = store.state.main.permissions.includes('writeStatementAdvancedTraining')
  p.educationStatementWS = store.state.main.permissions.includes('writeStatementAdvancedTrainingStatus')
  p.educationStatementT = store.state.main.permissions.includes('createAdvancedTraining')
  p.educationStatementD = store.state.main.permissions.includes('deleteStatementAdvancedTraining')

  p.qualificationRO = store.state.main.permissions.includes('readQualification')
  p.qualificationC = store.state.main.permissions.includes('createQualification')
  p.existQualificationC = store.state.main.permissions.includes('createExistsQualification')
  p.qualificationW = store.state.main.permissions.includes('writeQualification')
  p.qualificationWS = store.state.main.permissions.includes('writeQualificationStatus')
  p.qualificationWAS = store.state.main.permissions.includes('writeQualificationInAnyStatus')
  p.qualificationD = store.state.main.permissions.includes('deleteQualification')
  p.qualificationPreVerificationW = store.state.main.permissions.includes('writeQualificationPreVerification')
  p.qualificationPreVerificationWS = store.state.main.permissions.includes('writeQualificationPreVerificationStatus')

  p.qualificationStatementRO = store.state.main.permissions.includes('readQualificationApplication')
  p.qualificationStatementC = store.state.main.permissions.includes('createQualificationApplication')
  p.qualificationStatementW = store.state.main.permissions.includes('writeQualificationApplication')
  p.qualificationStatementWS = store.state.main.permissions.includes('writeQualificationApplicationStatus')
  p.qualificationStatementWAS = store.state.main.permissions.includes('writeQualificationInApplicationAnyStatus')
  p.qualificationStatementD = store.state.main.permissions.includes('deleteQualificationApplication')

  p.etiCertificatesRO = store.state.main.permissions.includes('readCertificates')
  p.etiCertificatesC = store.state.main.permissions.includes('addCertificatesETI')
  p.etiCertificatesWS = store.state.main.permissions.includes('writeCertificatesStatus')

  p.etiStatementRO = store.state.main.permissions.includes('readCertificateApplication')
  p.etiStatementC = store.state.main.permissions.includes('createCertificationApplication')
  p.etiStatementW = store.state.main.permissions.includes('writeCertificationApplication')
  p.etiStatementWS = store.state.main.permissions.includes('writeCertificationApplicationStatus')
  p.etiStatementD = store.state.main.permissions.includes('deleteCertificationApplication')

  p.etiCoursePriceRO = store.state.main.permissions.includes('readCoursePrice')
  p.etiCoursePriceW = store.state.main.permissions.includes('writeCoursePrice')

  p.etiRatioRO = store.state.main.permissions.includes('readETIProfitPart')
  p.etiRatioW = store.state.main.permissions.includes('writeETIProfitPart')

  p.etiInstitutionListRO = store.state.main.permissions.includes('readInstitutionListETI')

  p.etiCourseListRO = store.state.main.permissions.includes('readETIRegistry')
  p.etiCourseListC = store.state.main.permissions.includes('createETIRegistry')
  p.etiCourseListW = store.state.main.permissions.includes('writeETIRegistry')
  p.etiCourseListD = store.state.main.permissions.includes('deleteETIRegistry')

  p.etiDealingRO = store.state.main.permissions.includes('readDealingETI')
  p.sqcStatementApprovedW = store.state.main.permissions.includes('readApplicationSQCApproved')
  p.sqcStatementProcessW = store.state.main.permissions.includes('readApplicationSQCProccess')
  p.sqcStatementFromCabinetRO = store.state.main.permissions.includes('readApplicationSQCCreatedFromPA')
  p.serviceRecordBookRO = store.state.main.permissions.includes('readRecordBook')
  p.existServiceRecordBookC = store.state.main.permissions.includes('createExistRecordBook')

  p.newServiceRecordBookC = store.state.main.permissions.includes('createNewRecordBook')
  p.serviceRecordBookW = store.state.main.permissions.includes('writeRecordBook')
  p.serviceRecordBookWS = store.state.main.permissions.includes('writeRecordBookStatus')
  p.serviceRecordBookD = store.state.main.permissions.includes('deleteRecordBook')
  p.serviceRecordBookPreVerificationW = store.state.main.permissions.includes('writeRecordBookPreVerification')
  p.serviceRecordBookPreVerificationWS = store.state.main.permissions.includes('writeRecordBookPreVerificationStatus')

  p.serviceRecordBookStatementW = store.state.main.permissions.includes('writeApplicationRecordBook')
  p.serviceRecordBookStatementD = store.state.main.permissions.includes('deleteApplicationRecordBook')

  p.experienceRO = store.state.main.permissions.includes('readExperience')
  p.experienceNotConventionalRO = store.state.main.permissions.includes('readExperienceNotConventional')
  p.experiencePreVerificationW = store.state.main.permissions.includes('writeExperiencePreVerification')
  p.experiencePreVerificationWS = store.state.main.permissions.includes('writeExperiencePreVerificationStatus')
  p.experienceC = store.state.main.permissions.includes('createExperience')
  p.experienceW = store.state.main.permissions.includes('writeExperience')
  p.experienceWS = store.state.main.permissions.includes('writeExperienceStatus')
  p.experienceNotConventionalC = store.state.main.permissions.includes('createExperienceNotConventional')
  p.experienceNotConventionalW = store.state.main.permissions.includes('writeExperienceNotConventional')
  p.experienceNotConventionalWS = store.state.main.permissions.includes('writeExperienceNotConventionalStatus')
  p.experienceD = store.state.main.permissions.includes('deleteExperience')

  p.recordBookLineC = store.state.main.permissions.includes('createRecordBookEntry')
  p.recordBookLineW = store.state.main.permissions.includes('writeRecordBookEntry')
  p.recordBookLineWS = store.state.main.permissions.includes('writeRecordBookEntryStatus')
  p.recordBookLineD = store.state.main.permissions.includes('deleteRecordBookEntry')

  p.sqcStatementRO = store.state.main.permissions.includes('readApplicationSQC')
  p.sqcStatementC = store.state.main.permissions.includes('createApplicationSQC')
  p.sqcStatementWS = store.state.main.permissions.includes('writeApplicationSQCStatus')
  p.sqcStatementRejectedWS = store.state.main.permissions.includes('writeApplicationSQCStatusRejected')
  p.sqcStatementPaymentW = store.state.main.permissions.includes('writeApplicationSQCPayment')
  p.sqcStatementCadetWS = store.state.main.permissions.includes('writeApplicationSQCStatusCadet')
  p.sqcStatementPreVerificationW = store.state.main.permissions.includes('writeApplicationSQCPreVerification')
  p.sqcStatementPreVerificationWS = store.state.main.permissions.includes('writeApplicationSQCPreVerificationStatus')
  p.sqcStatementD = store.state.main.permissions.includes('deleteApplicationSQC')

  p.sqcProtocolRO = store.state.main.permissions.includes('readProtocolSQC')
  p.sqcProtocolC = store.state.main.permissions.includes('createProtocolSQC')
  p.sqcProtocolW = store.state.main.permissions.includes('writeProtocolSQC')
  p.sqcProtocolWS = store.state.main.permissions.includes('writeProtocolSQCStatus')
  p.sqcProtocolD = store.state.main.permissions.includes('deleteProtocolSQC')
  p.sqcProtocolRegenerationW = store.state.main.permissions.includes('writeRegenerateProtocolSQC')
  p.sqcProtocolStampW = store.state.main.permissions.includes('writeStamp')

  p.sqcWishesRO = store.state.main.permissions.includes('readWishesSQC')
  p.sqcWishesC = store.state.main.permissions.includes('createWishesSQC')
  p.sqcWishesU = store.state.main.permissions.includes('updateWishesSQC')
  p.sqcWishesT = store.state.main.permissions.includes('transferWishesSQC')
  p.sqcWishesD = store.state.main.permissions.includes('deleteWishesSQC')

  p.medicalRO = store.state.main.permissions.includes('readMedical')
  p.medicalC = store.state.main.permissions.includes('createMedical')
  p.medicalW = store.state.main.permissions.includes('writeMedical')
  p.medicalWS = store.state.main.permissions.includes('writeMedicalStatus')
  p.medicalD = store.state.main.permissions.includes('deleteMedical')
  p.medicalPreVerificationW = store.state.main.permissions.includes('writeMedicalPreVerification')
  p.medicalPreVerificationWS = store.state.main.permissions.includes('writeMedicalPreVerificationStatus')

  p.medicalStatementRO = store.state.main.permissions.includes('readStatementMedicalCertificate')
  p.medicalStatementC = store.state.main.permissions.includes('createStatementMedicalCertificate')
  p.medicalStatementW = store.state.main.permissions.includes('writeStatementMedicalCertificate')
  p.medicalStatementWS = store.state.main.permissions.includes('writeStatementMedicalCertificateStatus')
  p.medicalStatementD = store.state.main.permissions.includes('deleteStatementMedicalCertificate')
  p.medicalStatementT = store.state.main.permissions.includes('writeStatementMedicalToDocument')

  p.packetServiceRO = store.state.main.permissions.includes('readPacketService')
  p.packetServiceC = store.state.main.permissions.includes('createPacketService')
  p.packetServiceW = store.state.main.permissions.includes('writePacketService')
  p.packetServiceD = store.state.main.permissions.includes('deletePacketService')

  p.newAgentsStatementsW = store.state.main.permissions.includes('writeAgentApplication')

  p.agentStatementW = store.state.main.permissions.includes('writeAgentApplicationFromSailor')
  p.agentStatementA = store.state.main.permissions.includes('applyAgentApplicationFromSailor')

  p.backOfficeETIListC = store.state.main.permissions.includes('createInstitutionListETI')
  p.backOfficeETIListW = store.state.main.permissions.includes('writeInstitutionListETI')
  p.backOfficeDocumentsPriceW = store.state.main.permissions.includes('writePriceForPosition')
  p.backOfficeDealingW = store.state.main.permissions.includes('backOfficeDealingW')
}

export const setRoles = () => {
  r.sailorRating = store.state.sailor.rating
  r.userID = store.state.main.user.id
  r.commissioner = store.state.main.user.commissioner
  r.sailorIsSQC = store.state.sailor.sailorSQC
  r.sailorPreVerification = store.state.sailor.sailorVerify
  r.existSailorAgent = store.state.sailor.agentInfo
  r.editableByAgent = store.state.sailor.editableByAgent
  r.agent = store.state.main.user.type_user === 'agent'
  r.dpd = store.state.main.user.type_user === 'dpd'
  r.headAgent = store.state.main.user.type_user === 'head_agent'
  r.secretaryService = store.state.main.user.type_user === 'secretary_service'
  r.backOffice = store.state.main.user.type_user === 'back_office'
  r.marad = store.state.main.user.type_user === 'marad'
  r.medical = store.state.main.user.type_user === 'medical'
  r.secretarySQC = store.state.main.user.type_user === 'secretary_sqc'
  r.etiWorker = store.state.main.user.type_user === 'eti_employee'
  r.secretaryATC = store.state.main.user.type_user === 'secretary_atc'
}

export const checkAccess = (typeRule = null, typeDocument = null, sailorDocument = null, photo = null) => {
  if (p.superAdmin) return true

  switch (typeRule) {
    case 'admin':
      return p.superAdmin
    case 'agent':
      return r.agent
    case 'secretaryService':
      return r.secretaryService
    case 'backOffice':
      return r.backOffice
    case 'etiWorker':
      return r.etiWorker
    case 'headAgent':
      return r.headAgent
    case 'marad':
      return r.marad
    case 'medical':
      return r.medical
    case 'menuItem-agentInfo':
      return p.agentInfoRO
    case 'menuItem-sailor':
      return p.mainInfoRO
    case 'menuLabel-documents':
      return p.sqcStatementApprovedW || p.sqcStatementProcessW || p.sqcStatementProcessW ||
        p.serviceRecordBookStatementW || p.etiStatementsRO || p.etiPaymentsRO || p.agentVerificationDocsRO ||
        p.checkDocumentsW || p.packageQualificationStatementRO || p.reportSqcProtocolRO || p.reportSqcStatementRO ||
        p.reportStudentRO || p.reportEducationRO || p.reportQualificationRO || p.reportCertificateRO ||
        p.reportListExcel || p.userHiystoryRO || p.advanceTrainingStatementsRO || p.reportSailorPassportRO
    case 'menuLabel-admin':
      return p.etiRatioRO || p.etiCourseListRO || p.etiCoursePriceRO || p.packetPriceRO || p.etiInstitutionListRO ||
        p.etiDealingRO || p.agentsGroupRO || p.agentsInGroupRO || p.agentStatementRO || p.agentStatementFromSailorRO
    case 'menuLabel-settings':
      return p.newUserC || p.superAdmin
    case 'menuItem-statementSQC':
      return p.sqcStatementApprovedW || p.sqcStatementProcessW || p.sqcStatementProcessW
    case 'menuItem-statementETI':
      return p.etiStatementsRO
    case 'menuItem-statementAdvanceTraining':
      return p.advanceTrainingStatementsRO
    case 'tab-statementSQCApproved':
      return p.sqcStatementApprovedW
    case 'tab-statementSQCProcess':
      return p.sqcStatementProcessW
    case 'tab-statementSQCFromPA':
      return p.sqcStatementFromCabinetRO
    case 'tab-statementServiceRecordBook':
      return p.serviceRecordBookStatementW
    case 'menuItem-postVerificationDocuments':
      return p.postVerificationRO
    case 'menuItem-agentVerification':
      return p.agentVerificationDocsRO
    case 'menuItem-verificationAccount':
      return p.checkDocumentsW
    case 'menuItem-documentsToSign':
      return r.commissioner
    case 'menuItem-report':
      return p.reportSqcProtocolRO || p.reportSqcStatementRO || p.reportStudentRO || p.reportEducationRO ||
        p.reportQualificationRO || p.reportCertificateRO || p.reportListExcel || p.reportSailorPassportRO
    case 'sqc-report':
      return p.reportSqcProtocolRO || p.reportSqcStatementRO
    case 'cadet-report':
      return p.reportStudentRO
    case 'education-report':
      return p.reportEducationRO
    case 'qualification-report':
      return p.reportQualificationRO
    case 'certificates-report':
      return p.reportCertificateRO
    case 'sailorPassport-report':
      return p.reportSailorPassportRO
    case 'financial-report':
      return p.reportFinanceRO
    case 'excel-report':
      return p.reportListExcel
    case 'menuItem-upload':
      return p.educationFromExcelC
    case 'menuItem-userHistory':
      return p.userHiystoryRO
    case 'menuItem-etiRatio':
      return p.etiRatioRO
    case 'menuItem-etiCourse':
      return p.etiCourseListRO
    case 'menuItem-priceEtiCourse':
      return p.etiCoursePriceRO
    case 'menuItem-pricePacket':
      return p.packetPriceRO
    case 'menuItem-agentsStatement':
      return p.agentStatementRO
    case 'menuItem-agentsStatementFromSailor':
      return p.agentStatementFromSailorRO
    case 'menuItem-etiInstitution':
      return p.etiInstitutionListRO
    case 'menuItem-etiDealing':
      return p.etiDealingRO
    case 'menuItem-newUser':
      return p.newUserC
    case 'menuItem-agents':
      return p.agentsGroupRO || p.agentsInGroupRO
    case 'menuItem-backOffice':
      return p.etiRatioRO || p.etiCourseListRO || p.etiCoursePriceRO || p.packetPriceRO || p.etiInstitutionListRO ||
        p.etiDealingRO || p.agentsGroupRO || p.agentsInGroupRO
    case 'menuItem-qualificationPackageStatement':
      return p.packageQualificationStatementRO
    case 'menuItem-etiPayments':
      return p.etiPaymentsRO

    case 'tab-sailorPassport':
      return p.sailorPassportRO
    case 'tab-civilPassport':
      return p.civilPassportRO
    case 'tab-fullNameChanges':
      return p.fullNameChangesRO
    case 'tab-sailorPassportStatement':
      return p.sailorPassportStatementRO
    case 'tab-education':
      return p.educationRO
    case 'tab-student':
      return p.studentRO
    case 'tab-educationStatement':
      return p.educationStatementRO
    case 'tab-qualification':
      return p.qualificationRO
    case 'tab-qualificationStatement':
      return p.qualificationStatementRO
    case 'tab-etiCertificate':
      return p.etiCertificatesRO || p.etiCertificatesC
    case 'tab-etiStatement':
      return p.etiStatementRO
    case 'tab-experience':
      return p.experienceRO || p.experienceNotConventionalRO
    case 'tab-serviceRecordBook':
      return p.serviceRecordBookRO
    case 'tab-serviceRecordStatement':
      return p.serviceRecordBookStatementW || r.marad
    case 'tab-sqcProtocol':
      return p.sqcProtocolRO
    case 'tab-sqcStatement':
      return p.sqcStatementRO
    case 'tab-sqcWishes':
      return p.sqcWishesRO
    case 'tab-medical':
      return p.medicalRO
    case 'tab-medicalStatement':
      return p.medicalStatementRO
    case 'tab-positionStatement':
      return p.packetServiceRO

    case 'main-addSailor':
      return p.sailorC && !r.agent
    case 'main-addSailorWithoutTaxNumber':
      return p.sailorWithoutTaxC
    case 'main-agent':
      return r.agent
    case 'main-agentsSailor':
      return r.agent || r.headAgent || r.secretaryService || r.marad
    case 'main-sailorsList':
      return !r.agent && !r.headAgent && !r.secretaryService && !r.marad
    case 'main-search':
      return r.agent || r.headAgent || r.secretaryService
    case 'main-editInfo':
      return p.mainInfoW
    case 'main-ratingAll':
      return p.ratingRO || p.ratingW
    case 'main-ratingW':
      return p.ratingW
    case 'signDocument':
      return r.commissioner
    case 'document-author-view':
      return p.checkDocumentsW
    case 'verification-author-view':
      return p.verificationAuthorRO
    case 'user-history':
      return p.userHiystoryRO
    case 'verification-comment':
      return p.verificationCommentW
    case 'displaySearch':
      return !r.etiWorker && !r.secretaryATC
    case 'documents-merging':
      return p.mergeEducationDocuments || p.mergeQualificationDocuments
    case 'sailors-merging':
      return p.mergeSailors

    case 'statementSRB':
      switch (typeDocument) {
        case 'sailorLink':
          return true
        case 'create':
          return false
        case 'edit':
          return false
        case 'editStatus':
          return sailorDocument.status.id !== 12 && sailorDocument.status.id !== 47
        case 'files':
          return true
        case 'delete':
          return p.superAdmin
      }
      break
    case 'newAccounts':
      switch (typeDocument) {
        case 'sailorLink':
          return sailorDocument.item.sailor || sailorDocument.item.sailor_id
        case 'create':
          return false
        case 'edit':
          return true
        case 'editStatus':
          return false
        case 'files':
          return true
        case 'delete':
          return false
      }
      break
    case 'sailorPassport':
      switch (typeDocument) {
        case 'create':
          return (p.sailorPassportC && p.groupProfileId !== 37) ||
            (p.sailorPassportC && p.groupProfileId === 37 && !r.sailorIsSQC) || (p.newSailorPassportC && r.dpd)
        case 'edit':
          return (p.sailorPassportPreVerificationW && sailorDocument.status_document.id === 74) ||
            (((p.sailorPassportW && p.groupProfileId !== 37) ||
              (p.sailorPassportW && p.groupProfileId === 37 && !r.sailorIsSQC)) && sailorDocument.status_document.id === 74)
        case 'editStatus':
          return (p.sailorPassportPreVerificationWS && sailorDocument.status_document.id === 74 && r.sailorPreVerification) ||
            (p.sailorPassportWS && sailorDocument.status_document.id === 34) ||
            (p.postVerificationW && sailorDocument.status_document.id === 60)
        case 'files':
          return true
        case 'delete':
          return p.sailorPassportD && r.agent && sailorDocument.status_document.id === 74
        case 'deleteFile':
          return p.sailorPassportD && ((r.agent && sailorDocument.status_document.id === 74 && !photo.isDeleted) || (r.backOffice && photo.isDeleted))
        case 'preVerification':
          return !p.sailorPassportPreVerificationWS && !r.sailorPreVerification && sailorDocument.status_document.id !== 74
        case 'verificationSteps':
          return p.sailorPassportWS
        case 'addExistPassport':
          return (p.sailorPassportC && p.groupProfileId !== 37) || (p.sailorPassportC && p.groupProfileId === 37 && !r.sailorIsSQC)
        case 'addNewPassport':
          return p.newSailorPassportC
      }
      break
    case 'civilPassport':
      switch (typeDocument) {
        case 'edit':
          return p.civilPassportW
        case 'files':
          return true
        case 'deleteFile':
          return false
      }
      break
    case 'sailorFullNameChanges':
      switch (typeDocument) {
        case 'create':
          return p.fullNameChangesC
        case 'edit':
          return p.fullNameChangesW && sailorDocument.lastRecord
        case 'files':
          return true
        case 'delete':
          return p.fullNameChangesD
        case 'deleteFile':
          return p.fullNameChangesD && (!photo.isDeleted || (r.backOffice && photo.isDeleted))
      }
      break
    case 'sailorPassportStatement':
      switch (typeDocument) {
        case 'create':
          return (!r.dpd && p.sailorPassportStatementC) || (!r.existSailorAgent && r.dpd && p.sailorPassportStatementC)
        case 'editStatus':
          return p.sailorPassportStatementWS && (sailorDocument.status_document.id === 72 || sailorDocument.status_document.id === 42)
        case 'files':
          return true
        case 'delete':
          return p.sailorPassportStatementD
        case 'deleteFile':
          return p.sailorPassportStatementD && (!photo.isDeleted || (r.backOffice && photo.isDeleted))
      }
      break
    case 'education':
      switch (typeDocument) {
        case 'create':
          return p.educationC
        case 'edit':
          return p.educationPhotoC || (p.educationPreVerificationW && sailorDocument.status_document.id === 74) ||
            (((p.educationW && p.sailorDocument !== 37) || (p.educationW && p.sailorDocument === 37 && !r.sailorIsSQC)) &&
              sailorDocument.status_document.id === 74)
        case 'editStatus':
          return (p.educationPreVerificationWS && sailorDocument.status_document.id === 74 && r.sailorPreVerification) ||
              ((p.educationWS && p.sailorDocument !== 37 && (sailorDocument.status_document.id === 2 || sailorDocument.status_document.id === 34)) ||
                (p.educationWS && p.sailorDocument === 37 && (sailorDocument.type_document.id === 2 || sailorDocument.type_document.id === 4) &&
                  (sailorDocument.status_document.id === 34 || sailorDocument.status_document.id === 14))) ||
              (p.postVerificationW && sailorDocument.status_document.id === 60)
        case 'files':
          return true
        case 'delete':
          return p.educationD && r.agent && sailorDocument.status_document.id === 74
        case 'deleteFile':
          return p.educationD && ((r.agent && sailorDocument.status_document.id === 74 && !photo.isDeleted) || (r.backOffice && photo.isDeleted))
        case 'preVerification':
          return !p.educationPreVerificationWS && !r.sailorPreVerification && sailorDocument.status_document.id !== 74
        case 'editRegistryNumber':
          return !p.educationPhotoC
        case 'verificationSteps':
          return (p.educationWS && p.sailorDocument !== 37) ||
            (p.educationWS && p.sailorDocument === 37 && (sailorDocument.type_document.id === 2 ||
              sailorDocument.type_document.id === 4))
        case 'merging':
          return p.mergeEducationDocuments
      }
      break
    case 'student':
      switch (typeDocument) {
        case 'create':
          return p.studentC
        case 'edit':
          return p.studentW
        case 'editStatus':
          return p.studentWS
        case 'files':
          return true
        case 'delete':
          return p.studentD
        case 'deleteFile':
          return p.studentD && (!photo.isDeleted || (r.backOffice && photo.isDeleted))
      }
      break
    case 'educationStatement':
      switch (typeDocument) {
        case 'create':
          return p.educationStatementC
        case 'edit':
          return p.educationStatementW && (sailorDocument.status_document.id === 80 || sailorDocument.status_document.id === 42)
        case 'editStatus':
          return p.educationStatementWS && (sailorDocument.status_document.id === 80 || sailorDocument.status_document.id === 42)
        case 'files':
          return true
        case 'delete':
          return p.educationStatementD
        case 'deleteFile':
          return p.educationStatementD && (!photo.isDeleted || (r.backOffice && photo.isDeleted))
        case 'transfer':
          return (p.educationC || p.educationStatementT) && sailorDocument.status_document.id === 78
      }
      break
    case 'qualification':
      switch (typeDocument) {
        case 'create':
          return p.qualificationC || p.existQualificationC
        case 'createNewQualification':
          return !p.existQualificationC
        case 'edit':
          return p.qualificationWAS ||
          (p.qualificationPreVerificationW && sailorDocument.status_document.id === 74) ||
          (p.qualificationW && (p.sailorDocument === 37 || p.sailorDocument === 20) &&
            (sailorDocument.status_document.id === 34 || sailorDocument.status_document.id === 14 || sailorDocument.status_document.id === 74) &&
            !sailorDocument.new_document) ||
          (p.qualificationWS && p.qualificationC && (sailorDocument.status_document.id === 21 || sailorDocument.status_document.id === 74)) ||
          ((r.secretaryService || r.agent) && sailorDocument.status_document.id === 74)
        case 'editStatus':
          return (p.qualificationPreVerificationWS && sailorDocument.status_document.id === 74 && r.sailorPreVerification) ||
            (p.qualificationWS && p.groupProfileId === 37 && (sailorDocument.status_document.id === 19 ||
              sailorDocument.status_document.id === 21 || sailorDocument.status_document.id === 2)) ||
            (p.qualificationWS && p.groupProfileId !== 37 && (sailorDocument.status_document.id === 34 || sailorDocument.status_document.id === 14 ||
              sailorDocument.status_document.id === 19 || (r.editableByAgent && sailorDocument.status_document.id === 74))) ||
            (p.postVerificationW && sailorDocument.status_document.id === 60)
        case 'editStrictBlank':
          return p.qualificationWAS || (p.qualificationWS && p.qualificationC &&
            sailorDocument.type_document.id !== 3 && sailorDocument.status_document.id === 21)
        case 'files':
          return true
        case 'delete':
          return (p.qualificationD && r.agent && sailorDocument.status_document.id === 74) ||
            (p.qualificationD && !r.agent)
        case 'deleteFile':
          return p.qualificationD && ((r.agent && sailorDocument.status_document.id === 74 && !photo.isDeleted) ||
            (!r.agent && !photo.isDeleted) || (r.backOffice && photo.isDeleted))
        case 'preVerification':
          return !p.qualificationPreVerificationWS && !r.sailorPreVerification && sailorDocument.status_document.id !== 74
        case 'verificationSteps':
          return p.qualificationWS && p.sailorDocument !== 37
        case 'merging':
          return p.mergeQualificationDocuments
      }
      break
    case 'qualificationStatement':
      switch (typeDocument) {
        case 'create':
          return (p.qualificationStatementC && r.dpd && !r.existSailorAgent) || (p.qualificationStatementC && !r.dpd)
        case 'edit':
          return p.qualificationStatementW && sailorDocument.status_document.id === 25
        case 'editStatus':
          return p.qualificationStatementWAS || (sailorDocument.status_document.id === 87 && sailorDocument.status_dkk.have_all_docs && r.marad) ||
            (p.qualificationStatementWS && sailorDocument.status_dkk.have_all_docs)
        case 'files':
          return false
        case 'delete':
          return p.qualificationStatementD
        case 'deleteFile':
          return p.qualificationStatementD && ((r.agent && sailorDocument.status_document.id === 74 && !photo.isDeleted) || (r.backOffice && photo.isDeleted))
        case 'viewExperienceTable':
          return p.sailorDocument !== 37
        case 'viewPayment':
          return sailorDocument.status_dkk.have_all_docs && !(sailorDocument.status_document.id === 87 && r.marad)
        case 'viewStatus':
          return sailorDocument.is_payed && !(sailorDocument.status_document.id === 87 && r.marad)
        case 'maradVerification':
          return sailorDocument.status_document.id === 87 && r.marad
      }
      break
    case 'certification':
      switch (typeDocument) {
        case 'create':
          return p.etiCertificatesC
        case 'editStatus':
          return p.etiCertificatesWS && sailorDocument.status_document.id === 42
        case 'delete':
          return p.superAdmin
      }
      break
    case 'certificationStatement':
      switch (typeDocument) {
        case 'create':
          return p.etiStatementC
        case 'edit':
          return p.etiStatementW && sailorDocument.status_document.id === 63
        case 'editStatus':
          return p.etiStatementWS && sailorDocument.status_document.id === 63
        case 'delete':
          return p.etiStatementD
      }
      break
    case 'serviceRecordBook':
      switch (typeDocument) {
        case 'create':
          return p.existServiceRecordBookC || p.newServiceRecordBookC
        case 'createExistDoc':
          return p.existServiceRecordBookC
        case 'createNewDoc':
          return p.newServiceRecordBookC
        case 'edit':
          return (p.serviceRecordBookPreVerificationW && sailorDocument.status.id === 74) ||
            (p.serviceRecordBookW && sailorDocument.status.id === 74)
        case 'editStatus':
          return (p.serviceRecordBookPreVerificationWS && sailorDocument.status.id === 74 && r.sailorPreVerification) ||
            (p.serviceRecordBookWS && (sailorDocument.status.id === 34 || (r.editableByAgent && sailorDocument.status.id === 74))) ||
            (p.postVerificationW && sailorDocument.status.id === 60)
        case 'files':
          return true
        case 'delete':
          return p.serviceRecordBookD && r.agent && sailorDocument.status.id === 74
        case 'deleteFile':
          return p.serviceRecordBookD && ((r.agent && sailorDocument.status.id === 74 && !photo.isDeleted) || (r.backOffice && photo.isDeleted))
        case 'preVerification':
          return !p.serviceRecordBookPreVerificationWS && !r.sailorPreVerification && sailorDocument.status.id !== 74
        case 'addRecord':
          return (p.recordBookLineC && (sailorDocument.status.id === 2 || sailorDocument.status.id === 34 || sailorDocument.status.id === 74))
        case 'verificationSteps':
          return p.serviceRecordBookWS
      }
      break
    case 'serviceRecordBookLine':
      switch (typeDocument) {
        case 'edit':
          return (p.experiencePreVerificationW && sailorDocument.status_line.id === 74) ||
            (p.recordBookLineW && (sailorDocument.status_line.id === 74 || sailorDocument.status_line.id === 14))
        case 'editStatus':
          return (p.experiencePreVerificationWS && sailorDocument.status_line.id === 74 && r.sailorPreVerification) ||
            (p.recordBookLineWS && sailorDocument.status_line.id === 34) ||
            (r.editableByAgent && sailorDocument.status_line.id === 74) ||
            (p.postVerificationW && (sailorDocument.status_line.id === 60 || sailorDocument.status_line.id === 9)) ||
            (r.userID === 188 && (sailorDocument.status_line.id === 34 || sailorDocument.status_line.id === 10))
        case 'files':
          return true
        case 'delete':
          return p.recordBookLineD && r.agent && sailorDocument.status_line.id === 74
        case 'deleteFile':
          return p.recordBookLineD && ((r.agent && sailorDocument.status_line.id === 74 && !photo.isDeleted) || (r.backOffice && photo.isDeleted))
        case 'preVerification':
          return !p.experiencePreVerificationWS && !r.sailorPreVerification && sailorDocument.status_line.id !== 74
        case 'verificationSteps':
          return p.recordBookLineWS || r.userID === 188
      }
      break
    case 'experience':
      switch (typeDocument) {
        case 'create':
          return p.experienceC || p.experienceNotConventionalC
        case 'edit':
          return (p.experiencePreVerificationW || p.recordBookLineW || p.experienceW || p.experienceNotConventionalW) &&
            sailorDocument.status_line.id === 74
        case 'editStatus':
          return (p.experiencePreVerificationWS && sailorDocument.status_line.id === 74 && r.sailorPreVerification) ||
            ((p.experienceWS || p.recordBookLineWS || p.experienceNotConventionalWS) &&
              (sailorDocument.status_line.id === 34 || (r.editableByAgent && sailorDocument.status_line.id === 74))) ||
            (p.postVerificationW && (sailorDocument.status_line.id === 60 || sailorDocument.status_line.id === 9))
        case 'files':
          return true
        case 'delete':
          return p.experienceD && r.agent && sailorDocument.status_line.id === 74
        case 'deleteFile':
          return p.experienceD && ((r.agent && sailorDocument.status_line.id === 74 && !photo.isDeleted) || (r.backOffice && photo.isDeleted))
        case 'preVerification':
          return !p.experiencePreVerificationWS && !r.sailorPreVerification && sailorDocument.status_line.id !== 74
        case 'checkDocumentType':
          return p.experienceC
        case 'verificationSteps':
          return p.experienceWS || p.recordBookLineWS || p.experienceNotConventionalWS
      }
      break
    case 'recordBookStatement':
      switch (typeDocument) {
        case 'create':
          return true
        case 'edit':
          return (sailorDocument.status_document.id !== 12 && sailorDocument.status_document.id !== 47) || (sailorDocument.status_document.id === 87 && r.medical)
        case 'files':
          return true
        case 'delete':
          return p.serviceRecordBookStatementD
        case 'deleteFile':
          return p.serviceRecordBookStatementD && (!photo.isDeleted || (r.backOffice && photo.isDeleted))
        case 'transfer':
          return p.serviceRecordBookStatementW && sailorDocument.is_payed && sailorDocument.status_document.id !== 47
        case 'changeStatusToRejected':
          return p.serviceRecordBookStatementW && sailorDocument.status_document.id !== 49
      }
      break
    case 'sailorSQCStatement':
      switch (typeDocument) {
        case 'create':
          return p.sqcStatementC
        case 'edit':
          return p.sqcStatementC || (p.sqcStatementPreVerificationW &&
              (sailorDocument.status_document.id === 74 || sailorDocument.status_document.id === 24 || sailorDocument.status_document.id === 25))
        case 'editStatus':
          return ((p.sqcStatementWS && sailorDocument.status_dkk.have_all_docs && sailorDocument.is_payed) ||
            (r.secretarySQC && (sailorDocument.status_document.id === 42 || sailorDocument.status_document.id === 25))) ||
            (p.sqcStatementCadetWS && (sailorDocument.status_document.id === 25 || sailorDocument.status_document.id === 42) &&
              sailorDocument.status_dkk.not_have_educ_doc && sailorDocument.is_cadet) ||
            (p.sqcStatementPaymentW && sailorDocument.status_dkk.have_all_docs) ||
            (p.sqcStatementPreVerificationWS && sailorDocument.status_document.id === 74) ||
            (sailorDocument.status_document.id === 87 && r.marad && sailorDocument.status_dkk.have_all_docs) ||
            p.sqcStatementRejectedWS
        case 'files':
          return true
        case 'delete':
          return p.sqcStatementD && r.agent && sailorDocument.status_document.id === 74
        case 'deleteFile':
          return p.sqcStatementD && ((r.agent && sailorDocument.status_document.id === 74 && !photo.isDeleted) || (r.backOffice && photo.isDeleted))
        case 'regeneration':
          return r.backOffice && sailorDocument.has_related_docs
        case 'showPayment':
          return p.sqcStatementPaymentW && sailorDocument.status_dkk.have_all_docs && sailorDocument.status_document.id !== 74
        case 'showStudentStatuses':
          return p.sqcStatementCadetWS && (sailorDocument.status_document.id === 25 || sailorDocument.status_document.id === 42) &&
            sailorDocument.status_dkk.not_have_educ_doc && sailorDocument.is_cadet
        case 'showStatuses':
          return p.sqcStatementWS && sailorDocument.status_dkk.have_all_docs && sailorDocument.status_document.id !== 74
        case 'requiredFile':
          return sailorDocument.status_document.id === 87 && r.marad
        case 'showSuccessButton':
          return (p.sqcStatementPaymentW && sailorDocument.status_dkk.have_all_docs && sailorDocument.status_document.id !== 74) ||
            (p.sqcStatementCadetWS && (sailorDocument.status_document.id === 25 || sailorDocument.status_document.id === 42) &&
              sailorDocument.status_dkk.not_have_educ_doc && sailorDocument.is_cadet) ||
            (p.sqcStatementWS && sailorDocument.status_dkk.have_all_docs && sailorDocument.status_document.id !== 74) ||
            ((p.sqcStatementPreVerificationWS && r.sailorPreVerification && sailorDocument.status_document.id === 74) ||
              (sailorDocument.status_document.id === 87 && r.marad))
        case 'showRejectButton':
          return r.secretarySQC && (sailorDocument.status_document.id === 42 || sailorDocument.status_document.id === 25) && !sailorDocument.is_agent_create
        case 'showSaveLabel':
          return !(p.sqcStatementPreVerificationWS && r.sailorPreVerification && sailorDocument.status_document.id === 74) ||
            !(sailorDocument.status_document.id === 87 && r.marad)
        case 'preVerification':
          return (p.sqcStatementPreVerificationWS && r.sailorPreVerification && sailorDocument.status_document.id === 74) ||
            (sailorDocument.status_document.id === 87 && r.marad)
      }
      break
    case 'sailorSQCProtocols':
      switch (typeDocument) {
        case 'create':
          return p.sqcProtocolC
        case 'edit':
          return p.superAdmin
        case 'editStatus':
          return p.sqcProtocolWS && sailorDocument.decision
        case 'files':
          return p.sqcProtocolW
        case 'delete':
          return p.sqcProtocolD
        case 'deleteFile':
          return p.sqcProtocolD && (!photo.isDeleted || (r.backOffice && photo.isDeleted))
        case 'regeneration':
          return p.sqcProtocolRegenerationW && sailorDocument.is_printeble && sailorDocument.decision
        case 'signature':
          return !sailorDocument.signing.sign_status && (sailorDocument.signing.sign_access || p.sqcProtocolStampW)
      }
      break
    case 'sailorSQCWishes':
      switch (typeDocument) {
        case 'create':
          return p.sqcWishesC
        case 'update':
          return p.sqcWishesU
        case 'transfer':
          return p.sqcWishesT && sailorDocument.status_document.id === 43
        case 'delete':
          return p.sqcWishesD
      }
      break
    case 'sailorMedical':
      switch (typeDocument) {
        case 'create':
          return p.medicalC
        case 'edit':
          return (p.medicalPreVerificationW && sailorDocument.status_document.id === 74) || (((p.medicalW && p.sailorDocument !== 37) ||
            (p.medicalW && p.sailorDocument === 37 && r.sailorIsSQC === false) || r.medical) && sailorDocument.status_document.id === 74)
        case 'editStatus':
          return (p.medicalPreVerificationWS && sailorDocument.status_document.id === 74 && r.sailorPreVerification) ||
            (p.medicalWS && (sailorDocument.status_document.id === 34 ||
              (r.editableByAgent && sailorDocument.status_document.id === 74)) && !r.medical) ||
            (r.medical && sailorDocument.status_document.id === 77) ||
            (p.postVerificationW && sailorDocument.status_document.id === 60)
        case 'files':
          return true
        case 'delete':
          return p.medicalD && r.agent && sailorDocument.status_document.id === 74
        case 'deleteFile':
          return p.medicalD && ((r.agent && sailorDocument.status_document.id === 74 && !photo.isDeleted) || (r.backOffice && photo.isDeleted))
        case 'preVerification':
          return !p.medicalPreVerificationWS && !r.sailorPreVerification && sailorDocument.status_document.id !== 74
        case 'verificationSteps':
          return p.medicalWS && !r.medical
      }
      break
    case 'medicalStatement':
      switch (typeDocument) {
        case 'create':
          return p.medicalStatementC
        case 'edit':
          return p.medicalStatementW && (sailorDocument.status_document.id === 77 || sailorDocument.status_document.id === 42)
        case 'editStatus':
          return (p.medicalStatementWS && (sailorDocument.status_document.id === 77 || sailorDocument.status_document.id === 42)) ||
            (r.medical && sailorDocument.status_document.id === 77)
        case 'transfer':
          return (p.medicalStatementT && sailorDocument.status_document.id === 75 && sailorDocument.is_payed) ||
            (r.medical && sailorDocument.status_document.id === 75 && sailorDocument.is_payed)
        case 'files':
          return true
        case 'delete':
          return p.medicalStatementD
        case 'deleteFile':
          return p.medicalStatementD && ((r.agent && sailorDocument.status_document.id === 74 && !photo.isDeleted) || (r.backOffice && photo.isDeleted))
        case 'enterDoctor':
          return !r.medical
      }
      break
    case 'positionStatement':
      switch (typeDocument) {
        case 'create':
          return (p.packetServiceC && (r.agent || r.backOffice || r.marad)) || r.secretaryService
        case 'createAfterPreview':
          return !r.secretaryService
        case 'createSingleDocs':
          return !r.marad || !r.secretaryService
        case 'edit':
          return p.packetServiceW && (r.agent || r.backOffice || r.marad) && !sailorDocument.is_payed
        case 'files':
          return true
        case 'delete':
          return p.packetServiceD && (r.agent || r.backOffice || r.marad)
        case 'deleteFile':
          return p.packetServiceD && ((r.agent && !photo.isDeleted) || (r.backOffice && photo.isDeleted))
        case 'changeRating':
          return sailorDocument.is_payed && ((r.agent && r.sailorRating !== 4) || (r.backOffice && p.ratingW))
      }
      break
    case 'newAgents':
      switch (typeDocument) {
        case 'edit':
          return p.newAgentsStatementsW
        case 'editStatus':
          return p.newAgentsStatementsW
        case 'files':
          return true
      }
      break
    case 'agentStatements':
      switch (typeDocument) {
        case 'sailorLink':
          return (r.agent || r.secretaryService) && sailorDocument.status_document.id === 67
        case 'edit':
          return (p.agentStatementW && sailorDocument.status_document.id === 69) ||
            (p.agentStatementA && sailorDocument.status_document.id === 82) ||
            (r.secretaryService && !sailorDocument.date_end_proxy)
        case 'files':
          return true
        case 'showAgentName':
          return !r.marad
        case 'highlightDocument': // highlight document without termination date
          return r.secretaryService
      }
      break
    case 'agentDocuments':
      switch (typeDocument) {
        case 'sailorLink':
          return true
        case 'edit':
          return false
        case 'files':
          return false
      }
      break
    case 'backOfficeCoefficient':
      switch (typeDocument) {
        case 'create':
        case 'edit':
        case 'delete':
          return p.etiRatioW
      }
      break
    case 'backOfficeCoursePrice':
      switch (typeDocument) {
        case 'create':
        case 'edit':
        case 'delete':
          return p.p.etiCoursePriceW
      }
      break
    case 'backOfficeETIList':
      switch (typeDocument) {
        case 'create':
          return p.backOfficeETIListC
        case 'edit':
          return p.backOfficeETIListW
      }
      break
    case 'backOfficeCourse':
      switch (typeDocument) {
        case 'create':
          return p.etiCourseListC
      }
      break
    case 'backOfficeCourseLine':
      switch (typeDocument) {
        case 'edit':
          return p.etiCourseListW
        case 'delete':
          return p.etiCourseListD
      }
      break
    case 'backOfficeDocumentPrices':
      switch (typeDocument) {
        case 'create':
          return p.backOfficeDocumentsPriceW
        case 'edit':
          return false
      }
      break
    case 'backOfficeFutureDocumentPrices':
      switch (typeDocument) {
        case 'edit':
        case 'delete':
          return p.backOfficeDocumentsPriceW
      }
      break
    case 'backOfficePastDocumentPrices':
      switch (typeDocument) {
        case 'edit':
          return p.backOfficeDocumentsPriceW && sailorDocument.allowEdit
        case 'delete':
          return p.backOfficeDocumentsPriceW && sailorDocument.allowDelete
      }
      break
    case 'backOfficeDealing':
      switch (typeDocument) {
        case 'edit':
          return p.backOfficeDealingW
        case 'delete':
          return false
      }
      break
    case 'backOfficeAgentGroups':
      switch (typeDocument) {
        case 'edit':
          return true
        case 'delete':
          return false
        case 'editGroup':
          return !r.headAgent
      }
      break
  }
}
