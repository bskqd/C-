<template>
  <b-card header-tag="header">
    <div>
      <div
        v-if="sailorDocument.demand_dkk.exists_docs.length"
        class="text-left col-12 mt-1"
      >
        <label class="text-bold-600">
          {{ $t('existsDocs') }}:
        </label>
      </div>
      <b-table
        v-if="sailorDocument.demand_dkk.exists_docs.length"
        :items="sailorDocument.demand_dkk.exists_docs"
        :fields="fieldsExistDocuments"
        :sort-by.sync="sortByA"
        :sort-desc.sync="sortDescA"
        striped
        hover
      >
        <template #cell(status)="row">
          <span :class="getStatus(row.item.is_verification ? 34 : 1)">
            {{ row.item.is_verification ? $t('notVerified') : $t('verified') }}
          </span>
        </template>
      </b-table>

      <div
        v-if="sailorDocument.demand_dkk.documents.length"
        class="text-left col-12 mt-1"
      >
        <label class="text-bold-600">
          {{ $t('notExistsDocs') }}:
        </label>
      </div>
      <b-table
        v-if="sailorDocument.demand_dkk.documents.length"
        :items="sailorDocument.demand_dkk.documents"
        :fields="fieldsApplication"
        :sort-by.sync="sortByA"
        :sort-desc.sync="sortDescA"
        striped
        hover
      />

      <div class="text-left flex-row-sb">
        <div class="col-6">
          <label class="text-bold-600">
            {{ $t('rank') }}:
          </label>
          {{ sailorDocument.rank[labelName] }}
        </div>
        <div class="col-6">
          <label class="text-bold-600">
            {{ $t('position') }}:
          </label>
          <span v-for="position in sailorDocument.list_positions" :key="position.id">
            {{ position[labelName] }};
          </span>
        </div>
      </div>

      <div class="text-left flex-row-sb">
        <div class="col-6">
          <label class="text-bold-600">
            {{ $t('createDate') }}:
          </label>
          {{ sailorDocument.date_create }}
        </div>
        <div class="col-6">
          <label class="text-bold-600">
            {{ $t('dateModified') }}:
          </label>
          {{ sailorDocument.date_modified}}
        </div>
      </div>

      <div class="text-left flex-row-sb">
        <div class="col-6">
          <label class="text-bold-600">
            {{ $t('status') }}:
          </label>
          <span :class="getStatus(sailorDocument.status_document.id)">
            {{ sailorDocument.status_document[labelName] }}
          </span>
        </div>
      </div>
    </div>
  </b-card>
</template>

<script src="./SailorSQCWishesInfo.js" />
