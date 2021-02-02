import Vue from 'vue'
import Vuelidate from 'vuelidate'
import App from './App.vue'
import '@/registerServiceWorker'
import router from '@/router'
import store from '@/store'
import i18n from '@/locale/index'
import vuetify from '@/plugins/vuetify'
import VueSwal from 'vue-swal'
import { BootstrapVue, BootstrapVueIcons } from 'bootstrap-vue'
import Unicon from 'vue-unicons'
import { uniPlusCircle, uniCancel, uniPen, uniMultiply, uniAngleDown, uniAngleUp, uniCheck, uniPlus, uniInfoCircle,
  uniRefresh, uniScenery, uniUserCircle, uniFileUploadAlt, uniSync, uniBell, uniArrowCircleRight, uniCheckCircle,
  uniUpload, uniTrashAlt, uniFolderCheck, uniBookOpen, uniEnvelopeAdd } from 'vue-unicons/src/icons'
import { logo, logoMain, dcc, experience, qualification, medical, passports, graduation, ntzcerts, positionStatement,
  arrowRight } from '@/custom-icons'
import Multiselect from 'vue-multiselect'
import Notifications from 'vue-notification'
import WebCam from 'vue-web-cam'
import { notify } from '@/mixins/notify'
import { api } from '@/mixins/api'
import VueTheMask from 'vue-the-mask'
import VueNumeric from 'vue-numeric'
import Clipboard from 'v-clipboard'
import { sync } from 'vuex-router-sync'
import Table from './components/layouts/Table/Table.vue'

import 'vue-multiselect/dist/vue-multiselect.min.css'
import '@/assets/sass/main.sass'
import '@/assets/scss/main.scss'
import 'vuesax/dist/vuesax.css'
import '@/assets/sass/media/media.sass'
import '@/assets/css/main.css'
import '@/assets/css/bootstrap.css'
import '@/assets/css/bootstrap-extended.css'
import '@/assets/css/vertical-menu.css'
import '@/assets/css/core.css'

Vue.config.productionTip = false

Unicon.add([uniPlusCircle, uniCancel, uniPen, uniMultiply, uniAngleDown, uniAngleUp, uniCheck, uniPlus, uniInfoCircle,
  uniRefresh, uniScenery, uniUserCircle, logo, logoMain, dcc, experience, qualification, medical, passports, graduation,
  ntzcerts, uniFileUploadAlt, uniSync, uniBell, uniArrowCircleRight, positionStatement, uniCheckCircle, uniUpload,
  uniTrashAlt, uniFolderCheck, uniBookOpen, arrowRight, uniEnvelopeAdd ])

Vue.use(router)
Vue.use(VueSwal)
Vue.use(BootstrapVue)
Vue.use(BootstrapVueIcons)
Vue.use(Vuelidate)
Vue.use(Unicon)
Vue.use(Notifications)
Vue.use(WebCam)
Vue.component('multiselect', Multiselect)
Vue.use(VueTheMask)
Vue.use(VueNumeric)
Vue.use(Clipboard)
Vue.component('Table', Table)

Vue.prototype.$notification = notify
Vue.prototype.$api = api

sync(store, router)

new Vue({
  vuetify,
  router,
  store,
  i18n,
  render: h => h(App)
}).$mount('#app')
