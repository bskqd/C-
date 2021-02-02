import { api } from '@/mixins/api'

export const MAIN = {
  state: () => ({
    activePage: { name: '', access: true },
    token: localStorage.getItem('Token'),
    lang: 'en',
    user: {},
    permissions: [],
    permissionsReport: {},
    version: '',
    badgesCount: {},
    userNotification: {},
    webCamView: { status: false, comp: null, model: null },
    registerCode: { status: false, code: null },
    signatureKey: { status: false, key: null },
    isContractNeeded: false,
    selfHost: false,
    isTrained: true
  }),
  mutations: {
    setMainStateData (state, data) {
      state[data.type] = []
      state[data.type] = data.data
    },
    setUserInfo (state, data) {
      state.user = data.userprofile
      state.user.id = data.id
      state.user.name = data.last_name + ' ' + data.first_name + ' ' + data.userprofile.middle_name
      state.user.username = data.username
      state.lang = (data.userprofile.language).toLowerCase()
    },
    setUserPermissions (state, data) {
      state.permissions = data
    },
    setUserGroupProfile (state, data) {
      state.user.group = data
    },
    setUserPermissionReport (state, data) {
      state.permissionsReport = data
    },
    setVersion (state, data) {
      state.version = data
    },
    setNecessaryContract (state, data) {
      state.isContractNeeded = data
    },
    setActivePage (state, data) {
      state.activePage = data
    },

    setCountBadges (state, data) {
      state.badgesCount = {
        passportAll: data.passports.sum,
        passportStatement: data.passports.statement_sailor_passport,
        passportDocument: data.passports.passport_sailor,
        passportCitizen: data.passports.passport,
        educationAll: data.education.sum,
        educationStatement: data.education.statement_adv_training,
        educationDocument: data.education.main,
        studentCard: data.education.student,
        qualificationAll: data.dpo_documents.qual_doc + data.dpo_documents.statement_qual_doc,
        qualificationDocument: data.dpo_documents.qual_doc,
        qualificationStatement: data.dpo_documents.statement_qual_doc,
        certificateAll: data.ntz.sum,
        certificateDocument: data.ntz.certificate,
        certificateStatement: data.ntz.statement_eti,
        experienceAll: data.experience.sum,
        experienceDocument: data.experience.experience_doc,
        recordBookDocument: data.experience.service_record,
        recordBookStatement: data.experience.statement_service_record,
        sqcAll: data.dkk.sum,
        sqcDocument: data.dkk.protocol_dkk,
        sqcStatement: data.dkk.statement_dkk,
        sqcWishes: data.dkk.demand_position,
        medicalAll: data.medical_sertificate.sum,
        medicalDocument: data.medical_sertificate.medical_sertificate,
        medicalStatement: data.medical_sertificate.statement_med_cert,
        positionStatement: data.packet_item
      }
    },
    incrementBadgeCount (state, data) {
      state.badgesCount[data.child]++
      state.badgesCount[data.parent]++
    },
    decrementBadgeCount (state, data) {
      state.badgesCount[data.child]--
      state.badgesCount[data.parent]--
    },
    setCitizenPassportBadgeCount (state, data) {
      state.badgesCount.passportCitizen = data
    },

    setUserNotification (state, data) {
      state.userNotification = data
    },
    incrementUserNotification (state, data) {
      state.userNotification[data]++
      state.userNotification.summ++
    },
    decrementUserNotification (state, data) {
      state.userNotification[data]--
      state.userNotification.summ--
    },

    setViewRegisterCode (state, data) {
      state.registerCode = data
    },
    setViewSignatureKey (state, data) {
      state.signatureKey = data
    },
    setWebCamView (state, data) {
      state.webCamView = data
    },
    setHostName (state) {
      state.selfHost = location.hostname !== 'sec.morrichservice.com.ua'
    }
  },
  actions: {
    getUserInfo ({ commit }) {
      return api.get('api/v1/auth/get_user_info/').then(response => commit('setUserInfo', response.data))
    },
    getUserPermissions ({ commit }) {
      return api.get('api/v1/auth/get_user_permissions/').then(response => {
        commit('setUserPermissions', response.data.permissions)
        if (response.data.groups.length) commit('setUserGroupProfile', response.data.groups[0].id)
      })
    },
    async getUserPermissionReport ({ commit }) {
      await api.get('api/v1/auth/branch_office_restr/')
        .then(response => commit('setUserPermissionReport', response.data))
    },
    async getVersion ({ commit }) {
      await api.get('api/v1/auth/version/').then(response => {
        if (response.data.length) commit('setVersion', `beta v.${response.data[0].full_version}`)
      })
    },

    async getCountBadges ({ commit }, sailorID) {
      await api.get(`api/v2/sailor/${sailorID}/count_docs/`).then(response => commit('setCountBadges', response.data))
    }
  }
}
