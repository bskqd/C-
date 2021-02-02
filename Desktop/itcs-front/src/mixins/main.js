import store from '@/store'
import router from '@/router'

import Vue from 'vue'
import _ from 'lodash'
import i18n from '@/locale/index'

// id list statuses
const inProcess = [1, 5, 6, 11, 14, 18, 20, 21, 25, 31, 32, 48, 50, 51, 52, 63, 66, 69, 72, 77, 80, 82, 83]
const expired = [7, 8, 13, 30, 33, 53, 54, 56, 57, 73, 84]
const warning = [3, 45]
const reject = [4, 10, 16, 17, 23, 36, 44, 46, 49, 62, 65, 68, 71, 76, 79]
const valid = [0, 2, 9, 12, 19, 24, 29, 39, 41, 43, 47, 55, 58, 61, 64, 67, 70, 75, 78, 81]
const verification = [34, 60, 74, 86]
const info = [42]

export const getStatus = (statusId) => {
  switch (true) {
    case (inProcess.includes(statusId)):
      return 'in-process'
    case (expired.includes(statusId)):
      return 'expired'
    case (warning.includes(statusId)):
      return 'warning'
    case (reject.includes(statusId)):
      return 'reject'
    case (valid.includes(statusId)):
      return 'valid'
    case (verification.includes(statusId)):
      return 'verification'
    case (info.includes(statusId)):
      return 'info'
  }
}

export const getPaymentStatus = (statusId) => {
  if (statusId) {
    return 'payed'
  } else return 'notPayed'
}

export const getDateFormat = (date) => {
  if (date) {
    return date.split('-').reverse().join('.')
  }
}

export const viewDetailedBlock = (row, block) => {
  row.item.behavior = {}
  row.item.behavior[block] = true
}
export const viewDetailedComponent = (component, block) => {
  console.log(component)
  component.behavior = {}
  component.behavior[block] = true
}

export const showDetailed = (row) => {
  if (!row.detailsShowing) {
    row.toggleDetails()
  }
}

export const hideDetailed = (row) => {
  row.toggleDetails()
}

export const takePhotoFromCamera = (component, model) => {
  store.commit('setWebCamView',
    { status: true, comp: component, model: model })
}

export const getFilesFromData = (files) => {
  let photoArr = []
  try {
    for (let p of files) {
      Vue.prototype.$api.getPhoto(`media/${p.photo}`).then(photo => {
        photoArr.push({ id: p.id, url: photo, photoName: p.photo, isDeleted: p.is_delete })
      })
    }
  } catch (e) {
    console.log(e)
  }
  return photoArr
}

export const mappingQualification = (typeDocument, qualification) => {
  if (typeDocument !== null) {
    let qualificationType = 0
    switch (typeDocument.id) {
      case 1:
        qualificationType = 5
        return store.getters.qualificationById(qualificationType)
      case 3:
        qualificationType = 2
        return store.getters.qualificationById(qualificationType)
      case 2:
      case 4:
        qualificationType = 3
        return store.getters.qualificationById(qualificationType)
      default:
        qualification = null
        return []
    }
  } else {
    qualification = null
    return []
  }
}
export const mappingSpecialization = (speciality) => {
  if (speciality) {
    return store.getters.specializationById(speciality.id)
  } else {
    return []
  }
}

export const mappingProfession = (typeDocument) => {
  if (typeDocument) {
    if (typeDocument.id === 2) {
      return store.getters.professionById(4)
    } else {
      return store.getters.professionById(typeDocument.id)
    }
  } else {
    return store.state.directory.profession
  }
}

export const clearPosition = (rank, positions) => {
  if (positions) {
    positions.splice(0, positions.length)
  }
}

export const setSearchDelay = (_this, searchQuery, delayProp) => {
  clearTimeout(_this.delayProp)
  _this.delayProp = setTimeout(() => {
    _this.goSearch(searchQuery)
  }, 1000)
}

export const goBack = () => {
  // window.history.back()
  window.open('/', '_self')
}

export const mappingPositions = (rank) => {
  if (rank) {
    return store.getters.positionsById(rank.id)
  } else return []
}

export const mappingSQCPositions = (rank) => {
  if (rank) {
    return store.getters.positionsByIdSQC(rank.id)
  } else return []
}

export const mappingAvailablePositions = (rank) => {
  if (rank) {
    return store.getters.availablePositionsById(rank.id)
  } else return []
}

export const separatedExpiredDocs = (array, prop, maxDateProp, minDateProp) => {
  // Get min and max date for expired documents
  const minDateObject = _.minBy(array, value => { if (value[prop].id === 7) return value[minDateProp] })
  const maxDateObject = _.maxBy(array, value => { if (value[prop].id === 7) return value[maxDateProp] })
  // Get expired documents amount
  const expiredDocs = array.filter(value => value.status_document.id === 7)
  // Group records by expired status
  const result = []
  const sortedArrByStatus = _.toArray(_.groupBy(array, value => value[prop].id === 7))
  sortedArrByStatus.forEach(value => {
    if (value[0][prop].id === 7) {
      result.push({
        behavior: {},
        [prop]: value[0][prop],
        [minDateProp]: minDateObject[minDateProp],
        [maxDateProp]: maxDateObject[maxDateProp],
        statusClass: (value[0][prop].name_eng).replace(' ', '-').toLowerCase(),
        expiredDocsLength: expiredDocs.length,
        expiredDocs: value
      })
    } else {
      for (const document of value) {
        result.unshift(document)
      }
    }
  })
  return result
}

export const deleteConfirmation = (_this) => {
  return new Promise((resolve) => {
    _this.$swal({
      title: i18n.t('warning'),
      text: i18n.t('confirmDeleting'),
      icon: 'info',
      buttons: [i18n.t('cancel'), i18n.t('confirm')],
      dangerMode: true
    }).then(confirmation => {
      resolve(confirmation)
    })
  })
}

export const regenerationConfirmation = (_this) => {
  return new Promise((resolve) => {
    _this.$swal({
      title: i18n.t('regenerationConfirm'),
      text: i18n.t('regenerationInfo'),
      icon: 'warning',
      buttons: [i18n.t('cancel'), i18n.t('confirm')],
      dangerMode: true
    }).then(confirmation => {
      resolve(confirmation)
    })
  })
}

export const getExperienceStatus = (row) => {
  let status
  if (row.item.value) {
    status = i18n.t('enough')
  } else {
    try {
      status = `${i18n.t('required')}: ${row.item.must_be_exp} ${i18n.t('month')};
        ${i18n.t('received')}: ${row.item.sailor_month} ${i18n.t('month')} ${row.item.sailor_days} ${i18n.t('days')};
        ${i18n.t('left')}: ${row.item.month_left} ${i18n.t('month')} ${row.item.days_left} ${i18n.t('days')};`
    } catch {
      status = `${i18n.t('left')} ${row.item.month_left} ${i18n.t('month')} ${i18n.t('of')} ${row.item.must_be_exp} ${i18n.t('month')}`
    }
  }
  return status
}

export const enterDoublePosition = (rank, positions) => {
  positions.splice(0, positions.length)
  if (rank) {
    const doublePositions = [106, 121, 122, 123]
    if (doublePositions.includes(rank.id)) {
      const positionList = store.getters.positionsByIdSQC(rank.id)
      positionList.forEach(value => {
        positions.push(value)
      })
    }
  }
}

export const back = (type) => {
  const link = store.state.route.from.name || type
  router.push({ name: link })
}
