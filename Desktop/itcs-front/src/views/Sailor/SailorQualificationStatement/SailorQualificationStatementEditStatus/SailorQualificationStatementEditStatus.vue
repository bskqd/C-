<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList">
      <div
        v-if="checkAccess('qualificationStatement', 'viewPayment', sailorDocument)"
        class="text-left flex-row-sb form-group"
      >
        <b>{{ $t('payment') }}:</b>
        <multiselect
          v-model="payment"
          :options="paymentStatus"
          :placeholder="$t('payment')"
          :searchable="true"
          :allow-empty="false"
          :label="labelName"
          track-by="id"
        />
      </div>
      <div v-if="checkAccess('qualificationStatement', 'viewStatus', sailorDocument)">
        <b>{{ $t('status') }}:</b>
        <multiselect
          v-model="status"
          :options="mappingStatuses"
          :searchable="true"
          :placeholder="$t('solution')"
          :allow-empty="false"
          :label="labelName"
          track-by="id"
        />
      </div>
      <div
        v-if="checkAccess('qualificationStatement', 'maradVerification', sailorDocument)"
        class="text-left mt-2"
      >
        <FileDropZone ref="mediaContent" class="w-100 p-0" />
      </div>
      <div
        v-if="sailorDocument.status_dkk.have_all_docs || sailorDocument.is_payed ||
         checkAccess('qualificationStatement', 'maradVerification', sailorDocument)"
        class="text-center"
      >
        <b-overlay
          :show="buttonLoader"
          spinner-variant="primary"
          opacity="0.65"
          blur="2px"
          variant="white"
          class="w-100"
          spinner-small
        >
          <b-button
            @click="saveSolution"
            variant="success"
          >
            {{ checkAccess('qualificationStatement', 'maradVerification', sailorDocument) ? $t('setVerify') : $t('save') }}
          </b-button>
        </b-overlay>
      </div>
    </div>
  </b-card>
</template>

<script src="./SailorQualificationStatementEditStatus.js" />
