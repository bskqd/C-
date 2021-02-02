<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList text-left">
      <div class="d-flex text-left">
        <div>
          <b-button
            @click="saveDocument"
            class="text-bold-600 mr-1"
          >
            {{ $t('saveDoc') }}
          </b-button>
        </div>
        <div>
          <b-button
            v-if="!sailorDocument.blank_strict_report"
            @click="showStatementSaving = !showStatementSaving"
            class="text-bold-600"
          >
            {{ $t('saveStatement') }}
          </b-button>
        </div>
      </div>

      <div v-if="showStatementSaving" class="d-flex">
        <label class="w-100">
          {{ $t('strictBlank')}}
        </label>
        <div class="w-50 p-0">
          <b-input
            v-model="strictBlank"
            :placeholder="$t('strictBlank')"
            type="number"
          />
        </div>
        <div>
          <b-button
            @click="saveApplicationDocument()"
            class="text-bold-600 ml-3"
          >
            {{ $t('saveStatement') }}
          </b-button>
        </div>
      </div>

      <div class="w-100 mt-1 text-left">
        <label class="text-bold-600">
          {{ $t('number') }}:
        </label>
        {{ sailorDocument.name_book }}
      </div>

      <div
        v-if="sailorDocument.waibill_number"
        class="w-100 text-left mt-1"
      >
        <label class="mr-1 text-bold-600">
          {{ $t('wayBillNumber') }}:
        </label>
        {{ sailorDocument.waibill_number }}
      </div>

      <div class="w-100 p-0 text-left mt-1">
        <div class="w-50">
          <label class="text-bold-600">
            {{ $t('dateIssue') }}:
          </label>
          {{ getDateFormat(sailorDocument.date_issued) }}
        </div>

        <div class="w-50">
          <label class="text-bold-600">
            {{ $t('affiliate') }}:
          </label>
          {{ sailorDocument.branch_office[labelName] }}
        </div>
      </div>

      <div
        v-if="checkAccess('document-author-view') && sailorDocument.created_by"
        class="w-100 p-0"
      >
        <div class="w-50">
          <label class="text-bold-600">
            {{ $t('recordAuthor') }}:
          </label>
          {{ sailorDocument.created_by.name }}
        </div>
        <div class="w-50">
          <label class="text-bold-600">
            {{ $t('createDate') }}:
          </label>
          {{ sailorDocument.created_by.date }}
        </div>
      </div>
      <div
        v-if="checkAccess('verification-author-view') && sailorDocument.verificated_by"
        class="w-100 p-0"
      >
        <div class="w-50">
          <label class="text-bold-600">
            {{ $t('verifier') }}:
          </label>
          {{ sailorDocument.verificated_by.name }}
        </div>
        <div class="w-50">
          <label class="text-bold-600">
            {{ $t('verificationDate') }}:
          </label>
          {{ sailorDocument.verificated_by.date }}
        </div>
     </div>

      <div class="w-100 mt-1">
        <label class="text-bold-600">
          {{ $t('status') }}:
        </label>
        <span :class="getStatus(sailorDocument.status.id)">
          {{ sailorDocument.status[labelName] }}
        </span>
      </div>
    </div>

    <SailorRecordBookLine :serviceRecordBookId="sailorDocument.id" />
  </b-card>
</template>

<script src="./SailorRecordBookInfo.js"/>
