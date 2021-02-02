<template>
  <b-card header-tag="header">
    <div>
      <div class="text-left col-12 mb-1">
        <b-button
          @click="saveDocument"
          class="text-bold-600"
        >
          {{ $t('saveDoc') }}
        </b-button>
<!--        <b-button-->
<!--          v-if="checkAccess('sailorSQCStatement', 'regeneration', sailorDocument)"-->
<!--          @click="regenerateApplication"-->
<!--          class="text-bold-600 ml-2"-->
<!--        >-->
<!--          {{ $t('regenerateDoc') }}-->
<!--        </b-button>-->
      </div>

      <div
        v-if="sailorDocument.status_dkk.exists_docs.length"
        class="text-left col-12 mt-1"
      >
        <SailorSQCStatementTableChanges
          v-if="checkAccess('backOffice') && sailorDocument.has_related_docs"
          :sailorDocument="sailorDocument"
        />
        <label class="text-bold-600" :class="{ 'ml-3': checkAccess('backOffice') }">
          {{ $t('existsDocs') }}:
        </label>
      </div>
      <b-table
        v-if="sailorDocument.status_dkk.exists_docs.length"
        :items="sailorDocument.status_dkk.exists_docs"
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
        v-if="sailorDocument.status_dkk.documents.length"
        class="text-left col-12 mt-1"
      >
        <label class="text-bold-600">
          {{ $t('notExistsDocs') }}:
        </label>
      </div>
      <b-table
        v-if="sailorDocument.status_dkk.documents.length"
        :items="sailorDocument.status_dkk.documents"
        :fields="fieldsApplication"
        :sort-by.sync="sortByA"
        :sort-desc.sync="sortDescA"
        striped
        hover
      />

      <div class="text-left col-12 mt-1">
        <label class="text-bold-600">
          {{ $t('experience') }}: {{ $t('noCheck') }}
        </label>
      </div>
      <b-table
        :items="sailorDocument.status_dkk.experince"
        :fields="fieldsExperience"
        :sort-by.sync="sortByA"
        :sort-desc.sync="sortDescA"
        striped
        hover
      >
        <template #cell(status)="row">
          <div
            class="experience-status"
            :class="getStatus(row.item.value ? 1 : 7)"
          >
            {{ getExperienceStatus(row) }}
          </div>
        </template>
      </b-table>

      <div class="seafarerInfoList text-left">
        <div>
          <label class="text-bold-600">
            {{ $t('number') }}:
          </label>
          {{ sailorDocument.number }}
        </div>

        <div class="w-50">
          <label class="text-bold-600">
            {{ $t('rank') }}:
          </label>
          {{ sailorDocument.rank[labelName] }}
        </div>

        <div class="w-50 p-0">
          <label class="text-bold-600">
            {{ $t('position') }}:
          </label>
          <span v-for="position in sailorDocument.list_positions" :key="position.id">
            {{ position[labelName] }};
          </span>
        </div>

        <div v-if="checkAccess('document-author-view') && sailorDocument.created_by">
          <div class="w-50 p-0">
            <label class="text-bold-600">
              {{ $t('recordAuthor') }}:
            </label>
            {{ sailorDocument.created_by.name }}
          </div>
          <div class="w-50 p-0">
            <label class="text-bold-600">
              {{ $t('createDate') }}:
            </label>
            {{ sailorDocument.created_by.date }}
          </div>
        </div>

        <div v-if="checkAccess('verification-author-view') && sailorDocument.approved_by">
          <div class="w-50 p-0">
            <label class="text-bold-600">
              {{ $t('approvedBy') }}:
            </label>
            {{ sailorDocument.approved_by.name }}
          </div>
          <div class="w-50 p-0">
            <label class="text-bold-600">
              {{ $t('approvedDate') }}:
            </label>
            {{ sailorDocument.approved_by.date }}
          </div>
        </div>

        <div class="w-50">
          <label class="text-bold-600">
            {{ $t('dataEvent') }}:
          </label>
          {{ getDateFormat(sailorDocument.date_meeting) }}
        </div>

        <div v-if="checkAccess('admin')">
          <label class="text-bold-600">
            {{ $t('typeDoc') }}:
          </label>
          {{ sailorDocument.is_continue ? $t('confirmation') : $t('appropriation') }}
        </div>

        <div>
          <label class="text-bold-600">
            {{ $t('payment') }}:
          </label>
          {{ sailorDocument.is_payed ? $t('isPayed') : $t('notPayed') }}
        </div>

        <div v-if="sailorDocument.is_etransport_pay && !sailorDocument.is_payed">
          <label class="text-bold-600 pr-1">
            {{ $t('etransportPayment') }}
          </label>
          <b-link
            href="https://sea.e-transport.gov.ua"
            target="_blank"
          >
          <span class="text-primary">
            (https://sea.e-transport.gov.ua)
          </span>
          </b-link>
        </div>

        <div class="w-100">
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

<script src="./SailorSQCStatementInfo.js" />
