import SailorSQCWishesAdd from './SailorSQCWishesAdd/SailorSQCWishesAdd.vue'
import { mapState } from 'vuex'

export default {
  name: 'SailorSQCWishes',
  components: {
    SailorSQCWishesAdd
  },
  data () {
    return {
      fields: [
        { key: 'date_create',
          label: this.$i18n.t('createDate')
        },
        { key: 'rank',
          label: `${this.$i18n.t('qualification')} - ${this.$i18n.t('rank')}`
        },
        { key: 'list_positions',
          label: this.$i18n.t('position')
        },
        { key: 'status_document',
          label: this.$i18n.t('status'),
          tdClass: 'status-table'
        },
        { key: 'event',
          label: this.$i18n.t('actions'),
          class: 'mw-0 position-relative'
        }
      ],
      sortBy: 'rank',
      newDoc: false,
      sortDesc: true
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      items: state => state.sailor.sailorSQCWishes,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    })
  },
  methods: {
    // /** Get all wishes by Seafarer */
    // getWishesSQC () {
    //   this.tableLoader = true
    //   this.$api.get(`api/v2/sailor/${this.id}/demand/`).then(response => {
    //     this.tableLoader = false
    //     if (response.status === 'success') {
    //       response.data.map(item => {
    //         item.behavior = {}
    //         item.photo = getFilesFromData(item.photo)
    //         item._list_positions = item.list_positions.map(value => value[this.labelName])
    //       })
    //       this.items = response.data
    //     }
    //   })
    // },

    // /**
    //  * Delete the wish by Seafarer
    //  * @param row: selected row
    //  **/
    // deleteSeafarerWish (row) {
    //   deleteConfirmation(this).then(confirmation => {
    //     if (confirmation) {
    //       this.$api.delete(`api/v2/sailor/${this.id}/demand/${row.item.id}/`).then(response => {
    //         if (response.status === 'deleted') {
    //           this.$notification.success(this, this.$i18n.t('deleteNewWish'))
    //           this.getWishesSQC()
    //           this.$store.commit('decrementBadgeCount', {
    //             child: 'sqcWishes',
    //             parent: 'sqcAll'
    //           })
    //         }
    //       })
    //     }
    //   })
    // }
  }
}
