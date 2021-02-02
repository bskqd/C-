import { hideDetailed, enterDoublePosition, mappingSQCPositions } from '@/mixins/main'
import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { required } from 'vuelidate/lib/validators'
import { mapGetters, mapState } from 'vuex'

function formFieldsInitialState () {
  return {
    newRank: null,
    newPosition: []
  }
}

export default {
  name: 'SailorSQCWishesAdd',
  components: {
    ValidationAlert
  },
  data () {
    return {
      dataForm: formFieldsInitialState(),
      buttonLoader: false,
      enterDoublePosition,
      mappingSQCPositions,
      hideDetailed
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    }),
    ...mapGetters({
      ranks: 'ranksSQC'
    })
  },
  validations: {
    dataForm: {
      newRank: { required },
      newPosition: { required }
    }
  },
  methods: {
    /** check validation field */
    checkInfo () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else this.saveNewWish()
    },

    /**
     * Save new wish by Seafarer
     * @function checkInfo - validation fields
     * @function saveNewApplicationSQC - save application SQC
     **/
    saveNewWish () {
      this.buttonLoader = true
      const positions = this.dataForm.newPosition.map(value => value.id)
      const body = {
        sailor: this.id,
        rank: this.dataForm.newRank.id,
        list_positions: positions
      }
      this.$api.post(`api/v2/sailor/${this.id}/demand/`, body).then(response => {
        this.buttonLoader = false
        if (response.status === 'created') {
          this.$notification.success(this, this.$i18n.t('addNewWish'))
          this.$store.commit('addDataSailor', { type: 'sailorSQCWishes', value: response.data })
          this.$parent.viewAdd = false
          this.$data.dataForm = formFieldsInitialState()
          this.$v.$reset()
          this.$store.commit('incrementBadgeCount', {
            child: 'sqcWishes',
            parent: 'sqcAll'
          })
        }
      })
    },

    /** Remove second double-position if first was removed */
    removePosition (removedPosition) {
      const doublePositions = [106, 121, 122, 123]
      if (doublePositions.includes(removedPosition.rank)) {
        this.dataForm.newPosition.length = 0
      }
    }
  }
}
