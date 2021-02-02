import SailorSQCStatementTableChanges from '@/views/Sailor/SailorSQCStatement/SailorSQCStatementTableChanges/SailorSQCStatementTableChanges.vue'
import { getStatus, regenerationConfirmation, getExperienceStatus, getDateFormat } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorSQCStatementInfo',
  props: {
    sailorDocument: Object
  },
  components: {
    SailorSQCStatementTableChanges
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
          label: `${this.$i18n.t('position')} / ${this.$i18n.t('nameInstitution')}`,
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
      API: process.env.VUE_APP_API,
      sortByA: 'status',
      sortDescA: true,
      getExperienceStatus,
      getDateFormat,
      getStatus,
      checkAccess
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    })
  },
  methods: {
    /** Save new document */
    saveDocument () {
      const body = {
        statement_id: this.sailorDocument.id
      }
      this.$api.post(`api/v1/docs/auth_statement_for_dkk/`, body).then(response => {
        if (response.status === 'success') {
          window.open(`${this.API}docs/generate_statement_for_dkk/${response.data.token}`, '_blank')
        }
      })
    },

    /** Regenerate statement */
    regenerateApplication () {
      regenerationConfirmation(this).then(confirmation => {
        if (confirmation) {
          this.$api.get(`api/v2/sailor/${this.id}/statement/protocol_sqc/${this.sailorDocument.id}/regenerate_related_docs/`).then(response => {
            switch (response.status) {
              case 'success':
                this.$store.dispatch('getSQCStatements', this.id)
                break
              case 'error':
                if (response.data[0] === 'Document does not have related docs') {
                  this.$notification.error(this, this.$i18n.t('noRelatedDocs'))
                }
                break
            }
          })
        }
      })
    }
  }
}
