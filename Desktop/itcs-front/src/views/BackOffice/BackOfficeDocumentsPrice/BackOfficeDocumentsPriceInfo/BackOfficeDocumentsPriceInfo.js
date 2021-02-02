import { deleteConfirmation, hideDetailed } from '@/mixins/main'
import Paginate from '@/components/atoms/Paginate'

export default {
  name: 'BackOfficeDocumentsPriceInfo',
  props: {
    row: Object
  },
  components: {
    Paginate
  },
  data () {
    return {
      fields: [
        { key: 'type_of_form',
          label: this.$i18n.t('typeDoc')
        },
        { key: 'date_start',
          label: this.$i18n.t('dateEffective')
        },
        { key: 'full_price',
          label: this.$i18n.t('coming')
        },
        { key: 'to_sqc',
          label: this.$i18n.t('toSQC'),
          thClass: 'border-l',
          tdClass: 'border-l'
        },
        { key: 'to_qd',
          label: this.$i18n.t('toQD')
        },
        { key: 'to_td',
          label: this.$i18n.t('toTD')
        },
        { key: 'to_sc',
          label: this.$i18n.t('toSC')
        },
        { key: 'to_agent',
          label: this.$i18n.t('toAgent')
        },
        { key: 'to_medical',
          label: this.$i18n.t('toMedical')
        },
        { key: 'to_cec',
          label: this.$i18n.t('toCEC')
        },
        { key: 'to_mrc',
          label: this.$i18n.t('toMRC')
        },
        { key: 'to_portal',
          label: this.$i18n.t('toPortal'),
          thClass: 'border-r',
          tdClass: 'border-r'
        },
        { key: 'sum_to_distribution',
          label: this.$i18n.t('all')
        },
        { key: 'profit',
          label: this.$i18n.t('profit')
        },
        { key: 'event',
          label: this.$i18n.t('actions'),
          class: 'mw-0'
        }
      ],
      itemsFuture: {},
      itemsPast: {},
      hideDetailed
    }
  },
  mounted () {
    this.getFutureValuesInfo()
    this.getPastValuesInfo()
  },
  methods: {
    /** Get previous price for future value */
    getFutureValuesInfo (page = null) {
      const url = page || `api/v1/back_off/price_for_position/${this.row.item.id}/future_values/?page_size=20`
      this.$api.get(url).then(response => {
        if (response.status === 'success') {
          response.data.results.map(item => {
            item.behavior = {}
            item.allowDelete = new Date(item.date_start) > new Date()
            // condition for actual value below
            item.allowEdit = !((!item.date_end || new Date(item.date_end) >= new Date()) && new Date(item.date_start) <= new Date())
          })
          this.itemsFuture = response.data
        }
      })
    },

    /** Get previous price for position value */
    getPastValuesInfo (page = null) {
      const url = page || `api/v1/back_off/price_for_position/${this.row.item.id}/past_values/?page_size=20`
      this.$api.get(url).then(response => {
        if (response.status === 'success') {
          response.data.results.map(item => {
            item.behavior = {}
            item.allowDelete = new Date(item.date_start) > new Date()
            // condition for actual value below
            item.allowEdit = !((!item.date_end || new Date(item.date_end) >= new Date()) && new Date(item.date_start) <= new Date())
          })
          this.itemsPast = response.data
        }
      })
    },

    /** Delete row price for position */
    deletePositionPrice (row) {
      deleteConfirmation(this).then(confirmation => {
        if (confirmation) {
          this.$api.delete(`api/v1/back_off/price_for_position/${row.item.id}/`).then(response => {
            if (response.status === 'delete') {
              this.$notification.success(this, this.$i18n.t('priceEtiDeleted'))
              this.getFutureValuesInfo()
              this.getPastValuesInfo()
            }
          })
        }
      })
    }
  }
}
