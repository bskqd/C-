import { mapState } from 'vuex'
import { getDateFormat, getStatus, hideDetailed, getExperienceStatus } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'

export default {
  name: 'SailorQualificationStatementInfo',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      fieldsExistDocuments: [
        { key: 'type_doc',
          label: this.$i18n.t('typeDoc'),
          sortable: true
        },
        { key: 'info',
          label: this.$i18n.t('data'),
          sortable: true,
          tdClass: 'ellipsis'
        },
        { key: 'number',
          label: this.$i18n.t('number'),
          sortable: true
        },
        { key: 'name_issued',
          label: this.$i18n.t('issued'),
          sortable: true,
          tdClass: 'ellipsis'
        },
        { key: 'date_start',
          label: this.$i18n.t('dateIssue')
        },
        { key: 'date_end',
          label: this.$i18n.t('dateEnd')
        },
        { key: 'status',
          label: this.$i18n.t('status'),
          sortable: true
        }
      ],
      fieldsApplication: [
        { key: 'type_document',
          label: this.$i18n.t('typeDoc'),
          sortable: true
        },
        { key: 'document_descr',
          label: this.$i18n.t('nameDoc'),
          sortable: true
        },
        { key: 'standarts_text',
          label: this.$i18n.t('requirements'),
          sortable: true
        }
      ],
      fieldsExperience: [
        { key: 'experience_descr',
          label: this.$i18n.t('experience'),
          sortable: true
        },
        { key: 'standarts_text',
          label: this.$i18n.t('standards'),
          sortable: true
        },
        { key: 'status',
          label: this.$i18n.t('status'),
          sortable: true
        }
      ],
      API: process.env.VUE_APP_API,
      sortByA: 'status',
      sortDescA: true,
      getExperienceStatus,
      getDateFormat,
      hideDetailed,
      getStatus,
      checkAccess
    }
  },
  computed: {
    ...mapState({
      lang: state => state.main.lang,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    })
  },
  methods: {
    /** Generate document for application qualification */
    saveDocument () {
      const body = {
        statement_id: this.sailorDocument.id
      }
      this.$api.post('api/v1/docs/auth_statement_for_qualification/', body).then(response => {
        if (response.status === 'success') {
          window.open(`${this.API}docs/generate_statement_for_qualification/${response.data.token}`, '_blank')
        }
      })
    }
  }
}
