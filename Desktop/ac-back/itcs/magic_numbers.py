# айдишники статусов "имеет належну квалификацию" и "не умеет належной квалификации"

reject_qualification = 3  # не мае квалификации
allow_qualification = 28  # мае квалификацию

#  айдишники должностей(position) танкеристов
tankers_position = (181, 182, 183, 184, 185)

# решение протокола дкк
decision_allow = 1
decision_reject = 2

# статус отсуствия документов или опыта в заявках на дкк или заявках на дкк
# все статусы заявок на дкк и квалификационные дкоументы
status_state_qual_dkk_absense = 16
status_state_qual_dkk_approv = 24
status_state_qual_dkk_in_process = 25
status_state_qual_dkk_rejected = 23
status_state_qual_dkk_student = 58
status_state_qual_dkk_canceled = 73

# статусы квалификационных документов и нтз
status_qual_doc_in_proccess = 21
status_qual_doc_invalid = 20
status_qual_doc_valid = 19
status_qual_doc_lost = 18
status_qual_doc_destroyed = 17
status_qual_doc_expired = 7
status_qual_doc_canceled = 33

# типы документов(кроме подтверждения к диплому) у которых кончается срок действия
qual_documents_with_end_date = (89, 88, 86, 85, 57, 21)

celery_user_id = 13
ntz_user_id = 16

# статусы ПКМ
status_service_record_lost = 1
status_service_record_valid = 2
status_service_record_destroyed = 6
status_service_record_invalid = 13
status_service_record_in_process = 14
STATUS_SERVICE_RECORD_CANCELED = 89

VERIFICATION_STATUS = 34

CLEAR_USER = 161

status_statement_to_per_cabinet_approv = 41

# статусы "хотелки" моряка на ДКК (demand_position)
status_demand_pos_all_enough = 43
status_demand_pos_not_documents = 44
status_demand_pos_not_experience = 45
status_demand_pos_all_not_enough = 46

# статусы заявки на ПКМ
status_statement_serv_rec_created = 47
status_statement_serv_rec_in_process = 48
status_statement_serv_rec_rejected = 49

CREATED_FROM_PERSONAL_CABINET = 42

AST_USER_ID = 337

# статусы протоколов ДКК
status_protocol_dkk_valid = 29
status_protocol_dkk_canceled = 30
status_protocol_dkk_lost = 31
status_protocol_dkk_destroyed = 32
status_protocol_dkk_expired = 54

# статусы студентческих билетов
status_student_id_valid = 55
status_student_id_invalid = 56
status_student_id_expired = 57

# статус для заявлений дкк поданных кадетами
status_cadets_state_dkk_allowed = 58

STATUS_TO_ADDITIONAL_VERIFICATION = 60

ALL_VALID_STATUSES = [2, 9, 19, 24, 29, 39, 41, 55, 61, 64, 67, 70, 75, 89]

# статусы для заявлений на прохождение курсов в НТЗ
status_statement_eti_valid = 61
status_statement_eti_invalid = 62
status_statement_eti_in_process = 63
status_statement_eti_document_created = 85

# статусы для заявлений на агентов
status_statement_agent_valid = 64
status_statement_agent_invalid = 65
status_statement_agent_in_process = 66

# статусы для заявлений на агентов
status_statement_agent_sailor_valid = 67
status_statement_agent_sailor_invalid = 68
status_statement_agent_sailor_in_process = 69
status_statement_agent_sailor_wait_secretary = 82
status_statement_agent_sailor_wait_sailor = 83

# статусы для заявлений на ПОМ
status_statement_sailor_passport_valid = 70
status_statement_sailor_passport_invalid = 71
status_statement_sailor_passport_in_process = 72

# статусы Back Office
STATUS_CREATED_BY_AGENT = 74

# статусы для заявления мед свидетельства
status_statement_medical_cert_valid = 75
status_statement_medical_cert_invalid = 76
status_statement_medical_cert_in_process = 77
STATUS_STATEMENT_MEDICAL_CERT_CREATED = 81
# статусы для заявления на повышение квалификации
status_statement_adv_training_valid = 78
status_statement_adv_training_invalid = 79
status_statement_adv_training_in_process = 80
# статус Анулировано для оплаченных заявлений при удалении пакета
status_statement_canceled = 84

STATUS_REMOVED_DOCUMENT = 86

CREATED_FROM_MORRICHSERVICE = 87

SQC_WAIT_DECISION = 88
SQC_WAIT_SIGNATURES = 89


# ACCRUAL TYPES
class AccrualTypes:
    SQC_WITHOUT_EXPERIENCE = 2
    SQC_WITH_EXPERIENCE = 1
    QUALIFICATION = 3
    PROOF_OF_DIPLOMA = 4
    SAILOR_PASSPORT_GETTING_20 = 5
    SAILOR_PASSPORT_CONTINUE_20 = 6
    MEDICAL = 7
    ADVANCED_TRAINING = 8
    AGENT = 9
    SERVICE_CENTER = 10
    CERTIFICATE = 12
    SAILOR_PASSPORT_GETTING_7 = 14
    SAILOR_PASSPORT_CONTINUE_7 = 13
    BLANK_SERVICE_RECORD = 15
    MORRICHSERVICE = 16
    CADET_SQC = 17
    CADET_QUALIFICATION = 18
    CADET_PROOF_OF_DIPLOMA = 19
    CADET_AGENT = 20

    # Lists of acrrual
    LIST_SQC = (SQC_WITH_EXPERIENCE, SQC_WITHOUT_EXPERIENCE, CADET_SQC)
    LIST_QUALIFICATION = (QUALIFICATION, CADET_QUALIFICATION)
    LIST_PROOF = (PROOF_OF_DIPLOMA, CADET_PROOF_OF_DIPLOMA)
    LIST_SAILOR_PASSPORT = (SAILOR_PASSPORT_CONTINUE_7, SAILOR_PASSPORT_GETTING_7,
                            SAILOR_PASSPORT_GETTING_20, SAILOR_PASSPORT_CONTINUE_20)
    LIST_MEDICAL = (MEDICAL,)
    LIST_ADVANCED_TRAINING = (ADVANCED_TRAINING,)
    LIST_AGENT = (AGENT, CADET_AGENT)
    LIST_SERVICE_CENTER = (SERVICE_CENTER,)
    LIST_CERTIFICATE = (CERTIFICATE,)
    LIST_BLANK_SAILOR_PASSPORT = (BLANK_SERVICE_RECORD,)
    LIST_MORRICHSERVICE = (MORRICHSERVICE,)
