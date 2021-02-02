import { checkAccess } from '@/mixins/permissions'

export default {
  name: 'AgentsDocument',
  data () {
    return {
      fields: [
        { key: 'number',
          label: this.$i18n.t('number'),
          sortable: true
        },
        { key: 'typeDocument',
          label: this.$i18n.t('typeDoc'),
          sortable: true
        },
        { key: 'issued',
          label: this.$i18n.t('issued'),
          sortable: true
        },
        { key: 'event',
          label: this.$i18n.t('actions'),
          class: 'mw-0'
        }
      ],
      items: [],
      tableLoader: true,
      checkAccess
    }
  },
  beforeCreate () {
    this.$store.commit('setActivePage', { name: 'agentsDocument', access: checkAccess('menuItem-agentVerification') })
  },
  mounted () {
    this.getAgentsDocumentsForVerification()
  },
  methods: {
    getAgentsDocumentsForVerification () {
      this.tableLoader = true
      this.$api.get('api/v1/verification/seaman_document/').then(response => {
        this.tableLoader = false
        if (response.code === 200) {
          response.data.map(item => {
            item.typeDocument = item.type_document
            switch (item.content_type) {
              case 'servicerecord':
                item.link = 'experience-records-info'
                break
              case 'qualificationdocument':
              case 'proofofworkdiploma':
                item.link = 'qualification-documents-info'
                break
              case 'education':
                item.link = 'education-documents-info'
                break
              case 'medicalcertificate':
                item.link = 'medical-certificates-info'
                break
              case 'sailorpassport':
                item.link = 'passports-sailors-info'
                break
              case 'lineinservicerecord':
                if (item.service_record) {
                  item.link = 'experience-records-line-info'
                } else {
                  item.link = 'experience-reference-info'
                }
                break
            }
          })
          this.items = response.data
        }
      })
    }
  }
}
