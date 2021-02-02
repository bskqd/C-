<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList">
      <div class="w-40">
        <b>{{ $t('nameUa') }}:</b>
        {{ sailorDocument.name_ukr }}
      </div>
      <div class="w-40">
        <b>{{ $t('nameEn') }}:</b>
        {{ sailorDocument.name_eng }}
      </div>
      <div class="w-20">
        <b>{{ $t('abbreviation') }}:</b>
        {{ sailorDocument.name_abbr }}
      </div>
      <div class="w-50">
        <b>{{ $t('contractNumber') }}:</b>
        {{ sailorDocument.contract_number }}
      </div>
      <div class="w-50">
        <b>{{ $t('contractDate') }}:</b>
        {{ getDateFormat(sailorDocument.contract_number_date) }}
      </div>
      <div class="w-50">
        <b>{{ $t('directorName') }}:</b>
        {{ sailorDocument.director_name }}
      </div>
      <div class="w-50">
        <b>{{ $t('position') }}:</b>
        {{ sailorDocument.director_position }}
      </div>
      <div class="w-50">
        <b>{{ $t('accountantFullName') }}:</b>
        {{ sailorDocument.accountant_full_name }}
      </div>
      <div class="w-50">
        <b>{{ $t('requisites') }}:</b>
        {{ sailorDocument.requisites }}
      </div>
      <div class="w-50">
        <b>{{ $t('bank') }}:</b>
        {{ sailorDocument.bank_name }}
      </div>
      <div class="w-50">
        <b>{{ $t('checkNumber') }}:</b>
        {{ sailorDocument.check_number }}
      </div>
      <div class="w-33">
        <b>{{ $t('edrpou') }}:</b>
        {{ sailorDocument.okpo }}
      </div>
      <div class="w-33">
        <b>{{ $t('vatNumber') }}:</b>
        {{ sailorDocument.nds_number }}
      </div>
      <div class="w-33">
        <b>{{ $t('mfoCode') }}:</b>
        {{ sailorDocument.mfo }}
      </div>
      <div class="w-100">
        <b>{{ $t('street') }}:</b>
        {{ sailorDocument.address }}
      </div>
      <div class="w-50">
        <b>{{ $t('email') }}:</b>
        {{ sailorDocument.email }}
      </div>
      <div class="w-50">
        <b>{{ $t('phoneNumber') }}:</b>
        {{ sailorDocument.phone }}
      </div>
      <div class="w-50">
        <b>{{ $t('status') }}:</b>
        <span :class="getPaymentStatus(!sailorDocument.is_disable)">
          {{ sailorDocument.is_disable ? $t('isDisable') : $t('isNotDisable') }}
        </span>
      </div>
      <div class="w-50">
        <b>{{ $t('isRed') }}:</b>
        {{ sailorDocument.is_red ? $t('yes') : $t('no') }}
      </div>
      <div
        v-if="sailorDocument.red_history && sailorDocument.red_history.length"
        class="w-100 pl-1 pr-1"
      >
        <b>{{ $t('redHistory') }}:</b>
        <b-table
          :items="sailorDocument.red_history"
          :fields="fields"
          class="text-center"
          striped
          hover
        >
          <template #cell(date_start)="row">
            {{ getDateFormat(row.item.date_start) }}
          </template>

          <template #cell(date_end)="row">
            {{ getDateFormat(row.item.date_end) }}
          </template>
        </b-table>
      </div>
    </div>
  </b-card>
</template>

<script src="./BackOfficeETIListInfo.js" />
