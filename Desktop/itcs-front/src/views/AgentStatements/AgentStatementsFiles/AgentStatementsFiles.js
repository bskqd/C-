import { hideDetailed, getFilesFromData } from '@/mixins/main'

export default {
  name: 'AgentStatementsFiles',
  props: {
    row: Object
  },
  data () {
    return {
      photoArray: [],
      hideDetailed
    }
  },
  mounted () {
    try {
      this.photoArray = getFilesFromData(this.row.item.photo)
    } catch (e) {
      console.log(e)
    }
  }
}
