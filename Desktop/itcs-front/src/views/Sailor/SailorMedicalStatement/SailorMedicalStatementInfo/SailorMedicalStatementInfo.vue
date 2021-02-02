<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList text-left">
      <div class="w-33">
        <b>{{ $t('createDate') }}:</b>
        {{ sailorDocument.date_create }}
      </div>
      <div class="w-33">
        <b>{{ $t('dateModified') }}:</b>
        {{ sailorDocument.date_modified }}
      </div>
      <div class="w-33">
        <b>{{ $t('dateReceipt') }}:</b>
        {{ getDateFormat(sailorDocument.date_meeting) }}
      </div>
      <div class="w-33">
        <b>{{ $t('medicalInstitution') }}:</b>
        {{ sailorDocument.medical_institution.value }}
      </div>
      <div class="w-33">
        <b>{{ $t('position') }}:</b>
        {{ sailorDocument.position[this.labelName] }}
      </div>
      <div class="w-33">
        <b>{{ $t('number') }}:</b>
        {{ sailorDocument.number }}
      </div>
      <div class="w-100">
        <b>{{ $t('payment') }}:</b>
        {{ sailorDocument.is_payed ? $t('isPayed') : $t('notPayed') }}
      </div>
      <div class="w-100">
        <b>{{ $t('status') }}:</b>
        <span :class="getStatus(sailorDocument.status_document.id)">
          {{ sailorDocument.status_document[this.labelName] }}
        </span>
      </div>
    </div>
  </b-card>
</template>

<script src="./SailorMedicalStatementInfo.js" />
