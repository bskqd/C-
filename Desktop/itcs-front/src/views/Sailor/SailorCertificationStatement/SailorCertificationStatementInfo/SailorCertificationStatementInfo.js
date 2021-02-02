import { mapState } from 'vuex'
import { getDateFormat, hideDetailed, getStatus } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { OPTIONS } from '@/store/index'

export default {
  name: 'SeafarerCertApplicationInfo',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      MAIN: process.env.VUE_APP_MAIN,
      hideDetailed,
      getDateFormat,
      checkAccess,
      getStatus
    }
  },
  computed: {
    ...mapState({
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    }),
    priceWithCommission () {
      if (checkAccess('certificationStatement', 'payment', this.sailorDocument)) {
        return this.sailorDocument.requisites.amount + (this.sailorDocument.requisites.amount * 0.04)
      } else return this.sailorDocument.requisites.amount
    }
  },
  methods: {
    /** Create a payment with "Platon" system */
    createPayment () {
      const params = new URLSearchParams({
        callback_url: window.location.href
      })
      // window.open(`${this.MAIN}payments/platon/statement_certificate/${this.sailorDocument.id}/?${params}`, '_blank')
      fetch(`${this.MAIN}payments/platon/statement_certificate/${this.sailorDocument.id}/?${params}`, OPTIONS)
        .then(response => {
          response.text().then(html => {
            document.getElementById('app').innerHTML = html
            document.getElementById('pay').click()
          })
        })
    }
  }
}
