import SailorCertificationStatementAdd from '@/views/Sailor/SailorCertificationStatement/SailorCertificationStatementAdd/SailorCertificationStatementAdd.vue'
import { mapState } from 'vuex'

export default {
  name: 'SailorCertificationStatement',
  components: {
    SailorCertificationStatementAdd
  },
  data () {
    return {
      fields: [
        { key: 'number',
          label: this.$i18n.t('number')
        },
        { key: 'date_create',
          label: this.$i18n.t('createDate')
        },
        { key: 'date_meeting',
          label: this.$i18n.t('meetingDate')
        },
        { key: 'institution',
          label: this.$i18n.t('nameInstitution')
        },
        { key: 'course',
          label: this.$i18n.t('course')
        },
        { key: 'is_payed',
          label: this.$i18n.t('payment')
        },
        { key: 'status_document',
          label: this.$i18n.t('status')
        },
        { key: 'event',
          label: this.$i18n.t('actions'),
          class: 'mw-0 position-relative'
        }
      ],
      sortBy: 'number',
      sortDesc: true,
      viewNewDoc: false
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      items: state => state.sailor.certificationStatement
    })
  }
  // mounted () {
  //   this.getCertificateStatements()
  // },
  // methods: {
  //   /** Get eti certificates statements */
  //   getCertificateStatements () {
  //     this.tableLoader = true
  //     this.$api.get(`api/v2/sailor/${this.id}/statement/certificate/`).then((response) => {
  //       this.tableLoader = false
  //       if (response.code === 200) {
  //         response.data.map(item => {
  //           item.behavior = {}
  //         })
  //         this.items = response.data
  //       }
  //     })
  //   },
  //
  //   /** Delete eti certificates statement */
  //   deleteCertificateStatement (row) {
  //     deleteConfirmation(this).then(confirmation => {
  //       if (confirmation) {
  //         this.$api.delete(`api/v2/sailor/${this.id}/statement/certificate/${row.item.id}`).then(response => {
  //           if (response.code === 204) {
  //             this.$notification.success(this, this.$i18n.t('etiStatementDeleted'))
  //             this.getCertificateStatements()
  //             this.$store.commit('decrementBadgeCount', {
  //               child: 'certificateStatement',
  //               parent: 'certificateAll'
  //             })
  //           }
  //         })
  //       }
  //     })
  //   }
  // }
}
