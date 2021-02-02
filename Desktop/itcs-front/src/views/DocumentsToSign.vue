<template>
  <Page
    page="documentSign"
    :access="checkAccess('signDocument')">
    <div class="vx-card p-2">
    <Table
      :loader="tableLoader"
      :items="items.results"
      :fields="fields"
      :sortBy="sortBy"
      :sortDesc="sortDesc"
      :getDocuments="getDocumentsList"
      type="documentSign"/>
    <Paginate
      :current="items.current"
      :next="items.next"
      :prev="items.previous"
      :count="items.count"
      :changePage="getDocumentsList" />
    </div>
  </Page>
</template>

<script>
import Page from '@/components/layouts/Page.vue'
import Table from '@/components/layouts/Table/Table.vue'
import Paginate from '@/components/atoms/Paginate.vue'
import { checkAccess } from '@/mixins/permissions'

export default {
  name: 'DocumentsToSign',
  components: {
    Page,
    Table,
    Paginate
  },
  data () {
    return {
      checkAccess,
      filter: null,
      fields: [
        { key: 'sailor_full_name',
          label: this.$i18n.t('sailorName'),
          sortable: true
        },
        { key: 'protocol_number',
          label: this.$i18n.t('numberProtocol'),
          sortable: true
        },
        { key: 'signature_type',
          label: this.$i18n.t('typeSign'),
          sortable: true
        },
        { key: 'is_signatured',
          label: this.$i18n.t('statusSign'),
          sortable: true
        },
        { key: 'protocol_status',
          label: this.$i18n.t('status'),
          sortable: true
        },
        { key: 'event',
          label: this.$i18n.t('openSailor'),
          sortable: true
        }
      ],
      items: [],
      sortBy: 'name',
      sortDesc: false,
      tableLoader: true,
      buttonLoader: false
    }
  },
  mounted () {
    this.getDocumentsList()
  },
  methods: {
    getDocumentsList (link = '') {
      this.tableLoader = true
      let params = new URLSearchParams({
        page_size: 20
      })

      let url = `api/v1/signature/document_to_sign/?${params}`

      if (link) url = link

      this.$api.get(url).then(response => {
        this.tableLoader = false
        console.log(response)
        if (response.code === 200) {
          this.items = response.data
        }
      })
    }
  }
}
</script>
