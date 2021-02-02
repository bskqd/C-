<template>
  <div class="seafarerInfoList">
    <div class="w-50">
      <b>{{ $t('dateEffective') }}:</b>
      {{ getDateFormat(sailorDocument.date_start) }}
    </div>
    <div class="w-50">
      <b>{{ $t('dateEnd') }}:</b>
      {{ getDateFormat(sailorDocument.date_end) }}
    </div>
    <div class="w-50">
      <b>{{ $t('etiPercent') }}:</b>
      {{ sailorDocument.percent_of_eti }}
    </div>
    <div class="w-50">
      <b>{{ $t('profitPercent') }}:</b>
      {{ sailorDocument.percent_of_profit }}
    </div>
  </div>
</template>

<script src="./BackOfficeCoefficientsInfo.js" />
