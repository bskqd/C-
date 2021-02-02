import { getStatus, getExperienceStatus } from '@/mixins/main'

export default {
  name: 'SailorPositionStatementPreview',
  props: {
    row: Object
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
      fieldsNotExistDocuments: [
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
      fieldsExperience: [
        { key: 'experience_descr',
          label: this.$i18n.t('experience')
        },
        { key: 'standarts_text',
          label: this.$i18n.t('standards')
        },
        { key: 'status',
          label: this.$i18n.t('status')
        }
      ],
      experienceArr: [],
      existDocsArr: [],
      getExperienceStatus,
      getStatus
    }
  }
}
