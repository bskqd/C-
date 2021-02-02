<template>
  <div>
    <b-card class="vx-card" no-body>
      <StatementsSearch
        :newAccounts="true"
        :getReport="newAccountsSearch"
        report="newAccounts"
        ref="search"
      />
    </b-card>
    <b-card class="vx-card" no-body>
      <Table
        :items="items.results"
        :fields="fields"
        type="newAccounts"
        link="new-accounts-info"
      />
      <Paginate
        :current="items.current"
        :next="items.next"
        :prev="items.previous"
        :count="items.count"
        :changePage="getNewAccounts" />
    </b-card>
  </div>
</template>

<script>
import StatementsSearch from '@/components/molecules/ReportSearch/ReportSearch.vue'
import Paginate from '@/components/atoms/Paginate.vue'
import { checkAccess } from '@/mixins/permissions'
import { mapState } from 'vuex'

export default {
  name: 'NewAccounts',
  components: {
    StatementsSearch,
    Paginate
  },
  data () {
    return {
      fields: [
        { key: 'created_at',
          label: this.$i18n.t('createDate')
        },
        { key: 'fullName',
          label: this.$i18n.t('fullName'),
          sortable: true
        },
        { key: 'birthday',
          label: this.$i18n.t('dateBorn'),
          sortable: true
        },
        { key: 'phone',
          label: this.$i18n.t('phoneNumber'),
          sortable: true
        },
        { key: 'passport',
          label: this.$i18n.t('passport'),
          sortable: true
        },
        { key: 'inn',
          label: this.$i18n.t('taxNumber'),
          sortable: true
        },
        { key: 'status_document',
          label: this.$i18n.t('status'),
          sortable: true
        },
        { key: 'event',
          label: this.$i18n.t('actions'),
          class: 'mw-0'
        }
      ],
      params: new URLSearchParams({
        page_size: 20
      }),
      checkAccess
    }
  },
  beforeCreate () {
    this.$store.commit('setActivePage', { name: 'newAccounts', access: checkAccess('menuItem-verificationAccount') })
  },
  computed: {
    ...mapState({
      items: state => state.sailor.newAccounts
    })
  },
  mounted () {
    if (!this.items.length) this.getNewAccounts(null)
  },
  methods: {
    newAccountsSearch (sort, params) {
      this.params = params
      const url = `api/v1/sms_auth/list_verification/?${this.params}`
      this.$store.dispatch('getNewAccountsList', url)
    },

    getNewAccounts (link) {
      this.$store.dispatch('getNewAccountsList', link)
    }
  }
}
</script>
