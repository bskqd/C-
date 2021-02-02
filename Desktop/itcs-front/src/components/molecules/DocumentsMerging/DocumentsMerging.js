import SailorEducationInfo from '@/views/Sailor/SailorEducation/SailorEducationInfo/SailorEducationInfo.vue'
import SailorQualificationInfo from '@/views/Sailor/SailorQualification/SailorQualificationInfo/SailorQualificationInfo.vue'
import { checkAccess } from '@/mixins/permissions'

export default {
  name: 'DocumentsMerging',
  props: {
    sailorID: [String, Number],
    type: String,
    documents: Array
  },
  components: {
    SailorEducationInfo,
    SailorQualificationInfo
  },
  data () {
    return {
      documentFrom: null,
      documentTo: null,
      checkAccess
    }
  },
  beforeCreate () {
    this.$store.commit('setActivePage', { name: 'home', access: checkAccess('documents-merging') })
  },
  mounted () {
    this.documents.sort((a, b) => a.item.id > b.item.id ? 1 : -1)
    this.documentFrom = this.documents[0].item
    this.documentTo = this.documents[1].item
    console.log('from', this.documentFrom.id, 'to', this.documentTo.id)
  },
  methods: {
    mergeDocuments () {
      const body = {
        sailor_key: this.sailorID,
        content_type: this.type,
        old_document: this.documentFrom.id,
        new_document: this.documentTo.id
      }
      if (this.type === 'qualification') {
        body.content_type = this.documentFrom.type_document.id === 16 ? 'proofofworkdiploma' : 'qualificationdocument'
      }
      this.$api.post(`api/v1/back_off/merge_documents/`, body).then(response => {
        if (response.status === 'success') {
          this.$notification.success(this, this.$i18n.t('successMerge'))
          if (this.type === 'education') {
            this.$router.push({ name: 'education-documents', params: { id: this.sailorID } })
            this.$store.dispatch('getEducationDocs', this.id)
          } else {
            this.$router.push({ name: 'qualification-documents', params: { id: this.sailorID } })
            this.$store.dispatch('getQualificationDocuments', this.id)
          }
        }
      })
    }
  }
}
