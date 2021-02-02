import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import FileDropZone from '@/components/atoms/DropZone/DropZone.vue'
import PhoneMaskInput from 'vue-phone-mask-input'
import { required, requiredIf, maxLength, minLength } from 'vuelidate/lib/validators'
import { mapState } from 'vuex'

function formFieldsInitialState () {
  return {
    deliveryType: null,
    city: null,
    warehouse: null,
    street: null,
    house: null,
    flat: null,
    phoneNumber: null,
    deliveryStreets: [],
    deliveryWarehouses: [],
    deliveryTypeList: [
      { id: 1, name_ukr: 'Нова пошта (самовивіз)', name_eng: 'Nova Poshta (self-pickup)', courier: false },
      { id: 2, name_ukr: 'Нова пошта (кур’єр)', name_eng: 'Nova Poshta (courier)', courier: true }
    ],
    buttonLoader: false
  }
}

export default {
  name: 'SailorRecordBookStatementAdd',
  components: {
    ValidationAlert,
    PhoneMaskInput,
    FileDropZone
  },
  data () {
    return {
      selectLoader: false,
      dataForm: formFieldsInitialState()
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      // mapping documents
      mappingDeliveryCities: state => state.directory.deliveryCities
    })
  },
  validations: {
    dataForm: {
      city: { required },
      warehouse: {
        required: requiredIf(function () {
          return this.dataForm.deliveryType.id === 1
        })
      },
      street: {
        required: requiredIf(function () {
          return this.dataForm.deliveryType.id === 2
        })
      },
      house: {
        required: requiredIf(function () {
          return this.dataForm.deliveryType.id === 2
        })
      },
      phoneNumber: { required, maxLength: maxLength(13), minLength: minLength(13) }
    }
  },
  methods: {
    /** Get delivery warehouses or streets by city id */
    getDeliveryInfo (id) {
      this.selectLoader = true
      this.dataForm.warehouse = null
      this.dataForm.street = null

      if (this.dataForm.deliveryType.id === 1) {
        this.$api.get(`api/v1/delivery/novaposhta_warehouse/${id}/`).then(response => {
          this.selectLoader = false
          if (response.status === 'success') {
            this.dataForm.deliveryWarehouses = response.data
          }
        })
      } else {
        this.$api.get(`api/v1/delivery/novaposhta_street/${id}/`).then(response => {
          this.selectLoader = false
          if (response.status === 'success') {
            this.dataForm.deliveryStreets = response.data
          }
        })
      }
    },

    /** Check field validation */
    checkInfo () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.addApplicationRB()
    },

    /** Add new record book application */
    addApplicationRB () {
      this.dataForm.buttonLoader = true
      const body = {
        sailor: this.id,
        type_post: 'novaposhta',
        phone_number: this.dataForm.phoneNumber,
        is_courier: this.dataForm.deliveryType.courier,
        city_id: this.dataForm.city.id,
        other_street: null,
        warehouse_id: this.dataForm.deliveryType.id === 1 ? this.dataForm.warehouse.id : null,
        street_id: this.dataForm.deliveryType.id === 1 ? null : this.dataForm.street.id,
        house: this.dataForm.deliveryType.id === 1 ? null : this.dataForm.house,
        apartment: this.dataForm.deliveryType.id === 1 ? null : this.dataForm.flat
      }
      this.$api.post(`api/v2/sailor/${this.id}/statement/service_record/`, body).then(response => {
        this.dataForm.buttonLoader = false
        if (response.status === 'created') {
          const files = this.$refs.mediaContent.filesArray
          if (files.length) {
            this.$api.postPhoto(files, 'StatementServiceRecord', response.data.id).then((response) => {
              if (response.status !== 'created' && response.status !== 'success') {
                this.$notification.error(this, this.$i18n.t('errorAddFile'))
              }
            })
          }

          this.$notification.success(this, this.$i18n.t('submittedStatementRB'))
          this.$store.commit('addDataSailor', { type: 'recordBookStatement', value: response.data })
          this.$parent.viewAdd = false
          this.$store.commit('incrementBadgeCount', {
            child: 'recordBookStatement',
            parent: 'experienceAll'
          })
          this.$store.commit('incrementUserNotification', 'statement_service_record')
          this.$data.dataForm = formFieldsInitialState()
          this.$v.$reset()
        }
      })
    }
  }
}
