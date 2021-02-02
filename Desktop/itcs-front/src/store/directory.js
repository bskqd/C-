import { api } from '@/mixins/api'

export const DIRECTORY = {
  state: () => ({
    sex: [],
    positions: [],
    ranks: [],
    country: [],
    region: [],
    city: [],
    statuses: [],
    typeShip: [],
    modeShipping: [],
    typeGEU: [],
    ports: [],
    responsibility: [],
    positionsShip: [],
    typeDoc: [],
    typeDocQualification: [],
    extent: [],
    institution: [],
    profession: [],
    qualificationLevels: [],
    specialization: [],
    medInstitution: [],
    doctors: [],
    positionMedical: [],
    limitations: [
      {
        id: 1,
        name_ukr: 'Немає',
        name_eng: 'None'
      },
      {
        id: 2,
        name_ukr: 'Не дійсний для роботи в умовах тропічного клімату',
        name_eng: 'Not valid for use in tropical climates'
      },
      {
        id: 3,
        name_ukr: 'Необхідно використання окулярів або контактних лінз для виконання службових обов’язків',
        name_eng: 'You must use glasses or contact lenses to perform your duties'
      }
    ],
    affiliate: [],
    agents: [],
    commission: [],
    allCommissioners: [],
    paymentStatus: [
      { id: 1, status: true, name_ukr: 'Оплачено', name_eng: 'Paid' },
      { id: 2, status: false, name_ukr: 'Не оплачено', name_eng: 'No paid' }],
    educationTraining: [],
    courses: [],
    solutions: [],
    positionFunction: [],
    positionLimitation: [],
    userList: [],
    deliveryCities: [],
    faculties: [],
    educationForm: [],
    responsibilityWorkBook: [],
    allCertificatesETI: [],
    allAccrualTypeDoc: [],
    agentGroups: [],
    agentsList: [],
    filteredETI: {},
    registrationPermissionsList: []
  }),
  mutations: {
    setStateData (state, data) {
      state[data.type] = data.data
    },
    clearFilteredEtiList (state) {
      state.filteredETI = {}
    }
  },
  actions: {
    async getSex ({ commit }) {
      await api.get('api/v1/directory/sex/').then(response => {
        commit('setStateData', {
          type: 'sex',
          data: response.data
        })
      })
    },

    async getRanks ({ commit }) {
      await api.get('api/v1/directory/rank/').then(response => {
        commit('setStateData', {
          type: 'ranks',
          data: response.data
        })
      })
    },

    async getPositions ({ commit }) {
      await api.get('api/v1/directory/position/').then(response => {
        commit('setStateData', {
          type: 'positions',
          data: response.data
        })
      })
    },

    async getCountry ({ commit }) {
      await api.get('api/v1/directory/country/').then(response => {
        commit('setStateData', {
          type: 'country',
          data: response.data
        })
      })
    },

    async getRegion ({ commit }) {
      await api.get('api/v1/directory/region/').then(response => {
        commit('setStateData', {
          type: 'region',
          data: response.data
        })
      })

      // name: val.value,
      // name_eng: val.value_eng
    },

    async getCity ({ commit, state }, regionID) {
      state.city = []
      let params = new URLSearchParams({})
      if (regionID) params.set('region', regionID)

      api.get(`api/v1/directory/city/?${params}`).then(response => {
        commit('setStateData', {
          type: 'city',
          data: response.data
        })
      })

      // name: val.value,
      // name_eng: val.value_eng
    },

    async getStatusDocs ({ commit }) {
      await api.get('api/v1/directory/status_document/').then(response => {
        commit('setStateData', {
          type: 'statuses',
          data: response.data
        })
      })
    },

    async getTypeShip ({ commit }) {
      await api.get('api/v1/directory/type_vessel/').then(response => {
        commit('setStateData', {
          type: 'typeShip',
          data: response.data
        })
      })
    },

    async getModeShipping ({ commit }) {
      await api.get('api/v1/directory/mode_of_navigation/').then(response => {
        commit('setStateData', {
          type: 'modeShipping',
          data: response.data
        })
      })
    },

    async getTypeGEU ({ commit }) {
      await api.get('api/v1/directory/type_geu/').then(response => {
        commit('setStateData', {
          type: 'typeGEU',
          data: response.data
        })
      })
    },

    async getPorts ({ commit }) {
      await api.get('api/v1/directory/port/').then(response => {
        commit('setStateData', {
          type: 'ports',
          data: response.data
        })
      })
    },

    async getResponsibility ({ commit }) {
      await api.get('api/v1/directory/responsibility/').then(response => {
        commit('setStateData', {
          type: 'responsibility',
          data: response.data
        })
      })
    },

    async getPositionsOnShip ({ commit }) {
      await api.get('api/v1/directory/position_for_experience/').then(response => {
        commit('setStateData', {
          type: 'positionsShip',
          data: response.data
        })
      })
    },

    async getTypeDoc ({ commit }) {
      await api.get('api/v1/directory/type_document_nz/').then(response => {
        commit('setStateData', {
          type: 'typeDoc',
          data: response.data
        })
      })
    },

    async getTypeDocQual ({ commit }) {
      await api.get('api/v1/directory/type_document/').then(response => {
        commit('setStateData', {
          type: 'typeDocQualification',
          data: response.data
        })
      })
    },

    async getExtent ({ commit }) {
      await api.get('api/v1/directory/extent_nz/').then(response => {
        response.data.sort(function (a, b) {
          return (a.id - b.id)
        })
        commit('setStateData', {
          type: 'extent',
          data: response.data
        })
      })
    },

    async getNameInstitution ({ commit }) {
      await api.get('api/v1/directory/name_nz/').then(response => {
        commit('setStateData', {
          type: 'institution',
          data: response.data
        })
      })
    },

    async getProfession ({ commit }) {
      await api.get('api/v1/directory/speciality/').then(response => {
        commit('setStateData', {
          type: 'profession',
          data: response.data
        })
      })
    },

    async getQualification ({ commit }) {
      await api.get('api/v1/directory/level_qualification/').then(response => {
        commit('setStateData', {
          type: 'qualificationLevels',
          data: response.data
        })
      })
    },

    async getSpecialization ({ commit }) {
      await api.get('api/v1/directory/specialization/').then(response => {
        commit('setStateData', {
          type: 'specialization',
          data: response.data
        })
      })
    },

    async getMedicalInstitution ({ commit }) {
      await api.get('api/v1/directory/medical_institution/').then(response => {
        commit('setStateData', {
          type: 'medInstitution',
          data: response.data
        })
      })
    },

    async getDoctors ({ commit }) {
      await api.get('api/v1/directory/doctor_in_medical/').then(response => {
        commit('setStateData', {
          type: 'doctors',
          data: response.data
        })
      })
    },

    async getPositionForMedical ({ commit }) {
      await api.get('api/v1/directory/position_for_medical/').then(response => {
        commit('setStateData', {
          type: 'positionMedical',
          data: response.data
        })
      })
    },

    async getAffiliate ({ commit }) {
      await api.get('api/v1/directory/branch_office/').then(response => {
        commit('setStateData', {
          type: 'affiliate',
          data: response.data
        })
      })
    },

    async getAgents ({ commit }) {
      await api.get('api/v1/directory/auth_users/').then(response => {
        commit('setStateData', {
          type: 'agents',
          data: response.data
        })
      })
    },

    async getCommissioners ({ commit }) {
      await api.get('api/v1/directory/commisioner_for_committe/').then(response => {
        response.data = response.data.filter(value => value.name)
        response.data.map(value => {
          value.signer = value.id
          value.user_fio_ukr = value.name
        })
        commit('setStateData', {
          type: 'commission',
          data: response.data
        })
        commit('setStateData', {
          type: 'allCommissioners',
          data: response.data
        })
      })
    },

    async getETI ({ commit }) {
      await api.get('api/v1/directory/ntz/').then(response => {
        commit('setStateData', {
          type: 'educationTraining',
          data: response.data
        })
      })
    },

    async getCourses ({ commit }) {
      await api.get('api/v1/directory/course_for_ntz/').then(response => {
        commit('setStateData', {
          type: 'courses',
          data: response.data
        })
      })
    },

    async getSolutions ({ commit }) {
      await api.get('api/v1/directory/decision/').then(response => {
        commit('setStateData', {
          type: 'solutions',
          data: response.data
        })
      })
    },

    async getPositionsFunctions ({ commit }) {
      await api.get('api/v1/directory/functions_for_position/').then(response => {
        commit('setStateData', {
          type: 'positionFunction',
          data: response.data
        })
      })
    },

    async getPositionsLimitations ({ commit }) {
      await api.get('api/v1/directory/limitation/').then(response => {
        commit('setStateData', {
          type: 'positionLimitation',
          data: response.data
        })
      })
    },

    async getAllUsers ({ commit }) {
      await api.get('api/v1/auth/users/').then(response => {
        if (response.status === 'success') {
          response.data.map((item) => {
            item.userFullName = `${item.last_name} ${item.first_name} ${item.userprofile.middle_name || ''}`
          })
          commit('setStateData', { type: 'userList', data: response.data })
        }
      })
    },

    async getDeliveryCity ({ commit }) {
      await api.get('api/v1/delivery/novaposhta_city/').then(response => {
        commit('setStateData', {
          type: 'deliveryCities',
          data: response.data
        })
      })
    },

    async getFaculties ({ commit }) {
      await api.get('api/v1/directory/faculty/').then(response => {
        commit('setStateData', {
          type: 'faculties',
          data: response.data
        })
      })
    },

    async getEducationForm ({ commit }) {
      await api.get('api/v1/directory/education_form/').then(response => {
        commit('setStateData', {
          type: 'educationForm',
          data: response.data
        })
      })
    },

    async getResponsibilityWorkBook ({ commit }) {
      await api.get('api/v1/directory/responsibility_work_book/').then(response => {
        commit('setStateData', {
          type: 'responsibilityWorkBook',
          data: response.data
        })
      })
    },

    async getAllCommissioners ({ commit }) {
      await api.get('api/v1/directory/all_commissioners/').then(response => {
        console.log(response)
        commit('setStateData', {
          type: 'allCommissioners',
          data: response.data.commissioners
        })
      })
    },

    async getAllCertificatesETI ({ commit }) {
      await api.get('api/v1/directory/NTZ/').then(response => {
        commit('setStateData', {
          type: 'allCertificatesETI',
          data: response.data
        })
      })
    },

    async getAllAccrualTypeDoc ({ commit }) {
      await api.get('api/v1/directory/type_of_accrual_rules/').then(response => {
        commit('setStateData', {
          type: 'allAccrualTypeDoc',
          data: response.data
        })
      })
    },

    async getAgentGroups ({ commit }) {
      await api.get('api/v1/seaman/seaman_groups/').then(response => {
        commit('setStateData', {
          type: 'agentGroups',
          data: response.data
        })
      })
    },

    async getAgentsList ({ commit }) {
      await api.get('api/v1/seaman/list_of_seamans/').then(response => {
        response.data.results.map(item => {
          item.fullName = `${item.last_name} ${item.first_name} ${item.userprofile.middle_name}`
        })

        commit('setStateData', {
          type: 'agentsList',
          data: response.data.results
        })
      })
    },

    getFilteredETI ({ commit, state }, searchQueries) {
      return new Promise((resolve, reject) => {
        const params = new URLSearchParams({
          course: searchQueries.course.id,
          city: searchQueries.city
        })
        api.get(`api/v1/back_off/certificates/list_eti/?${params}`).then(response => {
          if (response.status === 'success') {
            response.data.map((item, key) => {
              item.institutionName = item.ntz[searchQueries.labelName]
              switch (key) {
                case 0:
                  item.status = 'green-option'
                  break
                case 1:
                  item.status = 'grey-option'
                  break
                default:
                  item.status = 'red-option'
              }
            })
            state.filteredETI[searchQueries.arrayIndex] = response.data
            resolve(response)
          }
        })
      })
    },

    async getRegistrationPermissions ({ commit }) {
      await api.get('api/v1/auth/groups/').then(response => {
        response.data.map(item => {
          item.text = item.name
          delete item.name
        })
        commit('setStateData', {
          type: 'registrationPermissionsList',
          data: response.data
        })
      })
    }
  },

  getters: {
    ranksSQC: state => state.ranks.filter(rank => rank.is_dkk),
    noSortedPositionsById: state => id => state.positions.filter(position => position.rank === id),
    positionsById: state => id => state.positions.filter(position => position.rank === id),
    positionsByIdSQC: state => id => state.positions.filter(position => position.rank === id && position.is_dkk),
    regionById: state => id => state.region.filter(region => region.country === id),
    cityById: state => id => state.city.filter(city => city.region === id),
    cityByName: state => name => state.city.filter(city => city.name === name),
    statusChoose: state => serv => state.statuses.filter(status => status.for_service === serv),
    statusById: state => id => state.statuses.find(status => status.id === id),
    portsActual: state => actuality => state.ports.filter(port => port.is_disable === actuality),
    typeDocsForUpload: state => state.typeDoc.filter(typeDoc => typeDoc.id === 2 || typeDoc.id === 3),
    typeDocQualificationByService: state => service => state.typeDocQualification.filter(typeDoc => typeDoc.for_service === service),
    institutionByType: state => id => state.institution.filter(inst => inst.type_nz === id),
    professionById: state => id => state.profession.filter(profession => profession.type_document_nz === id),
    qualificationById: state => id => state.qualificationLevels.filter(qualification => qualification.type_NZ === id),
    specializationById: state => id => state.specialization.filter(doctor => doctor.speciality === id),
    doctorsById: state => id => state.doctors.filter(doctor => doctor.medical_institution === id),
    affiliateById: state => id => state.affiliate.find(affiliate => affiliate.id === id),
    affiliateByName: state => name => state.affiliate.filter(affiliate => affiliate.name_ukr === name),
    paymentStatusByStatus: state => status => state.paymentStatus.filter(paymentStatus => paymentStatus.status === status),
    functionByPosition: state => id => state.positionFunction.filter(positionFunction => positionFunction.position === id),
    notDisabledPorts: state => state.ports.filter(port => !port.is_disable)
  }
}
