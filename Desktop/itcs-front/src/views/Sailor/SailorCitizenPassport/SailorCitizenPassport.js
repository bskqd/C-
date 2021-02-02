import SeafarerCitizenPassportInfo from './SailorCitizenPassportInfo/SailorCitizenPassportInfo.vue'
import SeafarerCitizenPassportEdit from './SailorCitizenPassportEdit/SailorCitizenPassportEdit.vue'
import ViewPhotoList from '@/components/atoms/ViewPhotoList'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorCitizenPassport',
  components: {
    SeafarerCitizenPassportInfo,
    SeafarerCitizenPassportEdit,
    ViewPhotoList
  },
  data () {
    return {
      item: {},
      readonly: true,
      cardLoader: false,
      checkAccess
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      token: state => state.main.token,
      lang: state => state.main.lang
    })
  },
  mounted () {
    this.getPassport()
  },
  methods: {
    getPassport () {
      this.cardLoader = true
      this.$api.get(`api/v2/sailor/${this.id}/citizen_passport/`)
        .then(response => {
          this.cardLoader = false
          if (response.status === 'success') {
            // try {
            //   response.data[0].photo = getFilesFromData(response.data[0].photo)
            // } catch (e) {
            //   console.log(e)
            // }

            this.item = response.data.length ? response.data[0] : {}

            if (Object.keys(this.item).length &&
              (!this.item.country || !this.item.issued_by || !this.item.photo.length)) {
              this.$store.commit('setCitizenPassportBadgeCount', 0)
            } else this.$store.commit('setCitizenPassportBadgeCount', 1)
          }
        })
    },

    /**
    * Check validation form
    **/
    checkInfo () {
      this.$refs.SeafarerCitizenPassEdit.checkInfo()
    },

    /**
     * Click cancel in edit passport info or get new info after save new passport data
     **/
    finishEdit () {
      this.getPassport()
      this.readonly = true
    }
  }
}
