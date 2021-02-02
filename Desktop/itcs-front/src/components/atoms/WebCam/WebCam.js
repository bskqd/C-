import { mapState } from 'vuex'

export default {
  name: 'WebCam',
  data () {
    return {
      webCam: null,
      detectWebCam: true,
      scans: [],
      activeCamera: [],
      allCameras: [],
      activeCameraId: '1'
    }
  },
  computed: {
    ...mapState({
      usingCompForScans: state => state.main.webCamView.comp,
      usingModel: state => state.main.webCamView.model
    })
  },
  mounted () {
    console.log(this)
    this.webCam = this.$refs.webCam
    this.checkCameras()
  },
  methods: {
    checkCameras () {
      try {
        this.detectWebCam = true
        this.allCameras = this.webCam.cameras
      } catch (e) {
        this.detectWebCam = false
        console.error(e)
      }
    },

    selectCamera (camera) {
      this.activeCameraId = camera.deviceId
    },

    takePhoto () {
      let photo = this.webCam.capture()

      let arr = photo.split(',')
      let mime = arr[0].match(/:(.*?);/)[1]
      let bstr = atob(arr[1])
      let n = bstr.length
      let u8arr = new Uint8Array(n)

      while (n--) {
        u8arr[n] = bstr.charCodeAt(n)
      }

      let name = 'scan-' + Date.now() + '.jpg'

      let file = new File([u8arr], name, { type: mime })

      this.scans.push({ src: photo, file: file })
    },

    deletePhotoScan (scan, scanIndex) {
      this.scans = this.scans.filter((val, index) => {
        if (index !== scanIndex) {
          return val
        }
      })
    },

    usePhoto () {
      console.log(this.scans)

      this.usingModel.scans = this.scans.map(val => {
        return val.file
      })

      console.log(this.usingModel.scans)

      this.closeWebCam()
    },

    closeWebCam () {
      this.$store.commit('setWebCamView', { status: false, comp: null, model: null })
      this.scans = []
    }
  }
}
