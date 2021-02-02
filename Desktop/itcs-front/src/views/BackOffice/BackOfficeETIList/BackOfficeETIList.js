import { mapState } from 'vuex'
import CertificateAdd from './BackOfficeETIListAdd/BackOfficeETIListAdd.vue'

export default {
  name: 'BackOfficeListETI',
  components: {
    CertificateAdd
  },
  data () {
    return {
      fields: [
        { key: 'contract_number',
          label: this.$i18n.t('contractNumber')
        },
        { key: 'etiInstitutionName',
          label: this.$i18n.t('denomination')
        },
        { key: 'director_name',
          label: this.$i18n.t('directorName')
        },
        { key: 'okpo',
          label: this.$i18n.t('edrpou')
        },
        { key: 'is_red',
          label: this.$i18n.t('isRed')
        },
        { key: 'is_disable',
          label: this.$i18n.t('status')
        },
        { key: 'event',
          label: this.$i18n.t('actions'),
          class: 'mw-0'
        }
      ],
      newDoc: false
    }
  },
  computed: {
    ...mapState({
      items: state => state.sailor.backOfficeETIList
    })
  }
}
