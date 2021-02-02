<template>
  <div class="d-flex flex-wrap justify-content-center pt-3">
    <div
      v-for="photo of photoArray"
      :key="photo.id"
      class="deleted-document-block"
    >
      <unicon
        v-if="photo.id && !btnDelete.includes(documentType) && checkAccess(documentType, 'deleteFile', sailorDocument, photo)"
        @click="deleteDocument(photo)"
        name="multiply"
        fill="#42627e"
        height="25px"
        width="25px"
        class="deleted-document-icon"
      />
      <a
        :href="photo.url"
        target="_blank"
        class="d-block"
      >
        <div style="position: relative;">
          <img
            :src="photo.url"
            :alt="documentType"
            width="400"
            class="d-block"
            style="max-width: 100%"
          />
          <span
            v-if="photo.isDeleted"
            class="deleted-document-text"
          >
            {{ $t('deleted') }}
          </span>
        </div>
        <p class="deleted-document-name">
          {{ photo.photoName }}
        </p>
      </a>
    </div>
  </div>
</template>

<script>
import { checkAccess } from '@/mixins/permissions'
import { deleteConfirmation, getFilesFromData } from '@/mixins/main'
import { mapState } from 'vuex'

export default {
  name: 'ViewPhotoList',
  props: {
    sailorDocument: Object,
    documentType: String
  },
  data () {
    return {
      btnDelete: ['civilPassport', 'newAgents', 'newAccounts', 'agentStatements', 'serviceRecordBookLineShortInfo'],
      photoArray: [],
      photoTypeDoc: null,
      getFunctionName: null,
      checkAccess
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId
    })
  },
  mounted () {
    this.photoArray = getFilesFromData(this.sailorDocument.photo)
    switch (this.documentType) {
      case 'sailorPassport':
        this.getFunctionName = 'getSailorPassport'
        this.photoTypeDoc = 'SeafarerPassDoc'
        break
      case 'sailorFullNameChanges':
        this.getFunctionName = 'getFullNameChanges'
        this.photoTypeDoc = 'OldName'
        break
      case 'sailorPassportStatement':
        this.getFunctionName = 'getSailorPassportStatements'
        this.photoTypeDoc = 'StatementSailorPassport'
        break
      case 'education':
        this.getFunctionName = 'getEducationDocs'
        this.photoTypeDoc = 'GraduationDoc'
        break
      case 'student':
        this.getFunctionName = 'getStudentCard'
        this.photoTypeDoc = 'StudentCard'
        break
      case 'educationStatement':
        this.getFunctionName = 'getGraduationStatements'
        this.photoTypeDoc = 'StatementAdvancedTraining'
        break
      case 'qualification':
        this.getFunctionName = 'getQualificationDocuments'
        if (this.sailorDocument.type_document.id === 16) {
          this.photoTypeDoc = 'ProofOfWorkDiploma'
        } else {
          this.photoTypeDoc = 'QualificationDoc'
        }
        break
      case 'qualificationStatement':
        this.getFunctionName = 'getQualificationStatements'
        this.photoTypeDoc = 'StatementQualificationDoc'
        break
      case 'serviceRecordBook':
        this.getFunctionName = 'getRecordBooks'
        this.photoTypeDoc = 'RecordBookDoc'
        break
      case 'serviceRecordBookLine':
        this.getFunctionName = 'getRecordBooks'
        this.photoTypeDoc = 'ExperienceDoc'
        break
      case 'experience':
        this.getFunctionName = 'getExperienceReferences'
        this.photoTypeDoc = 'ExperienceDoc'
        break
      case 'recordBookStatement':
        this.getFunctionName = 'getRecordBookStatement'
        this.photoTypeDoc = 'StatementServiceRecord'
        break
      case 'sailorSQCStatement':
        this.getFunctionName = 'getSQCStatements'
        this.photoTypeDoc = 'StatementSqp'
        break
      case 'sailorSQCProtocols':
        this.getFunctionName = 'getProtocolsSQC'
        this.photoTypeDoc = 'ProtoclsSQCDoc'
        break
      case 'sailorMedical':
        this.getFunctionName = 'getMedicalCertificates'
        this.photoTypeDoc = 'MedicalDoc'
        break
      case 'medicalStatement':
        this.getFunctionName = 'getMedicalStatements'
        this.photoTypeDoc = 'StatementMedicalCertificate'
        break
      case 'positionStatement':
        this.getFunctionName = 'getPositionStatements'
        this.photoTypeDoc = 'PacketItem'
        break
    }
  },
  methods: {
    /** Delete documents */
    deleteDocument (file) {
      deleteConfirmation(this).then(confirmation => {
        if (confirmation) {
          this.$api.deletePhoto(this, file.id).then(response => {
            if (response.status === 'deleted') {
              this.$notification.success(this, this.$i18n.t('deletedDocument'))
              this.$store.dispatch(this.getFunctionName, this.id)
            } else {
              this.$notification.error(this, this.$i18n.t('cantDeleteDoc'))
            }
          })
        }
      })
    }
  }
}
</script>
