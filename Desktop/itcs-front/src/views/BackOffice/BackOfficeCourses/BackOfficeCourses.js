import CoursesAdd from './BackOfficeCoursesAdd/BackOfficeCoursesAdd.vue'
import { viewDetailedBlock, showDetailed, goBack } from '@/mixins/main'

export default {
  name: 'BackOfficeCourses',
  components: {
    CoursesAdd
  },
  data () {
    return {
      fields: [
        { key: 'name_ukr',
          label: this.$i18n.t('nameInstitution'),
          sortable: true
        },
        { key: 'name_abbr',
          label: this.$i18n.t('abbreviation'),
          sortable: true
        },
        { key: 'event',
          label: this.$i18n.t('actions'),
          class: 'mw-0'
        }
      ],
      items: [],
      sortBy: 'nameInstitution',
      sortDesc: false,
      tableLoader: true,
      newDoc: false,
      showDetailed,
      viewDetailedBlock,
      goBack
    }
  },
  mounted () {
    this.getCoursesETI()
  },
  methods: {
    getCoursesETI () {
      this.tableLoader = true
      this.$api.get('api/v1/back_off/certificates/eti_registry/by_institution/').then(response => {
        this.tableLoader = false
        if (response.code === 200) {
          response.data.map((item) => {
            item.eti_registry.map(value => {
              value.behavior = {}
            })
            item.behavior = {}
          })
          this.items = response.data
        }
      })
    }
  }
}
