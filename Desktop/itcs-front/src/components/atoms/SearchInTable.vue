<template>
  <b-form-group
    label-align-sm="left"
    label-size="sm"
    :label-for="$t('search')"
    class="mb-0 w-full"
  >
    <b-input-group size="sm w-full pr-1">
      <b-icon icon="search" class="inline-block search-icon--seafarer"/>
      <input
          :value="value"
          @input="setValue($event)"
          :placeholder="$t('search')"
          class="input-rounded-full w-full ml-1"
        />
      <b-form-datepicker
          :value="value"
          @input="setDate($event)"
          :locale="lang"
          start-weekday="1"
          max="2200-12-31"
          min="1900-01-01"
          class="inline-block date-icon date-icon--seafarer position-absolute"
          button-only
          right
        />
    </b-input-group>
  </b-form-group>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'SearchInTable',
  props: {
    value: [String, Number]
  },
  computed: {
    ...mapState({
      lang: state => state.main.lang
    })
  },
  methods: {
    setDate (e) {
      this.$emit('input', e)
    },
    setValue (e) {
      this.$emit('input', e.target.value)
    }
  }
}
</script>
