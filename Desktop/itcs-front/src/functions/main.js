/**
* Global Functions
* */

import store from '@/store'

/**
 * Fetch
 * @param _this
 * @param url
 * @param options
 * @returns {Promise<Response>}
 */
export const myFetch = (_this, url, options) => {
  return fetch(url, options)
    .then(response => {
      switch (true) {
        case response.status === 101:
        case response.status === 204:
        case response.status === 205:
          return { status: 'deleted' }
        case response.status === 304:
          return { status: 'ok' }
        case response.status >= 200 && response.status <= 299:
        case response.status === 400:
          return response.json().then(data => {
            switch (response.status) {
              case 200:
                return { status: 'success', data: data }
              case 201: // create any
                return { status: 'created', data: data }
              case 204: // delete
                return { status: 'deleted' }
              case 400:
                if (data[0] === 'Sailor not found' || data[0] === 'Sailor does not exists') {
                  // this.$notification.error.(_this, 'Моряка не існує')
                  _this.$swal('Моряка не існує!')
                    .then(() => {
                      // window.location = '/'
                    })
                } else {
                  return { status: 'error', data: data }
                }
            }
          })
        // case response.status === 400:
        //   console.log(response)
        //   this.$notification.error(_this, 'Спробуйте знову')
        //   return { status: 'error' }
        case response.status === 401:
          if (window.location.pathname !== '/login') {
            // localStorage.removeItem('Token')
            // window.location = '/login'
          }
          break
        case response.status === 418:
          window.location = '/404'
          break
        case response.status === 404:
          // this.$notification.error(_this, 'Спробуйте знову')
          return { status: 'not found' }
        case response.status === 500:
          // this.$notification.error(_this, 'Спробуйте знову')
          return { status: 'server error' }
        case response.status === 502:
          // this.$notification.error(_this, 'Спробуйте знову')
          return { status: 'bad gateway' }
      }
    })
    .catch((error) => {
      console.error(error)
      if (window.location.pathname !== '/login' && error.status === 401) {
        console.log('kick')
        // localStorage.removeItem('Token')
        // window.location = '/login'
      }
    })
}

export const myFetchGetPhoto = (_this, url) => {
  const token = localStorage.getItem('Token')
  let optionsPhoto = {
    method: 'GET',
    headers: {
      'Access-Control-Request-Headers': '*',
      'Authorization': 'Token ' + token
    },
    mode: 'cors',
    redirect: 'follow'
  }
  return fetch(url, optionsPhoto)
    .then(response => {
      switch (true) {
        case response.status >= 200 && response.status <= 299:
        case response.status === 400:
          return response.blob().then(images => {
            return URL.createObjectURL(images)
          })
      }
    })

  // response.blob()).then(images => {
  //   let outside = URL.createObjectURL(images)
  //   console.log(outside)
  //   _this.img = outside
  // })}
}

export const myFetchDoc = (url, options) => {
  return fetch(url, options)
    .then((response) => {
      if (response.status === 401) {
        // localStorage.removeItem('Token')
        // window.location = '/login'
      }
      if (response.ok) {
        return response.blob()
      }
    })
    .catch((error) => {
      console.error(error)
    })
}

/**
 * Show info row in table
 * @param row
 */
export const showDetailed = (row) => {
  if (!row.detailsShowing) {
    row.toggleDetails()
  }
}

/**
 * Hide info row in table
 * @param row
 */
export const hideDetailed = (row) => {
  row.toggleDetails()
}

/**
 * Check authorization client
 * @param token
 */
export const checkClient = (token) => {
  console.log(token)
}

export const changeLang = (lang) => {
  console.log(lang)
}

export function dateFormat (date = null) {
  let today = date || new Date()
  let dd = today.getDate()
  let mm = today.getMonth() + 1
  let yyyy = today.getFullYear()
  if (dd < 10) {
    dd = '0' + dd
  }
  if (mm < 10) {
    mm = '0' + mm
  }
  return yyyy + '-' + mm + '-' + dd
}

export const fetchPhoto = (_this, method, typeDocTitle, seafarerID, photos) => {
  const token = localStorage.getItem('Token')
  const API = process.env.VUE_APP_API
  let dataPhoto = new FormData()
  dataPhoto.append('type_document', typeDocTitle)
  dataPhoto.append('id_document', seafarerID)

  for (let photo of photos) {
    dataPhoto.append('photo', photo)
  }

  let url = API + 'sailor/photo_uploader/'

  try {
    return fetch(url, {
      method: method,
      body: dataPhoto,
      mode: 'cors',
      headers: {
        'Authorization': 'Token ' + token
      }
    })
      .then(response => {
        return response
      })
  } catch (error) {
    console.error('Error:', error)
  }
}

/**
 * clear select field options when rank.id != positions.rank
 * @param rank
 * @param positions
 */
export const clearPosition = (rank, positions) => {
  // if (positions !== null && rank.id !== positions[0].rank) {
  if (positions !== null) {
    positions.splice(0, positions.length)
  }
  // }
}

export const takePhotoFromCamera = (component, model) => {
  store.commit('setWebCamView',
    { status: true, comp: component, model: model })
}

/** Tomorrow's date in format YYYY-MM-DD */
export const getTomorrowDate = () => {
  const today = new Date()
  let tomorrow = new Date(today)
  tomorrow.setDate(tomorrow.getDate() + 1)
  tomorrow = tomorrow.toISOString().split('T')[0]
  return tomorrow
}

/**
 * Notification function
 * @param component
 * @param title
 * @param text
 * @param type
 */
export const hotify = (component, title, text, type) => {
  component.$notify({
    group: 'notify',
    title: title,
    text: text,
    duration: 7000,
    type: type
  })
}
