import store from '@/store'

class API {
  mainUrl = process.env.VUE_APP_MAIN
  mainUrlMedia = process.env.VUE_APP_MAIN_MEDIA

  fetch (url, options, body) {
    const token = localStorage.getItem('Token')

    if (!options.headers) {
      options.headers = {}
      options.headers.Accept = 'application/json'
      options.headers['Content-Type'] = 'application/json'
    }

    if (token) {
      options.headers.Authorization = `Token ${token}`
    }
    if (body) {
      options.body = JSON.stringify(body)
    }

    return fetchRequest(this.mainUrl + url, options)
  }

  async fetchPhoto (url, options, formData) {
    const token = localStorage.getItem('Token')

    if (!options.headers) {
      options.headers = {}
    }
    if (token) {
      options.headers.Authorization = `Token ${token}`
    }
    options.body = formData

    if (options.method === 'GET') {
      options.headers['Access-Control-Request-Headers'] = '*'
      return fetchFiles(this.mainUrlMedia + url, options)
        .then(images => {
          if (images) {
            return URL.createObjectURL(images)
          }
        })
    } else {
      return fetchRequest(this.mainUrl + url, options)
    }
  }

  get (url, headers = null) {
    const options = {
      method: 'GET',
      headers
    }
    return this.fetch(url, options)
  }

  post (url, body, headers = null) {
    const options = {
      method: 'POST',
      headers
    }
    return this.fetch(url, options, body)
  }

  put (url, body) {
    const options = { method: 'PUT' }
    return this.fetch(url, options, body)
  }

  delete (url) {
    const options = { method: 'DELETE' }
    return this.fetch(url, options)
  }

  patch (url, body) {
    const options = { method: 'PATCH' }
    return this.fetch(url, options, body)
  }

  getPhoto (url) {
    const options = {
      method: 'GET'
    }
    return this.fetchPhoto(url, options)
  }

  postPhoto (data, type, id) {
    let url = 'api/v1/sailor/photo_uploader/'

    const options = {
      method: 'POST'
    }

    let dataPhoto = new FormData()
    dataPhoto.append('type_document', type)
    dataPhoto.append('id_document', id)

    for (let photo of data) {
      dataPhoto.append('photo', photo)
    }

    return this.fetchPhoto(url, options, dataPhoto)
  }

  deletePhoto (_this, photoId) {
    const dataDocument = new FormData()
    dataDocument.append('type_document', _this.photoTypeDoc)
    dataDocument.append('id_document', _this.sailorDocument.id)

    const url = `api/v1/sailor/photo_uploader/${photoId}/`
    const token = localStorage.getItem('Token')
    const options = {
      method: 'DELETE',
      headers: {
        Authorization: `Token ${token}`
      },
      body: dataDocument
    }
    return fetchRequest(this.mainUrl + url, options)
  }

  getFiles (url) {
    const options = {
      method: 'GET'
    }
    return fetchFiles(this.mainUrlMedia + url, options)
  }
}

export const fetchFiles = (url, options) => {
  return fetch(url, options)
    .then((response) => {
      if (response.ok) {
        return response.blob()
      }
    })
    .catch((error) => {
      console.error(error)
    })
}

export const fetchRequest = (url, options) => {
  return fetch(url, options)
    .then(response => {
      switch (true) {
        case response.status === 204: // delete
          return { status: 'deleted', code: response.status }
        case response.status === 304:
          return { status: 'ok', code: response.status }
        case response.status >= 200 && response.status <= 299:
        case response.status === 400:
          return response.json().then(data => {
            switch (response.status) {
              case 200:
                return { status: 'success', code: response.status, data: data }
              case 201: // create any
                return { status: 'created', code: response.status, data: data }
              case 400:
                return { status: 'error', code: response.status, data: data }
            }
          })
        case response.status === 401:
          if (window.location.pathname !== '/login' && window.location.pathname !== '/404') {
            localStorage.removeItem('Token')
            window.location = '/login'
          }
          break
        case response.status === 418:
          window.location = '/404'
          break
        case response.status === 419:
          store.commit('setNecessaryContract', true)
          break
        case response.status === 404:
          return { status: 'not found', code: response.status }
        case response.status === 500:
          return { status: 'server error', code: response.status }
        case response.status === 502:
          return { status: 'bad gateway', code: response.status }
      }
    })
    .catch((error) => {
      console.error(error)
    })
}

export const getProcessingStatus = (type) => {
  switch (type) {
    case 0:
      return { id: 0, name_ukr: 'Не потрібно', name_eng: 'Do not need' }
    case 1:
      return { id: 1, name_ukr: 'Потрібно за 20 днів', name_eng: 'Needed in 20 days' }
    case 2:
      return { id: 2, name_ukr: 'Потрібно за 7 днів', name_eng: 'Needed in 7 days' }
    case 3:
      return { id: 3, name_ukr: 'Подовження за 20 днів', name_eng: 'Continued in 20 days' }
    case 4:
      return { id: 4, name_ukr: 'Подовження за 7 днів', name_eng: 'Continued in 7 days' }
  }
}

export const getUpdatedObject = (data) => {
  data.value.behavior = { viewInfoBlock: true }
  switch (data.type) {
    case 'sailorPassportStatement':
      data.value.processingStatus = getProcessingStatus(data.value.type_receipt)
      break
    case 'education':
      if (data.value.type_document.id === 1 || data.value.type_document.id === 2) data.value.experied_date = '-'
      break
    case 'qualification':
      if (data.value.type_document.id === 16) data.value.number = data.value.number_document
      break
    case 'serviceRecordBookLine':
      data.value.list_responsibilities = data.value.all_responsibility.filter(resp => resp.responsibility)
      break
    case 'experience':
      data.value.list_responsibilities = data.value.all_responsibility.filter(resp => resp.responsibility)
      break
    case 'sailorSQCProtocols':
      data.value.list_positions = data.value.position
      data.value.membersCommission = data.value.commissioner_sign.filter(value => value.commissioner_type === 'CH') // .map(value => value.user_fio_ukr)
      data.value.headCommission = data.value.commissioner_sign.find(value => value.commissioner_type === 'HD')
      data.value.secretaryCommission = data.value.commissioner_sign.find(value => value.commissioner_type === 'SC')
      break
    case 'positionStatement':
      data.value.list_positions = data.value.position
      data.value.includeSailorPass = getProcessingStatus(data.value.include_sailor_passport)
      break
    case 'newAccounts':
      data.value.sailorDateBirth = null
      break
    case 'backOfficeCoefficient':
      data.value.allowChange = new Date(data.value.date_start) > new Date()
      break
  }
  return data
}

export const api = new API()
