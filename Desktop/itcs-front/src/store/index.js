import Vue from 'vue'
import Vuex from 'vuex'
import { MAIN } from './main'
import { DIRECTORY } from './directory'
import { SAILOR } from './sailor'

Vue.use(Vuex)

export const OPTIONS = {
  method: 'GET',
  mode: 'cors',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Token ' + localStorage.getItem('Token')
  }
}

export default new Vuex.Store({
  modules: {
    main: MAIN,
    directory: DIRECTORY,
    sailor: SAILOR
  }
})
