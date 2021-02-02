<template>
  <div class="seafarerInfoList">
    <div class="w-50">
      <b>{{ $t('createDate') }}:</b>
      {{ sailorDocument.created_at }}
    </div>
    <div class="w-50">
      <b>{{ $t('fullName') }}:</b>
      {{ sailorDocument.last_name }} {{ sailorDocument.first_name }} {{ sailorDocument.middle_name }}
    </div>
    <div class="w-33">
      <b>{{ $t('dateBorn') }}:</b>
      {{ getDateFormat(sailorDocument.birthday) }}
    </div>
    <div class="w-33">
      <b>{{ $t('taxNumber') }}:</b>
      {{ sailorDocument.inn }}
    </div>
    <div class="w-33">
      <b>{{ $t('passport') }}:</b>
      {{ sailorDocument.passport }}
    </div>
    <div class="w-50">
      <b>{{ $t('phoneNumber') }}:</b>
      {{ sailorDocument.phone }}
    </div>
    <div class="w-50">
      <b>{{ $t('email') }}:</b>
      {{ sailorDocument.email }}
    </div>
    <div class="w-100">
      <b>{{ $t('status') }}:</b>
      <span :class="getStatus(sailorDocument.status_document.id)">
        {{ sailorDocument.status_document[labelName] }}
      </span>
    </div>
  </div>
</template>

<script>
import { getStatus, getDateFormat } from '@/mixins/main'
import { mapState } from 'vuex'

export default {
  name: 'NewAccountsInfo',
  props: {
    sailorDocument: Object
  },
  data () {
    return {
      getDateFormat,
      getStatus
    }
  },
  computed: {
    ...mapState({
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    })
  }
}
</script>
