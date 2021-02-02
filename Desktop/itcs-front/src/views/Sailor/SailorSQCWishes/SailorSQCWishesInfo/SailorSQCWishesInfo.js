import { hideDetailed, getStatus } from '@/mixins/main'
import { mapState } from 'vuex'

export default {
  name: 'SeafarerWishesInfo',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      fieldsExistDocuments: [
        { key: 'type_doc',
          label: this.$i18n.t('typeDoc')
        },
        { key: 'number',
          label: this.$i18n.t('number')
        },
        { key: 'info',
          label: this.$i18n.t('position'),
          tdClass: 'ellipsis'
        },
        { key: 'name_issued',
          label: this.$i18n.t('issued'),
          tdClass: 'ellipsis'
        },
        { key: 'date_start',
          label: this.$i18n.t('dateEffective')
        },
        { key: 'date_end',
          label: this.$i18n.t('dateTermination')
        },
        { key: 'status',
          label: this.$i18n.t('status')
        }
      ],
      fieldsApplication: [
        { key: 'type_document',
          label: this.$i18n.t('typeDoc')
        },
        { key: 'document_descr',
          label: this.$i18n.t('nameDoc'),
          tdClass: 'ellipsis'
        },
        { key: 'standarts_text',
          label: this.$i18n.t('requirements'),
          tdClass: 'ellipsis'
        }
      ],
      sortByA: 'status',
      sortDescA: true,
      hideDetailed,
      getStatus
    }
  },
  computed: {
    ...mapState({
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    })
  }
}
