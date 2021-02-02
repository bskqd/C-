<template>
  <Page
    page="verificationDocuments"
    :access="false">
    <div class="content-wrapper">
      <div class="router-view">
        <div class="vx-card p-2">
          <SearchInTable v-model="filter" />
          <b-overlay
            :show="tableLoader"
            spinner-variant="primary"
            opacity="0.65"
            blur="2px"
            variant="white"
          >
            <b-table
              :filter="filter"
              :items="items"
              :fields="fields"
              :sort-by.sync="sortBy"
              :sort-desc.sync="sortDesc"
              striped
              hover
            >
              <template #cell(id)="row">
                <b-button variant="outline-primary">
                  <a
                    :href="/sailor/ + row.item.id"
                    target="_blank"
                  >
                    <unicon
                      name="user-circle"
                      height="25px"
                      width="25px"
                      fill="#42627e"
                      class="cursor"
                    />
                  </a>
                </b-button>
              </template>
            </b-table>
          </b-overlay>
        </div>
      </div>
    </div>
  </Page>
</template>

<script>
import Page from '@/components/layouts/Page'
import SearchInTable from '@/components/atoms/SearchInTable.vue'
import { checkAccess } from '@/mixins/permissions'

export default {
  name: 'Verification',
  components: {
    Page,
    SearchInTable
  },
  data () {
    return {
      checkAccess,
      filter: null,
      fields: [],
      items: [],
      sortBy: 'nameSeafarer',
      sortDesc: false,
      tableLoader: true
    }
  },
  mounted () {
    this.getDocuments()
  },
  methods: {
    getDocuments () {
      this.tableLoader = true
      this.$api.get(`api/v1/verification/documents_to_verification/`).then(response => {
        if (response.code === 200) {
          this.items = response.data
        }
      })
    }
  }
}
</script>
