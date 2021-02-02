<template>
  <b-card v-if="Object.keys(sailorDocument).length" header-tag="header">
    <template #header>
      <div class="flex-row-sb">
        <div class="text-uppercase text-left">
          {{ $t(`${Object.keys(sailorDocument.behavior)[0]}-${type}`) }}
          <span v-if="checkAccess('backOffice')">
            (ID: {{ sailorDocument.id }})
          </span>
        </div>
        <div class="documentIconControl">
          <router-link
            v-if="sailorDocument.sailor_id"
            :to="{ name: 'passports-sailors', params: { id: sailorDocument.sailor_id }}"
            target="_blank"
          >
            <unicon
              name="user-circle"
              fill="#42627e"
              height="25px"
              width="25px"
              class="cursor mr-4"
            />
          </router-link>
          <unicon
            @click="viewDetailedComponent(sailorDocument, 'viewInfoBlock')"
            name="info-circle"
            fill="#42627e"
            height="25px"
            width="25px"
            class="cursor mr-4"
          />
          <unicon
            v-if="checkAccess(type, 'edit', sailorDocument)"
            @click="viewDetailedComponent(sailorDocument, 'viewEditBlock')"
            name="pen"
            fill="#42627e"
            height="25px"
            width="25px"
            class="cursor mr-4"
          />
          <unicon
            v-if="checkAccess(type, 'files', sailorDocument)"
            @click="viewDetailedComponent(sailorDocument, 'viewFilesBlock')"
            name="scenery"
            fill="#42627e"
            height="25px"
            width="25px"
            class="cursor mr-4"
          />
          <unicon
            @click="back('new-accounts')"
            name="multiply"
            fill="#42627e"
            height="25px"
            width="25px"
            class="close"
          />
        </div>
      </div>
    </template>
    <NewAccountsInfo
      v-if="sailorDocument.behavior.viewInfoBlock"
      :sailorDocument="sailorDocument"/>

    <NewAccountsEdit
      v-if="sailorDocument.behavior.viewEditBlock"
      :getDocuments="getVerificationAccount"
      :sailorDocument="sailorDocument"/>

    <ViewPhotoList
      v-else-if="sailorDocument.behavior.viewFilesBlock"
      :sailorDocument="sailorDocument"
      :documentType="type"/>
  </b-card>
</template>

<script>
import NewAccountsInfo from '@/views/NewAccounts/NewAccountsInfo.vue'
import NewAccountsEdit from '@/views/NewAccounts/NewAccountsEdit.vue'
import ViewPhotoList from '@/components/atoms/ViewPhotoList.vue'
import { viewDetailedComponent, back } from '@/mixins/main'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'NewAccountsDocument',
  components: {
    NewAccountsInfo,
    NewAccountsEdit,
    ViewPhotoList
  },
  data () {
    return {
      sailorDocument: {},
      type: 'newAccounts',
      viewDetailedComponent,
      checkAccess,
      back
    }
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId,
      labelName: state => state.main.lang === 'en' ? 'name_eng' : 'name_ukr'
    }),
    documentID () {
      return this.$route.params.documentID
    }
  },
  mounted () {
    this.getVerificationAccount()
  },
  methods: {
    getVerificationAccount () {
      this.$api.get(`api/v1/sms_auth/list_verification/${this.documentID}/`).then(response => {
        if (response.code === 200) {
          response.data.behavior = { viewInfoBlock: true }
          response.data.sailorDateBirth = null
          this.sailorDocument = response.data
        }
      })
    }
  }
}
</script>
