import { mapState } from 'vuex'

export default {
  name: 'SelectSex',
  prop: ['value'],
  data () {
    return {
      sex: this.value
    }
  },
  computed: {
    ...mapState({
      token: state => state.main.token,
      lang: state => state.main.lang,
      langSex: state => state.main.lang === 'en' ? 'value_eng' : 'value_ukr',
      mappingSex: state => state.directory.sex
    })
  },
  methods: {
    handleSelect (e) {
      this.$emit('input', this.sex)
    }
  }
}
