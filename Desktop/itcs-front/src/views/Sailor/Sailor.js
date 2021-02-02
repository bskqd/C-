import SailorMainInfo from './SailorMainInfo/SailorMainInfo.vue'
import WebCam from '@/components/atoms/WebCam/WebCam.vue'
import SignatureKey from '@/components/molecules/Signature/SignatureKey/SignatureKey.vue'
import TabsList from '@/components/atoms/TabsList.vue'
import SailorContractUploading from './SailorContactUploading/SailorContactUploading.vue'
import SailorAgentInfo from './SailorAgentInfo/SeafarerAgentInfo.vue'

import { mapState } from 'vuex'
import { checkAccess } from '@/mixins/permissions'

export default {
  name: 'Sailor',
  // provide: function () {
  //   return {
  //     getUpdatedApplication: this.getUpdatedApplications
  //   }
  // },
  components: {
    TabsList,
    SailorMainInfo,
    WebCam,
    SignatureKey,
    SailorContractUploading,
    SailorAgentInfo
  },
  data () {
    return {
      checkAccess,
      API: process.env.VUE_APP_API,
      id: String(this.$router.currentRoute.params['id']),
      code: null,
      tabPassport: [
        { labelKey: 'sailorPassport',
          countDocKey: 'passportDocument',
          link: 'passports-sailors'
        },
        { labelKey: 'civilPassport',
          countDocKey: 'passportCitizen',
          link: 'passports-citizen'
        },
        { labelKey: 'surnameChanges',
          link: 'passports-changes'
        },
        { labelKey: 'model-StatementSailorPassport',
          countDocKey: 'passportStatement',
          link: 'passports-statements'
        }
      ],
      tabEducation: [
        { labelKey: 'mainDocs',
          countDocKey: 'educationDocument',
          link: 'education-documents'
        },
        { labelKey: 'student',
          countDocKey: 'studentCard',
          link: 'education-student'
        },
        { labelKey: 'advanceTrainingStatement',
          countDocKey: 'educationStatement',
          link: 'education-statements'
        }
      ],
      tabQualification: [
        { labelKey: 'qualificationDocs',
          countDocKey: 'qualificationDocument',
          link: 'qualification-documents'
        },
        { labelKey: 'statements',
          countDocKey: 'qualificationStatement',
          link: 'qualification-statements'
        }
      ],
      tabCertification: [
        { labelKey: 'eti',
          countDocKey: 'certificateDocument',
          link: 'certification-certificates'
        },
        { labelKey: 'statements',
          countDocKey: 'certificateStatement',
          link: 'certification-statements'
        }
      ],
      tabExperience: [
        { labelKey: 'recordBook',
          countDocKey: 'recordBookDocument',
          link: 'experience-records'
        },
        { labelKey: 'internship',
          countDocKey: 'experienceDocument',
          link: 'experience-reference'
        },
        { labelKey: 'recordBookStatement',
          countDocKey: 'recordBookStatement',
          link: 'experience-statements'
        }
      ],
      tabSQC: [
        { labelKey: 'statementSQC',
          countDocKey: 'sqcStatement',
          link: 'sqc-statements'
        },
        { labelKey: 'protocolsSQC',
          countDocKey: 'sqcDocument',
          link: 'sqc-protocols'
        },
        { labelKey: 'sailorWishes',
          countDocKey: 'sqcWishes',
          link: 'sqc-wishes'
        }
      ],
      tabMedicine: [
        { labelKey: 'certificates',
          countDocKey: 'medicalDocument',
          link: 'medical-certificates' },
        { labelKey: 'statements',
          countDocKey: 'medicalStatement',
          link: 'medical-statements' }
      ]
    }
  },
  computed: {
    ...mapState({
      tabsCount: state => state.main.badgesCount,
      viewWebCam: state => state.main.webCamView.status,
      registerCode: state => state.main.registerCode,
      signatureKey: state => state.main.signatureKey,
      isContractNeeded: state => state.main.isContractNeeded,
      isTrained: state => state.main.isTrained
    })
  },
  beforeCreate () {
    this.$store.commit('setActivePage', { name: 'home', access: true })
  },
  mounted () {
    this.getTrainingStatus()
  },
  beforeMount () {
    this.$store.commit('setSailorId', this.id)
    this.$store.dispatch('getCountBadges', this.id)
    this.$store.dispatch('getProtocolsForQualification', this.id)
    this.$store.dispatch('getSuccessQualificationStatement', this.id)
    this.$store.dispatch('getDiplomas', this.id)
    this.$store.dispatch('getSuccessStatementsSQC', this.id)
    this.$store.dispatch('getSailorPassportProcessing', this.id)
    this.$store.dispatch('getAvailablePositions', this.id)
    // Sailor Documents
    this.$store.dispatch('getSailorInformation', this.id)
    this.$store.dispatch('getSailorPassport', this.id)
    this.$store.dispatch('getFullNameChanges', this.id)
    this.$store.dispatch('getSailorPassportStatements', this.id)
    this.$store.dispatch('getEducationDocs', this.id)
    this.$store.dispatch('getStudentCard', this.id)
    this.$store.dispatch('getGraduationStatements', this.id)
    this.$store.dispatch('getQualificationDocuments', this.id)
    this.$store.dispatch('getQualificationStatements', this.id)
    this.$store.dispatch('getCertificates', this.id)
    this.$store.dispatch('getCertificateStatements', this.id)
    this.$store.dispatch('getRecordBooks', this.id)
    this.$store.dispatch('getExperienceReferences', this.id)
    this.$store.dispatch('getRecordBookStatement', this.id)
    this.$store.dispatch('getSQCStatements', this.id)
    this.$store.dispatch('getProtocolsSQC', this.id)
    this.$store.dispatch('getWishesSQC', this.id)
    this.$store.dispatch('getMedicalCertificates', this.id)
    this.$store.dispatch('getMedicalStatements', this.id)
    this.$store.dispatch('getPositionStatements', this.id)
    this.$store.dispatch('getApprovedSailorPassportStatements', this.id)
    this.$store.dispatch('getExistSailorPassports', this.id)
  },
  methods: {
    // codeRegistration () {
    //   this.$store.commit('setViewRegisterCode', { status: true, code: this.code })
    //   this.$refs.mainInfo.registerCode()
    // },
    //
    // /** Close registration code number div */
    // closeRegisterCord () {
    //   this.$store.commit('setViewRegisterCode', { status: false, code: null })
    // },

    getTrainingStatus () {
      this.$api.get('api/v1/auth/user_is_trained/').then(response => {
        if (response.code === 200) {
          this.$store.commit('setMainStateData', { type: 'isTrained', data: response.data.is_trained })
        }
      })
    }
  }
}
