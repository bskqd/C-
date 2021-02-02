import SailorSQCWishesInfo from '@/views/Sailor/SailorSQCWishes/SailorSQCWishesInfo/SailorSQCWishesInfo.vue'
import { viewDetailedComponent, back, deleteConfirmation } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorSQCWishesDocument',
  components: {
    SailorSQCWishesInfo
  },
  data () {
    return {
      type: 'sailorSQCWishes',
      viewDetailedComponent,
      deleteConfirmation,
      checkAccess,
      back
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr'
    }),
    documentID () {
      return this.$route.params.documentID
    },
    sailorDocument () {
      return this.$store.getters.sailorDocumentByID({ type: 'sailorSQCWishes', id: Number(this.documentID) }) || {}
    }
  },
  methods: {
    deleteDocument () {
      deleteConfirmation(this).then(confirmation => {
        if (confirmation) {
          this.$api.delete(`api/v2/sailor/${this.id}/demand/${this.sailorDocument.id}/`).then(response => {
            if (response.code === 200 || response.code === 204) {
              this.$notification.success(this, this.$i18n.t('deletedDocument'))
              if (this.sailorDocument.status_document.id !== 86) {
                this.$store.commit('updateDataSailor', { type: 'sailorSQCWishes', value: response.data })
                this.$store.commit('decrementBadgeCount', {
                  child: 'sqcWishes',
                  parent: 'sqcAll'
                })
              } else {
                this.$store.commit('deleteDataSailor', { type: 'sailorSQCWishes', value: this.sailorDocument })
              }
              back('sqc-wishes')
            } else {
              this.$notification.error(this, this.$i18n.t('cantDeleteDoc'))
            }
          })
        }
      })
    },

    /**
     * Move wish to application SQC
     * @param row: selected row
     **/
    moveToApplicationSQC () {
      const body = {
        sailor_id: this.id,
        demand_id: this.sailorDocument.id
      }
      this.$api.post(`api/v2/sailor/${this.id}/demand/${this.sailorDocument.id}/create_statement/`, body).then(response => {
        if (response.status === 'success') {
          this.$notification.success(this, this.$i18n.t('moveSailorWish'))
          this.$store.dispatch('getWishesSQC', this.id)
          this.$store.dispatch('getSQCStatements', this.id)
          this.$store.commit('decrementBadgeCount', {
            child: 'sqcWishes',
            parent: 'sqcAll'
          })
          this.$store.commit('incrementBadgeCount', {
            child: 'sqcStatement',
            parent: 'sqcAll'
          })
        }
      })
    },

    /** Update seafarer wish list info */
    updateWishList () {
      const body = {
        sailor: parseInt(this.id)
      }
      this.$api.patch(`api/v2/sailor/${this.id}/demand/${this.sailorDocument.id}/`, body).then(response => {
        if (response.status === 'success') {
          this.$notification.success(this, this.$i18n.t('updateSailorWish'))
          this.$store.dispatch('getWishesSQC', this.id)
        }
      })
    }
  }
}
