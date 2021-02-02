<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList">
      <div class="w-100">
        <b>{{ $t('fullNameBefore') }}:</b>
        {{ sailorDocument[`old_last_${labelName}`] }} {{ sailorDocument[`old_first_${labelName}`] }} {{ sailorDocument[`old_middle_${labelName}`] }}
      </div>
      <div class="w-100">
        <b>{{ $t('fullNameAfter') }}:</b>
        {{ sailorDocument[`last_${labelName}`] }} {{ sailorDocument[`first_${labelName}`] }} {{ sailorDocument[`middle_${labelName}`] }}
      </div>
      <div class="w-50">
        <b>{{ $t('dateModified') }}:</b>
        {{ getDateFormat(sailorDocument.change_date) }}
      </div>
      <div class="w-50">
        <b>{{ $t('createDate') }}:</b>
        {{ getDateFormat(sailorDocument.date_create) }}
      </div>
    </div>
  </b-card>
</template>

<script src="./SailorFullNameChangesInfo.js" />
