import { mapState } from 'vuex'

export default {
  name: 'SignatureKey',
  data () {
    return {
      passwordSign: null,
      fileSign: null,
      errorFileSign: false,
      passwordStamp: null,
      fileStamp: null,
      errorFileStamp: false,
      serverOptions: [
        { 'issuerCNs': 'АЦСК ТОВ "Центр сертифікації ключів "Україна"',
          'address': 'uakey.com.ua',
          'ocspAccessPointAddress': 'uakey.com.ua/services/ocsp/',
          'ocspAccessPointPort': '80',
          'cmpAddress': 'uakey.com.ua',
          'tspAddress': 'uakey.com.ua',
          'tspAddressPort': '80',
          'directAccess': true,
          'cmpCompatibility': 3
        },
        { 'issuerCNs': 'Акредитований центр сертифікації ключів ІДД ДФС',
          'address': 'acskidd.gov.ua',
          'ocspAccessPointAddress': 'acskidd.gov.ua/services/ocsp/',
          'ocspAccessPointPort': '80',
          'cmpAddress': 'acskidd.gov.ua',
          'tspAddress': 'acskidd.gov.ua',
          'tspAddressPort': '80',
          'directAccess': true
        },
        { 'issuerCNs': 'АЦСК органів юстиції України',
          'address': 'ca.informjust.ua',
          'ocspAccessPointAddress': 'ca.informjust.ua/services/ocsp/',
          'ocspAccessPointPort': '80',
          'cmpAddress': 'ca.informjust.ua',
          'tspAddress': 'ca.informjust.ua',
          'tspAddressPort': '80',
          'directAccess': true
        },
        { 'issuerCNs': 'Акредитований центр сертифікації ключів Укрзалізниці',
          'address': 'csk.uz.gov.ua',
          'ocspAccessPointAddress': 'csk.uz.gov.ua/services/ocsp/',
          'ocspAccessPointPort': '80',
          'cmpAddress': 'csk.uz.gov.ua',
          'tspAddress': 'csk.uz.gov.ua',
          'tspAddressPort': '80'
        },
        { 'issuerCNs': 'АЦСК "MASTERKEY" ТОВ "АРТ-МАСТЕР"',
          'address': 'masterkey.ua',
          'ocspAccessPointAddress': 'ocsp.masterkey.ua/services/ocsp/',
          'ocspAccessPointPort': '80',
          'cmpAddress': 'masterkey.ua',
          'tspAddress': 'tsp.masterkey.ua/services/tsp/',
          'tspAddressPort': '80'
        },
        { 'issuerCNs': 'АЦСК ТОВ "КС"',
          'address': 'ca.ksystems.com.ua',
          'ocspAccessPointAddress': 'ca.ksystems.com.ua/services/ocsp/',
          'ocspAccessPointPort': '80',
          'cmpAddress': 'ca.ksystems.com.ua',
          'tspAddress': 'ca.ksystems.com.ua',
          'tspAddressPort': '80'
        },
        { 'issuerCNs': 'АЦСК ДП "УСС"',
          'address': 'csk.uss.gov.ua',
          'ocspAccessPointAddress': 'csk.uss.gov.ua/services/ocsp/',
          'ocspAccessPointPort': '80',
          'cmpAddress': 'csk.uss.gov.ua',
          'tspAddress': 'csk.uss.gov.ua',
          'tspAddressPort': '80',
          'directAccess': true
        },
        { 'issuerCNs': 'АЦСК Публічного акціонерного товариства "УкрСиббанк"',
          'address': 'csk.ukrsibbank.com',
          'ocspAccessPointAddress': 'csk.ukrsibbank.com/services/ocsp/',
          'ocspAccessPointPort': '80',
          'cmpAddress': 'csk.ukrsibbank.com',
          'tspAddress': 'csk.ukrsibbank.com',
          'tspAddressPort': '80'
        },
        { 'issuerCNs': 'АЦСК АТ КБ "ПРИВАТБАНК"',
          'address': 'acsk.privatbank.ua',
          'ocspAccessPointAddress': 'acsk.privatbank.ua/services/ocsp/',
          'ocspAccessPointPort': '80',
          'cmpAddress': 'acsk.privatbank.ua',
          'tspAddress': 'acsk.privatbank.ua',
          'tspAddressPort': '80',
          'directAccess': true
        },
        { 'issuerCNs': 'Акредитований Центр сертифікації ключів Збройних Сил',
          'address': 'ca.mil.gov.ua',
          'ocspAccessPointAddress': 'ca.mil.gov.ua/services/ocsp/',
          'ocspAccessPointPort': '80',
          'cmpAddress': 'ca.mil.gov.ua',
          'tspAddress': 'ca.mil.gov.ua',
          'tspAddressPort': '80'
        },
        { 'issuerCNs': 'АЦСК Державної прикордонної служби України',
          'address': 'acsk.dpsu.gov.ua',
          'ocspAccessPointAddress': 'acsk.dpsu.gov.ua/services/ocsp/',
          'ocspAccessPointPort': '80',
          'cmpAddress': 'acsk.dpsu.gov.ua',
          'tspAddress': 'acsk.dpsu.gov.ua',
          'tspAddressPort': '80'
        },
        { 'issuerCNs': 'АЦСК ринку електричної енергії',
          'address': 'acsk.oree.com.ua',
          'ocspAccessPointAddress': 'acsk.oree.com.ua/services/ocsp/',
          'ocspAccessPointPort': '80',
          'cmpAddress': 'acsk.oree.com.ua',
          'tspAddress': 'acsk.oree.com.ua',
          'tspAddressPort': '80'
        },
        { 'issuerCNs': 'КНЕДП - АЦСК МВС України',
          'address': 'ca.mvs.gov.ua',
          'ocspAccessPointAddress': 'ca.mvs.gov.ua/services/ocsp/',
          'ocspAccessPointPort': '80',
          'cmpAddress': 'ca.mvs.gov.ua',
          'tspAddress': 'ca.mvs.gov.ua',
          'tspAddressPort': '80'
        },
        { 'issuerCNs': 'АЦСК Національного банку України',
          'address': 'canbu.bank.gov.ua',
          'ocspAccessPointAddress': 'canbu.bank.gov.ua/services/ocsp/',
          'ocspAccessPointPort': '80',
          'cmpAddress': 'canbu.bank.gov.ua',
          'tspAddress': 'canbu.bank.gov.ua',
          'tspAddressPort': '80'
        },
        { 'issuerCNs': 'АЦСК Державної казначейської служби України',
          'address': 'acsk.treasury.gov.ua',
          'ocspAccessPointAddress': 'ocsp.treasury.gov.ua/OCSPsrv/ocsp',
          'ocspAccessPointPort': '80',
          'cmpAddress': '',
          'tspAddress': 'ocsp.treasury.gov.ua/TspHTTPServer/tsp',
          'tspAddressPort': '80',
          'certsInKey': true,
          'cmpCompatibility': 0
        },
        { 'issuerCNs': 'Акредитований центр сертифікації ключів ПАТ "НДУ"',
          'address': 'ca.csd.ua',
          'ocspAccessPointAddress': 'ca.csd.ua/public/ocsp',
          'ocspAccessPointPort': '80',
          'cmpAddress': 'ca.csd.ua/public/x509/cmp',
          'tspAddress': 'ca.csd.ua/public/tsa',
          'tspAddressPort': '80',
          'certsInKey': true,
          'cmpCompatibility': 3
        },
        { 'issuerCNs': 'АЦСК "eSign" ТОВ "Алтерсайн"',
          'address': 'ca.altersign.com.ua',
          'ocspAccessPointAddress': 'ca.altersign.com.ua/services/ocsp/',
          'ocspAccessPointPort': '80',
          'cmpAddress': '',
          'tspAddress': '',
          'tspAddressPort': '',
          'cmpCompatibility': 0
        },
        { 'issuerCNs': 'АЦСК ДП "Український інститут інтелектуальної власності"',
          'address': 'acsk.uipv.org',
          'ocspAccessPointAddress': 'ocsp.acsk.uipv.org',
          'ocspAccessPointPort': '80',
          'cmpAddress': '',
          'tspAddress': '',
          'tspAddressPort': '',
          'cmpCompatibility': 0
        },
        { 'issuerCNs': 'Акредитований центр сертифікації ключів АТ "Ощадбанк"',
          'address': 'ca.oschadbank.ua',
          'ocspAccessPointAddress': 'ca.oschadbank.ua/public/ocsp',
          'ocspAccessPointPort': '80',
          'cmpAddress': '',
          'tspAddress': 'ca.oschadbank.ua/public/tsa',
          'tspAddressPort': '80',
          'certsInKey': true,
          'cmpCompatibility': 0
        },
        { 'issuerCNs': 'АЦСК Генеральної прокуратури України',
          'address': 'ca.gp.gov.ua',
          'ocspAccessPointAddress': 'ca.gp.gov.ua/ocsp',
          'ocspAccessPointPort': '80',
          'cmpAddress': 'ca.gp.gov.ua/cmp',
          'tspAddress': 'ca.gp.gov.ua/tsp',
          'tspAddressPort': '80',
          'certsInKey': true,
          'cmpCompatibility': 1
        }
      ],
      server:
        { 'issuerCNs': 'АЦСК ТОВ "Центр сертифікації ключів "Україна"',
          'address': 'uakey.com.ua',
          'ocspAccessPointAddress': 'uakey.com.ua/services/ocsp/',
          'ocspAccessPointPort': '80',
          'cmpAddress': 'uakey.com.ua',
          'tspAddress': 'uakey.com.ua',
          'tspAddressPort': '80',
          'directAccess': true,
          'cmpCompatibility': 3
        }
    }
  },
  computed: {
    ...mapState({
      permissionSuperAdmin: state => state.main.permissions.superAdmin,
      permissionWriteStamp: state => state.main.permissions.writeStamp,
      signatureKey: state => state.main.signatureKey
    })
  },
  methods: {
    closeSignatureKey () {
      this.$store.commit('setViewSignatureKey', { status: false, key: null, signAccess: null })
    },
    checkFileNameSign () {
      let fileNameSign = this.fileSign.name.split('.')[0]
      switch (true) {
        case fileNameSign.includes('DS'):
        case fileNameSign.includes('BS'):
          this.errorFileSign = false
          break
        case fileNameSign.includes('S') && (!fileNameSign.includes('DS') || !fileNameSign.includes('BS')):
        case fileNameSign.includes('U'):
        default:
          this.errorFileSign = true
      }
    },
    checkFileNameStamp () {
      let fileNameStamp = this.fileStamp.name.split('.')[0]
      switch (true) {
        case fileNameStamp.includes('S'):
        case fileNameStamp.includes('U'):
          this.errorFileStamp = false
          break
        case fileNameStamp.includes('DS'):
        case fileNameStamp.includes('BS'):
        default:
          this.errorFileStamp = true
      }
    },
    readKeyFile () {
      if (this.signatureKey.signAccess && this.permissionWriteStamp) {
        // Если секретарь указан в документе и есть право на добавление печати
        this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.readKey(this.fileStamp, this.passwordStamp, this.server, false)
        this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.readKey(this.fileSign, this.passwordSign, this.server, true)
      } else if (this.permissionWriteStamp && !this.signatureKey.signAccess) {
        // Если секретарь не указан в документе но есть право на добавление печати
        this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.readKey(this.fileStamp, this.passwordStamp, this.server, false)
      } else if (this.signatureKey.signAccess && !this.permissionWriteStamp) {
        // Если секретарь указан в документе но нет права на добавление печати
        this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.readKey(this.fileSign, this.passwordSign, this.server, true)
      }
    },
    signDocFile () {
      if (this.signatureKey.signAccess && this.permissionWriteStamp) {
        // Если секретарь указан в документе и есть право на добавление печати
        this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.readKey(this.fileStamp, this.passwordStamp, this.server, false)
        this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.signFile(false)
        this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.readKey(this.fileSign, this.passwordSign, this.server, true)
        this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.signFile(true)
      } else if (this.permissionWriteStamp && !this.signatureKey.signAccess) {
        // Если секретарь не указан в документе но есть право на добавление печати
        this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.signFile(false)
      } else if (this.signatureKey.signAccess && !this.permissionWriteStamp) {
        // Если секретарь указан в документе но нет права на добавление печати
        this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.signFile(true)
      }
    },
    goBackSign () {
      this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.loadKey = false
      this.$parent.$refs.protocolsSQC.$refs.protocolSQCInfo.$refs.signature.loadStamp = false
      this.fileSign = null
      this.passwordSign = null
      this.fileStamp = null
      this.passwordStamp = null
    }
  }
}
