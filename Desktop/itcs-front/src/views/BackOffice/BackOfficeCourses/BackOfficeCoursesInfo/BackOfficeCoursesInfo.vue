<template>
  <div class="seafarerInfoList text-left">
    <div class="w-25">
      <b>{{ $t('numberProtocol') }}:</b>
      {{ sailorDocument.full_number_protocol }}
    </div>
    <div class="w-75">
      <b>{{ $t('course') }}:</b>
      {{ sailorDocument.course[labelName] }}
    </div>
    <div class="w-50">
      <b>{{ $t('dateEffective') }}:</b>
      {{ getDateFormat(sailorDocument.date_start) }}
    </div>
    <div class="w-50">
      <b>{{ $t('dateTermination') }}:</b>
      {{ getDateFormat(sailorDocument.date_end) }}
    </div>
    <div class="w-100">
      <span :class="getPaymentStatus(!sailorDocument.is_disable)">
        {{ sailorDocument.is_disable ? $t('isDisable') : $t('isNotDisable') }}
      </span>
    </div>
  </div>
</template>

<script src="./BackOfficeCoursesInfo.js" />
