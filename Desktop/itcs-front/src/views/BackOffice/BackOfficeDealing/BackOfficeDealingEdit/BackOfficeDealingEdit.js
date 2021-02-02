import { viewDetailedComponent } from '@/mixins/main'
import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'

export default {
  name: 'BackOfficeDealingETIEdit',
  props: {
    sailorDocument: Object
  },
  components: {
    ValidationAlert
  },
  data () {
    return {
      fields: [
        { key: 'institution',
          label: this.$i18n.t('eti'),
          sortable: true,
          tdClass: 'w-75'
        },
        { key: 'ratio',
          label: this.$i18n.t('ratio'),
          tdClass: 'd-flex align-items-center'
        },
        { key: 'consider',
          label: this.$i18n.t('consider')
        }
      ],
      items: [],
      number: {
        N: {
          pattern: /\d/
        },
        T: {
          pattern: /[1]/
        },
        R: {
          pattern: /[0]/
        },
        C: {
          pattern: /([,|.])/
        }
      },
      buttonLoader: false,
      viewDetailedComponent
    }
  },
  mounted () {
    this.getAllETIByCourse()
  },
  methods: {
    getAllETIByCourse () {
      this.$api.get(`api/v1/back_off/certificates/eti_registry/?course=${this.sailorDocument.id}&is_red=true`)
        .then(response => {
          if (response.code === 200) {
            response.data.map(val => {
              val.ratio = null
              this.sailorDocument.ntz_ratio.map(value => {
                if (value.ntz.id === val.institution.id) {
                  val.ratio = value.ratio * 100
                }
              })
              val.consider = val.ratio !== null
              val.error = false
            })
            this.items = response.data
            this.sailorDocument.child = response.data
          }
        })
    },
    checkSumRatio (row) {
      let sum = 0
      this.items.map(val => {
        val.error = false
        sum += (val.ratio === '' || val.ratio === null) ? 0 : parseInt(val.ratio)
      })

      if (sum > 100) row.item.error = true
    },

    setRatio () {
      let ratioArr = []
      this.sailorDocument.child.filter(val => {
        if (val.consider) {
          ratioArr.push({
            eti_id: val.institution.id,
            eti_ratio: parseFloat(val.ratio) / 100
          })
        }
      })

      const body = {
        eti_ratio: ratioArr
      }

      this.$api.put(`api/v1/back_off/certificates/month_ratio/${this.sailorDocument.id}/`, body)
        .then(response => {
          if (response.code === 200) {
            this.sailorDocument.ntz_ratio = response.data.ntz_ratio
            this.viewDetailedComponent(this.sailorDocument, 'viewInfoBlock')
          }
        })
    }
  }
}
