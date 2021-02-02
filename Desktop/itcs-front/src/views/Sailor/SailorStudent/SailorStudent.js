import { mapState } from 'vuex'
import SailorStudentAdd from './SailorStudentAdd/SailorStudentAdd.vue'

export default {
  name: 'SailorStudent',
  components: {
    SailorStudentAdd
  },
  data () {
    return {
      fields: [
        { key: 'number',
          label: this.$i18n.t('number')
        },
        { key: 'date_start',
          label: this.$i18n.t('dataEnrollment')
        },
        { key: 'faculty',
          label: this.$i18n.t('faculty')
        },
        { key: 'name_nz',
          label: this.$i18n.t('nameInstitution')
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
      items: state => state.sailor.student
    })
  },
  methods: {
    // getStudentCard () {
    //   this.$api.get(`api/v1/cadets/students_id_per_sailor/${this.id}/`)
    //     .then(response => {
    //       this.tableLoader = false
    //       if (response.code === 200) {
    //         response.data.map((item) => {
    //           item.behavior = {}
    //           item.photo = getFilesFromData(item.photo)
    //         })
    //
    //         this.items = response.data
    //       }
    //     })
    // },
    //
    // deleteStudentCard (row) {
    //   this.$api.delete(`api/v1/cadets/student_id/${row.item.id}/`)
    //     .then(response => {
    //       if (response.code === 204) {
    //         this.$notification.success(this, this.$i18n.t('deletedStudentCard'))
    //         this.$store.commit('decrementBadgeCount', {
    //           child: 'studentCard',
    //           parent: 'educationAll'
    //         })
    //         this.getStudentCard()
    //       }
    //     })
    // }
  }
}
