<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList">
      <div class="w-50">
        <b>{{ $t('createDate') }}:</b>
        {{ sailorDocument.date_created }}
      </div>
      <div class="w-50">
        <b>{{ $t('dateModified') }}:</b>
        {{ sailorDocument.date_modified }}
      </div>
      <div class="w-50">
        <b>{{ $t('delivery') }}:</b>
        {{ sailorDocument.delivery.post_service }}
      </div>
      <div class="w-50">
        <b>{{ $t('phoneNumber') }}:</b>
        {{ sailorDocument.delivery.phone_number }}
      </div>
      <div class="w-100">
        <b>{{ $t('department') }}:</b>
        {{ sailorDocument.delivery.area }}, {{ sailorDocument.delivery.city }}, {{ sailorDocument.delivery.warehouse }}
      </div>
      <div class="w-100">
        <b>{{ $t('payment') }}:</b>
        {{ sailorDocument.is_payed ? $t('isPayed') : $t('notPayed') }}
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

<script src="./SailorRecordBookStatementInfo.js"/>
