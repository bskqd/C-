<template>
  <div class="seafarerInfoList">
    <div class="w-100">
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
    <div class="w-50">
      <b>{{ $t('price') }}:</b>
      {{ sailorDocument.price }}
    </div>
    <div class="w-50">
      <b>{{ $t('priceForm') }}:</b>
      {{ sailorDocument.type_of_form === 'First' ? $t('firstForm') : $t('secondForm') }}
    </div>
  </div>
</template>

<script src="./BackOfficeCoursePricesInfo.js" />
