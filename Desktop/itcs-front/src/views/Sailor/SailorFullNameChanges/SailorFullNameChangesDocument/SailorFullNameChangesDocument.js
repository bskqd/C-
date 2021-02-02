import SailorFullNameChangesInfo from '@/views/Sailor/SailorFullNameChanges/SailorFullNameChangesInfo/SailorFullNameChangesInfo.vue'
import SailorFullNameChangesEdit from '@/views/Sailor/SailorFullNameChanges/SailorFullNameChangesEdit/SailorFullNameChangesEdit.vue'
import ViewPhotoList from '@/components/atoms/ViewPhotoList.vue'
import { viewDetailedComponent, back, deleteConfirmation } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'SailorFullNameChangesDocument',
  components: {
    SailorFullNameChangesInfo,
    SailorFullNameChangesEdit,
    ViewPhotoList
  },
  data () {
    return {
      type: 'sailorFullNameChanges',
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
      return this.$store.getters.sailorDocumentByID({ type: 'sailorFullNameChanges', id: Number(this.documentID) }) || {}
    }
  },
  methods: {
    deleteDocument () {
      deleteConfirmation(this).then(confirmation => {
        if (confirmation) {
          this.$api.delete(`api/v2/sailor/${this.id}/old_name/${this.sailorDocument.id}/`).then(response => {
            if (response.status === 'deleted') {
              this.$notification.success(this, this.$i18n.t('deletedDocument'))
              this.$store.dispatch('getFullNameChanges', this.id)
              this.$store.dispatch('getSailorInformation', this.id)
              back('passports-changes')
            } else {
              this.$notification.error(this, this.$i18n.t('cantDeleteDoc'))
            }
          })
        }
      })
    }
  }
}
