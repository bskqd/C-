<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList text-left">
      <div>
        <b>{{ $t('number') }}:</b>
        <span>{{ sailorDocument.number }}</span>
      </div>
      <div>
        <b>{{ $t('qualification') }}:</b>
        <span >{{ sailorDocument.course[labelName] }}</span>
      </div>
      <div>
        <b>{{ $t('nameInstitution') }}:</b>
        <span>{{ sailorDocument.institution[labelName] }}</span>
      </div>
      <div>
        <b>{{ $t('meetingDate') }}:</b>
        <span v-if="sailorDocument.date_meeting">
          {{ getDateFormat(sailorDocument.date_meeting) }}
        </span>
      </div>
      <div class="w-50">
        <b>{{ $t('createDate') }}:</b>
        <span>{{ sailorDocument.date_create }}</span>
      </div>
      <div class="w-50">
        <b>{{ $t('dateModified') }}:</b>
        <span>{{ sailorDocument.date_modified }}</span>
      </div>
      <div class="w-33">
        <b>{{ $t('paymentPurpose') }}:</b>
        <span>{{ sailorDocument.requisites.payment_due }}</span>
      </div>
      <div class="w-33">
        <b>{{ $t('bank') }}:</b>
        <span>{{ sailorDocument.requisites.bank }}</span>
      </div>
      <div class="w-33">
        <b>{{ $t('amount') }}:</b>
        <span>{{ priceWithCommission }} {{ $t('uah') }}</span>
      </div>
      <div class="w-50">
        <b>{{ $t('payment') }}:</b>
        <b-button
          v-if="sailorDocument.institution.can_pay_platon && sailorDocument.requisites.amount && !sailorDocument.is_payed &&
           checkAccess('agent')"
          @click="createPayment"
          variant="primary"
          class="m-0"
        >
          {{ $t('pay') }}
        </b-button>
        <span v-else>{{ sailorDocument.is_payed ? $t('isPayed') : $t('notPayed') }}</span>
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

<script src="./SailorCertificationStatementInfo.js"/>
