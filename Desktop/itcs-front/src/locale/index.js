import Vue from 'vue'
import VueI18n from 'vue-i18n'
import en from './en.json'
import ua from './ua.json'
import store from '@/store/index'
import { myFetch } from '@/functions/main'

Vue.use(VueI18n)

const TRANSLATIONS = {
  en: en,
  ua: ua
}

const messages = Object.assign(TRANSLATIONS)

async function getLang () {
  let url = process.env.VUE_APP_API + 'auth/get_user_language/'
  let options = {
    method: 'GET',
    mode: 'cors',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + store.state.main.token
    }
  }
  try {
    let getUserInfo = await myFetch('', url, options)
    i18n.locale = (getUserInfo.data.language).toLowerCase()
  } catch (e) {
    i18n.locale = 'ua'
  }
}
getLang()

const i18n = new VueI18n({
  locale: store.state.main.lang,
  messages,
  silentTranslationWarn: process.env.NODE_ENV === 'production'
})

export default i18n
