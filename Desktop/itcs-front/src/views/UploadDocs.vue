<template>
  <Page
    page="uploadDocs"
    :access="checkAccess('uploadDocument')">
    <div class="vx-card p-2">
      <div class="card-header pb-1">
        <div class="card-title">
          <h4 class="text-center mb-2">{{ $t('uploadDocs') }}</h4>
        </div>
      </div>
      <b-form @submit.prevent="validateForm">
        <div class="pageList p-0">
          <div class="w-50">
            <b>{{ $t('typeDoc') }}</b>
            <multiselect
              v-model="dataForm.typeDocument"
              @close="$v.dataForm.typeDocument.$touch()"
              :options="typeDocs"
              :searchable="true"
              :placeholder="$t('typeDoc')"
              :class="{ 'is-invalid': ($v.dataForm.typeDocument.$dirty && !$v.dataForm.typeDocument.required) }"
              :label="labelName"
              track-by="id"
            >
            </multiselect>
            <ValidationAlert
              v-if="($v.dataForm.typeDocument.$dirty && !$v.dataForm.typeDocument.required)"
              :text="$t('emptyField')"
            />
          </div>
          <div class="w-50">
            <b>{{ $t('nameInstitution') }}</b>
            <multiselect
              v-model="dataForm.nameInstitution"
              @close="$v.dataForm.nameInstitution.$touch()"
              :options="mappingInstitution(dataForm.typeDocument)"
              :searchable="true"
              :placeholder="$t('nameInstitution')"
              :class="{ 'is-invalid': ($v.dataForm.nameInstitution.$dirty && !$v.dataForm.nameInstitution.required) }"
              :label="labelName"
              track-by="id"
            >
            <span slot="noOptions">
              {{ $t('selectTypeDocument') }}
            </span>
            </multiselect>
            <ValidationAlert
              v-if="($v.dataForm.nameInstitution.$dirty && !$v.dataForm.nameInstitution.required)"
              :text="$t('emptyField')"
            />
          </div>
          <div class="w-100">
            <b>{{ $t('qualification') }}</b>
            <multiselect
              v-model="dataForm.qualification"
              @close="$v.dataForm.qualification.$touch()"
              :options="mappingQualification(dataForm.typeDocument)"
              :searchable="true"
              :placeholder="$t('qualification')"
              :class="{ 'is-invalid': ($v.dataForm.qualification.$dirty && !$v.dataForm.qualification.required) }"
              :label="labelName"
              track-by="id"
            >
            </multiselect>
            <ValidationAlert
              v-if="($v.dataForm.qualification.$dirty && !$v.dataForm.qualification.required)"
              :text="$t('emptyField')"
            />
          </div>
          <div>
            <b>{{ $t('excelFile') }}</b>
            <b-form-file
              v-model="dataForm.documentExel"
              @change="$v.dataForm.documentExel.$touch()"
              :placeholder="$t('excelFile')"
              :browse-text="$t('browse')"
              :class="{ 'border border-danger rounded h-100':
              ($v.dataForm.documentExel.$dirty && !$v.dataForm.documentExel.required) }"
              accept="application/excel, application/x-excel, application/x-msexcel, application/vnd.ms-excel, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            >
            </b-form-file>
            <ValidationAlert
              v-if="($v.dataForm.documentExel.$dirty && !$v.dataForm.documentExel.required)"
              :text="$t('emptyField')"
            />
          </div>
        </div>
        <div class="text-center">
          <b-overlay
            :show="saveButtonLoader"
            spinner-variant="primary"
            opacity="0.65"
            blur="2px"
            variant="white"
            class="w-100"
            spinner-small
          >
            <b-button
              type="submit"
              variant="success"
              class="mt-1"
            >
              {{ $t('save') }}
            </b-button>
          </b-overlay>
        </div>
      </b-form>
      <Table
        :loader="tableLoader"
        :items="items.results"
        :fields="fields"
        :sortBy="sortBy"
        :sortDesc="sortDesc"
        type="documentSign"/>
    </div>
  </Page>
</template>

<script>
import Page from '@/components/layouts/Page.vue'
import Table from '@/components/layouts/Table/Table.vue'
import { checkAccess } from '@/mixins/permissions'
import ValidationAlert from '@/components/atoms/FormComponents/ValidationAlert/ValidationAlert.vue'
import { required } from 'vuelidate/lib/validators'
import { mapGetters, mapState } from 'vuex'

function formFieldsInitialState () {
  return {
    nameInstitution: null,
    typeDocument: null,
    documentExel: null,
    qualification: null
  }
}

export default {
  name: 'UploadDocs',
  components: {
    Page,
    Table,
    ValidationAlert
  },
  data () {
    return {
      checkAccess,
      dataForm: formFieldsInitialState(),
      items: [],
      sortBy: 'numberDocument',
      sortDesc: true,
      filterMain: null,
      tableLoader: false,
      saveButtonLoader: false,
      fields: [
        { key: 'number_document',
          label: this.$i18n.t('docNumber'),
          sortable: true
        },
        { key: 'sailor_fio',
          label: this.$i18n.t('fullName'),
          sortable: true
        },
        { key: 'is_add',
          label: this.$i18n.t('addedFile'),
          sortable: true
        },
        { key: 'event',
          label: this.$i18n.t('openSailor'),
          sortable: false
        }
      ]
    }
  },
  validations: {
    dataForm: {
      nameInstitution: { required },
      typeDocument: { required },
      documentExel: { required },
      qualification: { required }
    }
  },
  computed: {
    ...mapState({
      labelName: state => (state.main.lang === 'en') ? 'name_eng' : 'name_ukr',
      qualificationExist: state => state.directory.qualificationLevels.length,
      institutions: state => state.directory.institution
    }),
    ...mapGetters({
      typeDocs: 'typeDocsForUpload'
    })
  },
  methods: {
    mappingInstitution (typeDocument) {
      if (typeDocument !== null) {
        return this.$store.getters.institutionByType(typeDocument.id)
      } else return []
    },

    mappingQualification (typeDoc) {
      if (typeDoc !== null) {
        switch (typeDoc.id) {
          case 2:
            // 3 - Qualification diploma
            return this.$store.getters.qualificationById(3)
          case 3:
            // 2 - Certificate of Advanced Studies
            return this.$store.getters.qualificationById(2)
        }
      } else {
        this.dataForm.qualification = null
        return []
      }
    },

    validateForm () {
      if (this.$v.$invalid) {
        this.$v.$touch()
      } else {
        this.uploadExelDocs()
      }
    },

    uploadExelDocs () {
      this.saveButtonLoader = true

      let dataBody = new FormData()
      dataBody.append('type_document', this.dataForm.typeDocument.id)
      dataBody.append('qualification_id', this.dataForm.qualification.id)
      dataBody.append('nz_id', this.dataForm.nameInstitution.id)
      dataBody.append('file', this.dataForm.documentExel)

      this.$api.post('api/v1/sailor/load_education/', dataBody).then(response => {
        this.saveButtonLoader = false
        if (response.code === 201) {
          this.$notification.success(this, this.$i18n.t('uploadedFile'))
          this.items = response.data
          this.tableLoader = false
          this.$data.dataForm = formFieldsInitialState()
          this.$v.$reset()
        }
      })
    }
  }
}
</script>
