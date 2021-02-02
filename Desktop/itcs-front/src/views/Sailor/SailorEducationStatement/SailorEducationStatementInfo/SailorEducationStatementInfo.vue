<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList text-left">
      <div class="w-25">
        <b>{{ $t('createDate') }}:</b>
        {{ sailorDocument.date_create }}
      </div>
      <div class="w-25">
        <b>{{ $t('dateModified') }}:</b>
        {{ sailorDocument.date_modified }}
      </div>
      <div class="w-25">
        <b>{{ $t('dateStartEdu') }}:</b>
        {{ getDateFormat(sailorDocument.date_meeting) }}
      </div>
      <div class="w-25">
        <b>{{ $t('dateEndEdu') }}:</b>
        {{ getDateFormat(sailorDocument.date_end_meeting) }}
      </div>
      <div class="w-33">
        <b>{{ $t('qualification') }}:</b>
        {{ sailorDocument.level_qualification[labelName] }}
      </div>
      <div class="w-33">
        <b>{{ $t('nameInstitution') }}:</b>
        {{ sailorDocument.educational_institution[labelName] }}
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
          {{ sailorDocument.status_document[labelName] }}
        </span>
      </div>
    </div>
  </b-card>
</template>

<script src="./SailorEducationStatementInfo.js" />
