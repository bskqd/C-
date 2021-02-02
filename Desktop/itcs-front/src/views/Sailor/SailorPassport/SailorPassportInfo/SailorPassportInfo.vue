<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList">
      <div class="w-50">
        <b>{{ $t('country') }}:</b>
        {{ sailorDocument.country[labelValue] }}
      </div>
      <div class="w-50">
        <b>{{ $t('port') }}:</b>
        {{ sailorDocument.country.id === 2 ? sailorDocument.port[labelName] : sailorDocument.other_port }}
      </div>
      <div class="w-50">
        <b>{{ $t('number') }}:</b>
        {{ sailorDocument.number_document }}
      </div>
      <div class="w-50">
        <b>{{ $t('captain') }}:</b>
        {{ sailorDocument.captain }}
      </div>
      <div class="w-50">
        <b>{{ $t('dateIssue') }}:</b>
        {{ getDateFormat(sailorDocument.date_start) }}
      </div>
      <div class="w-50">
        <b>{{ $t('dateTermValid') }}:</b>
        {{ getDateFormat(sailorDocument.date_end) }}
      </div>
      <div
        v-if="sailorDocument.date_renewal"
        class="w-100"
      >
        <b>{{ $t('dateRenewal') }}:</b>
        {{ getDateFormat(sailorDocument.date_renewal) }}
      </div>
      <div
        v-if="sailorDocument.created_by"
        class="w-50"
      >
        <b>{{ $t('recordAuthor') }}:</b>
        {{ sailorDocument.created_by.name }}
      </div>
      <div
        v-if="sailorDocument.created_by"
        class="w-50"
      >
        <b>{{ $t('createDate') }}:</b>
        {{ sailorDocument.created_by.date }}
      </div>
      <div
        v-if="sailorDocument.verificated_by"
        class="w-50"
      >
        <b>{{ $t('verifier') }}:</b>
        {{ sailorDocument.verificated_by.name }}
      </div>
      <div
        v-if="sailorDocument.verificated_by"
        class="w-50"
      >
        <b>{{ $t('verificationDate') }}:</b>
        {{ sailorDocument.verificated_by.date }}
      </div>
      <div class="w-100">
        <b>{{ $t('status') }}:</b>
        <span :class="getStatus(sailorDocument.status_document.id)">
        {{ sailorDocument.status_document[labelName] }}
      </span>
      </div>
    </div>
  </b-card>
</template>

<script src="./SailorPassportInfo.js"/>
