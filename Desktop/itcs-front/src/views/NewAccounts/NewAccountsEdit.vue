<template>
  <b-card header-tag="header">
    <div
      v-if="!sailorDocument.sailor_id"
      class="flex-row-sb wrap m-1"
    >
      <label>{{ $t('sailorId') }}</label>
      <b-input
        v-model="sailorId"
        :placeholder="$t('sailorId')"
        type="text"
        class="form-control"
        />
    </div>

    <div class="flex-row-sb wrap m-1">
      <label>{{ $t('status') }}</label>
      <multiselect
        v-model="status"
        :options="statusesList(sailorDocument.sailor_id)"
        :searchable="true"
        :placeholder="$t('status')"
        :allow-empty="false"
        :label="labelName"
        track-by="id"
      />
    </div>

    <b-overlay
      :show="buttonLoader"
      spinner-variant="primary"
      opacity="0.65"
      blur="2px"
      variant="white"
      class="w-100"
      spinner-small
    >
      <b-button
        @click="dateConfirmation"
        variant="success"
      >
        {{ $t('save') }}
      </b-button>
    </b-overlay>
  </b-card>
</template>

<script>
import { mapState } from 'vuex'
import { back } from '@/mixins/main'

export default {
  name: 'NewAccountsEdit',
  props: {
    sailorDocument: Object,
    getDocuments: Function
  },
  data () {
    return {
      buttonLoader: false,
      sailorId: this.sailorDocument.sailor_id,
      status: this.sailorDocument.status_document,
      back
    }
  },
  computed: {
    ...mapState({
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr'
    })
  },
  mounted () {
    this.getBirthDay()
  },
  methods: {
    statusesList (sailorID) {
      let statuses = this.$store.getters.statusChoose('User')
      if (sailorID) {
        return statuses
      } else {
        return statuses.filter(value => value.id !== 41)
      }
    },

    saveStatus () {
      this.buttonLoader = true
      const body = {
        status_document: this.status.id,
        sailor_id: this.sailorId || null
      }
      this.$api.patch(`api/v1/sms_auth/list_verification/${this.sailorDocument.id}/`, body).then(response => {
        this.buttonLoader = false
        switch (response.status) {
          case 'success':
            this.getDocuments()
            if (response.data.status_document.id === 36) {
              this.$notification.success(this, this.$i18n.t('rejectedStatement'))
            } else if (response.data.status_document.id === 41) {
              this.$notification.success(this, this.$i18n.t('verificationAccSuccess'))
            }

            if (response.data.status_document.id !== 34) back('new-accounts')
            break
          case 'error':
            if (response.data.error === 'Sailor has user') {
              this.$notification.error(this, this.$i18n.t('sailorHasUser'))
            }
            break
        }
      })
    },

    dateConfirmation () {
      if (this.sailorDocument.sailor_id && (this.sailorDocument.status_document.id === 41) &&
        (this.sailorDocument.sailorDateBirth !== this.sailorDocument.birthday)) {
        this.$swal({
          title: this.$i18n.t('notSimilarDate'),
          text: this.$i18n.t('continueVerification'),
          icon: 'warning',
          buttons: [this.$i18n.t('cancel'), this.$i18n.t('confirm')],
          dangerMode: true
        }).then((confirmation) => {
          if (confirmation) {
            this.saveStatus()
          }
        })
      } else this.saveStatus()
    },

    getBirthDay () {
      if (this.sailorDocument.sailor_id) {
        this.$api.get(`api/v2/sailor/${this.sailorDocument.sailor_id}/short/`).then(response => {
          if (response.status === 'success') {
            this.sailorDocument.sailorDateBirth = response.data.date_birth
          }
        })
      }
    }
  }
}
</script>
