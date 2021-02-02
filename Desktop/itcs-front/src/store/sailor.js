import { api, getUpdatedObject, getProcessingStatus } from '@/mixins/api'
import { setRoles } from '@/mixins/permissions'

export const SAILOR = {
  state: () => ({
    sailorId: 0,
    rating: 0,
    sailorSQC: true,
    editableByAgent: false,
    agentInfo: false,
    sailorVerify: false,
    successStatement: [],
    availablePositions: [],
    availableRank: [],
    diplomas: [],
    protocols: [],
    successQualificationStatement: [],
    sailorPassportProcessing: [],
    // Sailor documents
    sailorInfo: {},
    sailorPassport: [],
    sailorFullNameChanges: [],
    sailorPassportStatement: [],
    education: [],
    student: [],
    educationStatement: [],
    qualification: [],
    qualificationStatement: [],
    certification: [],
    certificationStatement: [],
    serviceRecordBook: [],
    serviceRecordBookLine: [],
    experience: [],
    recordBookStatement: [],
    sailorSQCStatement: [],
    sailorSQCProtocols: [],
    sailorSQCWishes: [],
    sailorMedical: [],
    medicalStatement: [],
    positionStatement: [],
    backOfficeETIList: [],
    backOfficeCoefficient: [],
    backOfficeCoursePrice: [],
    backOfficeDealing: [],
    newAgents: [],
    newAccounts: [],
    approvedSailorPassportStatements: [],
    existSailorPassports: []
  }),
  mutations: {
    setSailorId (state, data) {
      state.sailorId = data
    },
    setRating (state, value) {
      state.rating = value
    },
    setStateData (state, data) {
      state[data.type] = []
      state[data.type] = data.data
    },
    setAvailablePositions (state, data) {
      const availableRankArray = state.ranks.filter(value => {
        for (const rankId of data.rank) {
          if (rankId === value.id) return value
        }
      })

      const availablePositionsArray = state.positions.filter(value => {
        for (const positionId of data.position) {
          if (positionId === value.id) return value
        }
      })

      state.availableRank = availableRankArray
      state.availablePositions = availablePositionsArray
    },
    addSuccessQualificationStatement (state, data) {
      let record = state.successQualificationStatement.find(record => record.id === data.id)
      if (!record) {
        data = updateStatementObj(data)
        state.successQualificationStatement.push(data)
      }
    },
    addDataSailor (state, data) {
      const updatedObject = getUpdatedObject(data)
      state[data.type].push(updatedObject.value)
    },
    updateDataSailor (state, data) {
      const updatedObject = getUpdatedObject(data)
      const newArray = state[updatedObject.type].filter(item => item.id !== updatedObject.value.id)
      newArray.push(updatedObject.value)
      state[updatedObject.type] = newArray
    },
    deleteDataSailor (state, data) {
      state[data.type] = state[data.type].filter(item => item.id !== data.value.id)
    }
  },
  actions: {
    async getSailorInformation ({ commit }, id) {
      await api.get(`api/v2/sailor/${id}/`).then(response => {
        if (response.code === 200) {
          commit('setStateData', { type: 'sailorVerify', data: response.data.can_verify })
          commit('setStateData', { type: 'agentInfo', data: response.data.has_agent })
          commit('setStateData', { type: 'sailorSQC', data: response.data.is_dkk })
          commit('setStateData', { type: 'editableByAgent', data: response.data.can_verify })
          setRoles()

          response.data.phoneList = []
          response.data.email = ''
          try {
            response.data.contact_info.forEach(item => {
              if (item.type_contact === 'phone_number') {
                response.data.phoneList.push(item.value)
              } else if (item.type_contact === 'email') {
                response.data.email += item.value + ';'
              }
            })
            response.data.phoneNumber = null // response.data.phoneList[0]
          } catch (e) {}
          commit('setStateData', { type: 'sailorInfo', data: response.data })
        }
      })
    },
    async getRating ({ commit }, id) {
      let rating = await api.get(`api/v2/sailor/${id}/rating/`)
      commit('setRating', rating.data.rating)
    },
    async getSuccessStatementsSQC ({ commit }, id) {
      await api.get(`api/v2/sailor/${id}/statement/protocol_sqc/success/`).then(response => {
        commit('setStateData', { type: 'successStatement', data: response.data })
      })
    },
    async getAvailablePositions ({ commit }, sailorId) {
      await api.get(`api/v2/sailor/${sailorId}/available_position/`).then(response => {
        commit('setAvailablePositions', response.data)
      })
    },
    async getDiplomas ({ commit }, id) {
      await api.get(`api/v2/sailor/${id}/qualification/diploma_for_proof/`).then(response => {
        response.data.map(value => {
          value.name_ukr = `${value.number} ${value.rank.name_ukr} (${value.status_document.name_ukr})`
          value.name_eng = `${value.number} ${value.rank.name_eng} (${value.status_document.name_eng})`
          value.rank_id = value.rank.id
        })
        commit('setStateData', {
          type: 'diplomas',
          data: response.data
        })
      })
    },
    async getProtocolsForQualification ({ commit }, id) {
      await api.get(`api/v2/sailor/${id}/protocol_sqc/success/`).then(response => {
        response.data.map(value => {
          value.list_positions = value.position
          return updateStatementObj(value)
        })
        commit('setStateData', { type: 'protocols', data: response.data })
      })
    },
    async getSuccessQualificationStatement ({ commit }, id) {
      await api.get(`api/v2/sailor/${id}/statement/qualification/success/`).then(response => {
        response.data.map(value => {
          return updateStatementObj(value)
        })
        commit('setStateData', { type: 'successQualificationStatement', data: response.data })
      })
    },
    async getSailorPassportProcessing ({ commit }, id) {
      await api.get(`api/v2/sailor/${id}/sailor_passport/choice/`).then(response => {
        commit('setStateData', {
          type: 'sailorPassportProcessing',
          data: response.data
        })
      })
    },

    async getSailorPassport ({ commit }, id) {
      await api.get(`api/v2/sailor/${id}/sailor_passport/`).then(response => {
        if (response.status === 'success') {
          response.data.map((item) => {
            item.behavior = { viewInfoBlock: true }
          })
          commit('setStateData', { type: 'sailorPassport', data: response.data })
        }
      })
    },

    async getFullNameChanges ({ commit }, id) {
      await api.get(`api/v2/sailor/${id}/old_name/`).then(response => {
        if (response.status === 'success') {
          response.data.map((item, index) => {
            item.behavior = { viewInfoBlock: true }
            item.lastRecord = index === 0 // 0 position of array is always last record
          })
          commit('setStateData', { type: 'sailorFullNameChanges', data: response.data })
        }
      })
    },

    async getSailorPassportStatements ({ commit }, id) {
      await api.get(`api/v2/sailor/${id}/statement/sailor_passport/`).then(response => {
        if (response.status === 'success') {
          response.data.map(item => {
            item.behavior = { viewInfoBlock: true }
            item.processingStatus = getProcessingStatus(item.type_receipt)
          })
          commit('setStateData', { type: 'sailorPassportStatement', data: response.data })
        }
      })
    },

    async getEducationDocs ({ commit }, id) {
      await api.get(`api/v2/sailor/${id}/education/`).then(response => {
        if (response.status === 'success') {
          response.data.map((item) => {
            item.behavior = { viewInfoBlock: true }
            if (item.type_document.id === 1 || item.type_document.id === 2) {
              item.experied_date = '-'
            }
            item.allowMerge = response.data.filter(val => val.number_document === item.number_document).length > 1
          })
          commit('setStateData', { type: 'education', data: response.data })
        }
      })
    },

    async getStudentCard ({ commit }, id) {
      await api.get(`api/v1/cadets/students_id_per_sailor/${id}/`).then(response => {
        if (response.code === 200) {
          response.data.map((item) => {
            item.behavior = { viewInfoBlock: true }
          })
          commit('setStateData', { type: 'student', data: response.data })
        }
      })
    },

    async getGraduationStatements ({ commit }, id) {
      await api.get(`api/v2/sailor/${id}/statement/advanced_training/`).then(response => {
        if (response.status === 'success') {
          response.data.map(item => {
            item.behavior = { viewInfoBlock: true }
          })
          commit('setStateData', { type: 'educationStatement', data: response.data })
        }
      })
    },

    async getQualificationDocuments ({ commit }, id) {
      let items = []
      await api.get(`api/v2/sailor/${id}/qualification/`).then(response => {
        if (response.status === 'success') {
          response.data.map(item => {
            item.behavior = { viewInfoBlock: true }
            item.allowMerge = response.data.filter(val => val.number === item.number).length > 1
          })
          items = response.data
          api.get(`api/v2/sailor/${id}/proof_diploma/`).then(response => {
            if (response.status === 'success') {
              response.data.map(item => {
                item.behavior = { viewInfoBlock: true }
                item.number = item.number_document
                item.allowMerge = response.data.filter(val => val.number_document === item.number_document).length > 1

                let diplomaIndex = items.findIndex(value => value.id === item.diploma)
                items.splice(diplomaIndex + 1, 0, item)
              })
              commit('setStateData', { type: 'qualification', data: items })
            }
          })
        }
      })
    },

    async getQualificationStatements ({ commit }, id) {
      await api.get(`api/v2/sailor/${id}/statement/qualification/`).then(response => {
        if (response.code === 200) {
          response.data.map(item => {
            item.behavior = { viewInfoBlock: true }
          })
          commit('setStateData', { type: 'qualificationStatement', data: response.data })
        }
      })
    },

    async getCertificates ({ commit }, id) {
      await api.get(`api/v2/sailor/${id}/certificate/`).then(response => {
        if (response.code === 200) {
          response.data.map(item => {
            item.behavior = { viewInfoBlock: true }
          })
          const items = response.data.filter(val => val.ntz && val.course_traning)
          commit('setStateData', { type: 'certification', data: items })
        }
      })
    },

    async getCertificateStatements ({ commit }, id) {
      await api.get(`api/v2/sailor/${id}/statement/certificate/`).then((response) => {
        if (response.code === 200) {
          response.data.map(item => {
            item.behavior = { viewInfoBlock: true }
          })
          commit('setStateData', { type: 'certificationStatement', data: response.data })
        }
      })
    },

    async getRecordBooks ({ commit }, id) {
      await api.get(`api/v2/sailor/${id}/service_record/`).then(response => {
        if (response.status === 'success') {
          response.data.map(item => {
            item.behavior = { viewInfoBlock: true }
          })
          commit('setStateData', { type: 'serviceRecordBook', data: response.data })
        }
      })
    },

    async getRecordBookLineEntry ({ commit }, data) {
      await api.get(`api/v2/sailor/${data.id}/service_record/${data.service_book}/line/`).then(response => {
        if (response.status === 'success') {
          response.data.map(item => {
            item.behavior = { viewInfoBlock: true }
            item.list_responsibilities = item.all_responsibility
              .filter(resp => resp.responsibility)
          })
          commit('setStateData', { type: 'serviceRecordBookLine', data: response.data })
        }
      })
    },

    async getExperienceReferences ({ commit }, id) {
      await api.get(`api/v2/sailor/${id}/experience_certificate/`).then(response => {
        if (response.status === 'success') {
          response.data.map(item => {
            item.behavior = { viewInfoBlock: true }
            item.list_responsibilities = item.all_responsibility.filter(resp => resp.responsibility)
          })
          commit('setStateData', { type: 'experience', data: response.data })
        }
      })
    },

    async getRecordBookStatement ({ commit }, id) {
      await api.get(`api/v2/sailor/${id}/statement/service_record/`).then(response => {
        if (response.status === 'success') {
          response.data.map(item => {
            item.behavior = { viewInfoBlock: true }
          })
          commit('setStateData', { type: 'recordBookStatement', data: response.data })
        }
      })
    },

    async getSQCStatements ({ commit }, id) {
      await api.get(`api/v2/sailor/${id}/statement/protocol_sqc/`).then(response => {
        this.tableLoader = false
        if (response.status === 'success') {
          response.data.map((item) => {
            item.behavior = { viewInfoBlock: true }
          })
          commit('setStateData', { type: 'sailorSQCStatement', data: response.data })
        }
      })
    },

    async getProtocolsSQC ({ commit }, id) {
      await api.get(`api/v2/sailor/${id}/protocol_sqc/`).then(response => {
        if (response.status === 'success') {
          response.data.map(item => {
            item.behavior = { viewInfoBlock: true }
            item.list_positions = item.position
            item.membersCommission = item.commissioner_sign.filter(value => value.commissioner_type === 'CH') // .map(value => value.user_fio_ukr)
            item.headCommission = item.commissioner_sign.find(value => value.commissioner_type === 'HD')
            item.secretaryCommission = item.commissioner_sign.find(value => value.commissioner_type === 'SC')
          })
          commit('setStateData', { type: 'sailorSQCProtocols', data: response.data })
        }
      })
    },

    async getWishesSQC ({ commit }, id) {
      await api.get(`api/v2/sailor/${id}/demand/`).then(response => {
        if (response.status === 'success') {
          response.data.map(item => {
            item.behavior = { viewInfoBlock: true }
          })
          commit('setStateData', { type: 'sailorSQCWishes', data: response.data })
        }
      })
    },

    async getMedicalCertificates ({ commit }, id) {
      await api.get(`api/v2/sailor/${id}/medical/`).then(response => {
        if (response.status === 'success') {
          response.data.map(item => {
            item.behavior = { viewInfoBlock: true }
          })
          commit('setStateData', { type: 'sailorMedical', data: response.data })
        }
      })
    },

    async getMedicalStatements ({ commit }, id) {
      await api.get(`api/v2/sailor/${id}/statement/medical_certificate/`).then(response => {
        if (response.status === 'success') {
          response.data.map(item => {
            item.behavior = { viewInfoBlock: true }
          })
          commit('setStateData', { type: 'medicalStatement', data: response.data })
        }
      })
    },

    async getPositionStatements ({ commit }, id) {
      await api.get(`api/v1/back_off/packet/sailor/${id}/`).then(response => {
        if (response.status === 'success') {
          response.data.map(item => {
            item.behavior = { viewInfoBlock: true }
            item.list_positions = item.position
            item.includeSailorPass = getProcessingStatus(item.include_sailor_passport)
          })
          commit('setStateData', { type: 'positionStatement', data: response.data })
        }
      })
    },

    async getETICertificationInstitutions ({ commit }) {
      await api.get('api/v1/back_off/certificates/institution/').then(response => {
        if (response.status === 'success') {
          response.data.map(item => {
            item.behavior = { viewInfoBlock: true }
          })
          commit('setStateData', { type: 'backOfficeETIList', data: response.data })
        }
      })
    },

    async getBackOfficeCoefficients ({ commit }) {
      await api.get('api/v1/back_off/eti_profit_part/').then(response => {
        if (response.code === 200) {
          response.data.map(item => {
            item.behavior = { viewInfoBlock: true }
            item.allowChange = new Date(item.date_start) > new Date()
          })
          commit('setStateData', { type: 'backOfficeCoefficient', data: response.data })
        }
      })
    },

    async getBackOfficeCoursePrices ({ commit }) {
      await api.get('api/v1/back_off/course_price/').then(response => {
        if (response.code === 200) {
          response.data.map((item) => {
            item.behavior = { viewInfoBlock: true }
            item.allowDelete = new Date(item.date_start) > new Date()
            // condition for actual value below
            item.allowEdit = !((!item.date_end || new Date(item.date_end) >= new Date()) && new Date(item.date_start) <= new Date())
          })
          commit('setStateData', { type: 'backOfficeCoursePrice', data: response.data })
        }
      })
    },

    async getBackOfficeDealing ({ commit }) {
      await api.get('api/v1/back_off/certificates/month_ratio/').then(response => {
        if (response.code === 200) {
          response.data.map(item => {
            item.behavior = { viewInfoBlock: true }
          })
          commit('setStateData', { type: 'backOfficeDealing', data: response.data })
        }
      })
    },

    async getBecomingAgentStatements ({ commit }) {
      await api.get('api/v1/seaman/statement_seaman/').then(response => {
        if (response.status === 'success') {
          response.data.map(item => {
            item.behavior = { viewInfoBlock: true }
          })
          commit('setStateData', { type: 'newAgents', data: response.data })
        }
      })
    },

    async getNewAccountsList ({ commit }, link) {
      const url = link || 'api/v1/sms_auth/list_verification/?page_size=20'
      await api.get(url).then(response => {
        if (response.code === 200) {
          response.data.results.map(item => {
            item.behavior = { viewInfoBlock: true }
            item.sailorDateBirth = null
          })
          commit('setStateData', { type: 'newAccounts', data: response.data })
        }
      })
    },

    async getApprovedSailorPassportStatements ({ commit }, id) {
      await api.get(`api/v2/sailor/${id}/statement/sailor_passport/success/`).then(response => {
        if (response.code === 200) {
          response.data.map(item => {
            item.fullName = `${item.number} - ${item.port ? item.port.name_ukr : item.other_port}`
          })
          commit('setStateData', { type: 'approvedSailorPassportStatements', data: response.data })
        }
      })
    },

    async getExistSailorPassports ({ commit }, id) {
      await api.get(`api/v2/sailor/${id}/sailor_passport/allowed_to_continue/`).then(response => {
        if (response.code === 200) {
          response.data.map(item => {
            item.fullName = `${item.number_document} - ${item.port ? item.port.name_ukr : item.other_port}`
          })
          commit('setStateData', { type: 'existSailorPassports', data: response.data })
        }
      })
    }
  },
  getters: {
    sailorID (state) {
      return state.sailorId
    },
    diplomasForQualificationDocs: state => state.diplomas.filter(record => record.type_document.id === 49 || record.type_document.id === 1),
    diplomasByRank: state => rankId => state.diplomas.filter(diploma => diploma.rank_id === rankId),
    validSailorPassportProcessing: state => state.sailorPassportProcessing.filter(choice => choice.id !== 0),
    availablePositionsById: state => id => state.availablePositions.filter(position => position.rank === id),
    sailorDocumentByID: state => document => state[document.type].find(value => value.id === document.id),
    protocolsByRank: state => id => state.protocols.filter(protocol => protocol.rank_id === id),
    sailorIsCadet: state => state.student.filter(student => student.status_document.id === 55).length
  }
}

const updateStatementObj = (data) => {
  let positionUrk = []
  let positionEng = []
  data.list_positions.map(value => {
    positionUrk.push(value.name_ukr)
    positionEng.push(value.name_eng)
  })
  data.rank_id = data.rank.id
  data.name_ukr = `${data.number_document || data.number} ${positionUrk.join(', ')}`
  data.name_eng = `${data.number_document || data.number} ${positionEng.join(', ')}`

  if (data.hasOwnProperty('position')) {
    data.positionId = data.position.id
  }

  return data
}
