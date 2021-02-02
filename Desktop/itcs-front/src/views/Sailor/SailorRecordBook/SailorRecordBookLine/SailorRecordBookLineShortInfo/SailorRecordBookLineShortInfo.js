import SailorRecordBookLineInfo from '@/views/Sailor/SailorRecordBook/SailorRecordBookLine/SailorRecordBookLineInfo/SailorRecordBookLineInfo.vue'
import ViewPhotoList from '@/components/atoms/ViewPhotoList.vue'
import { hideDetailed } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'

export default {
  name: 'SailorRecordBookLineShortInfo',
  props: {
    row: Object
  },
  components: {
    SailorRecordBookLineInfo,
    ViewPhotoList
  },
  data () {
    return {
      type: 'serviceRecordBookLineShortInfo',
      hideDetailed,
      checkAccess
    }
  }
}
