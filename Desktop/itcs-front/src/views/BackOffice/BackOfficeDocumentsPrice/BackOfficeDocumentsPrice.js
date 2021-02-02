import BackOfficeDocumentsPriceAdd from './BackOfficeDocumentsPriceAdd/BackOfficeDocumentsPriceAdd.vue'

export default {
  name: 'BackOfficeDocumentsPrice',
  components: {
    BackOfficeDocumentsPriceAdd
  },
  data () {
    return {
      fields: [
        { key: 'typeDocName',
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
      items: [],
      tableLoader: true,
      viewAddBlock: false
    }
  },
  mounted () {
    this.getPrice()
  },
  methods: {
    /** Get price list */
    getPrice () {
      this.tableLoader = true
      this.$api.get('api/v1/back_off/price_for_position/actual_values/').then(response => {
        this.tableLoader = false
        response.data.map(item => {
          item.typeDocName = `${item.type_of_form === 'First' ? this.$i18n.t('First') : this.$i18n.t('Second')} ${item.type_document.value}`
        })
        response.data.sort((a, b) => {
          if (a.type_document.value < b.type_document.value) {
            return -1
          }
        })
        this.items = response.data
      })
    }
  }
}
