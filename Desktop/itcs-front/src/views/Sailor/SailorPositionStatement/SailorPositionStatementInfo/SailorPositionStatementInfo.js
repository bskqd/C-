import { hideDetailed, getDateFormat, getStatus } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapGetters, mapState } from 'vuex'
import { OPTIONS } from '@/store/index'

export default {
  name: 'SeafarerPositionApplicationInfo',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      missingDocFields: [
        { key: 'type_document_name',
          label: this.$i18n.t('typeDoc')
        },
        { key: 'document_description',
          label: this.$i18n.t('nameDoc')
        },
        { key: 'date_start_meeting',
          label: this.$i18n.t('dateStartEvent')
        },
        { key: 'date_end_meeting',
          label: this.$i18n.t('dateEndEvent')
        },
        { key: 'standarts_text',
          label: this.$i18n.t('requirements')
        },
        { key: 'payment_info',
          label: this.$i18n.t('payment')
        }
      ],
      agentAndServiceCenterFields: [
        { key: 'type_document_name',
          label: this.$i18n.t('typeDoc')
        },
        { key: 'name',
          label: this.$i18n.t('nameUa')
        },
        { key: 'additional',
          label: this.$i18n.t('nameEn')
        },
        { key: 'price',
          label: this.$i18n.t('price')
        }
      ],
      existAndAfterDocsFields: [
        { key: 'type_document_name',
          label: this.$i18n.t('typeDoc')
        },
        { key: 'number',
          label: this.$i18n.t('number')
        },
        { key: 'name_issued',
          label: this.$i18n.t('issued')
        },
        { key: 'date_start',
          label: this.$i18n.t('dateEffective')
        },
        { key: 'date_end',
          label: this.$i18n.t('dateTermination')
        },
        { key: 'info',
          label: this.$i18n.t('position')
        },
        { key: 'payment_info',
          label: this.$i18n.t('payment')
        },

        { key: 'status',
          label: this.$i18n.t('status')
        }
      ],
      MAIN: process.env.VUE_APP_MAIN,
      sortBy: 'type_document_name',
      sortDesc: false,
      hideDetailed,
      getDateFormat,
      checkAccess,
      getStatus
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr'
    }),
    ...mapGetters({
      sailorIsCadet: 'sailorIsCadet'
    })
  },
  mounted () {
    this.sailorDocument.dependencies.documents_and_statement.sort((a, b) => {
      if (a.status > b.status) {
        return -1
      }
    })

    const validQualificationDoc = this.sailorDocument.dependencies.documents_and_statement
      .find(value => (value.status === 1 || value.status === 2) && value.type_document_name === 'Кваліфікаційний документ')
    if (!validQualificationDoc) {
      this.sailorDocument.dependencies.documents_and_statement.map(item => {
        item.allowCreateDiploma = item.status === 1 && item.type_document_name === 'Підтвердження кваліфікаційного документу'
        return item
      })
    }
  },
  methods: {
    /** Set document price with commission of 4% */
    setPriceWithCommission (price) {
      return (price + (price * 0.04)).toFixed(2)
    },

    /** Create payment link with platon */
    createPayment (url) {
      const params = new URLSearchParams({
        callback_url: window.location.href
      })
      // window.open(`${this.MAIN}${url}?${params}`, '_blank')
      fetch(`${this.MAIN}${url}?${params}`, OPTIONS).then(response => {
        response.text().then(html => {
          document.getElementById('app').innerHTML = html
          document.getElementById('pay').click()
        })
      })
    },

    createDiploma () {
      this.$swal({
        title: this.$i18n.t('warning'),
        text: this.$i18n.t('createDiplomaConfirmation'),
        icon: 'info',
        buttons: [this.$i18n.t('cancel'), this.$i18n.t('confirm')],
        dangerMode: true
      }).then(confirmation => {
        if (confirmation) {
          this.$api.post(`api/v1/back_off/packet/${this.sailorDocument.id}/create_diploma_for_proof/`).then(response => {
            if (response.status === 'success') {
              this.$notification.success(this, this.$i18n.t('createdDiplomaStatement'))
              this.$store.dispatch('getPositionStatements', this.id)
            }
          })
        }
      })
    }

  }

}
