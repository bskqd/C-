<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList">
      <div class="w-50">
        <b>{{ $t('number') }}:</b>
        {{ sailorDocument.number }}
      </div>
      <div class="w-50">
        <b>{{ $t('port') }}:</b>
        {{ sailorDocument.port[labelName] }}
      </div>
      <div class="w-50">
        <b>{{ $t('payment') }}:</b>
        {{ sailorDocument.is_payed ? $t('isPayed') : $t('notPayed') }}
      </div>
      <div class="w-50">
        <b>{{ $t('receiveDoc') }}:</b>
        {{ sailorDocument.processingStatus[labelName] }}
      </div>
      <div
        v-if="!sailorDocument.is_continue"
        class="w-100"
      >
        <b>{{ $t('blankPayment') }}:</b>
        {{ sailorDocument.is_payed_blank ? $t('isPayed') : $t('notPayed') }}
      </div>
      <div class="w-33">
        <b>{{ $t('createDate') }}:</b>
        {{ sailorDocument.date_create }}
      </div>
      <div class="w-33">
        <b>{{ $t('dateModified') }}:</b>
        {{ sailorDocument.date_modified }}
      </div>
      <div class="w-33">
        <b>{{ $t('dataEvent') }}:</b>
        {{ sailorDocument.date_meeting }}
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

<script src="./SailorPassportStatementInfo.js" />
