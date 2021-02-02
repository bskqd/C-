<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList">
      <div
        v-if="!sailorDocument.is_payed"
        class="w-100 mb-1 pl-1 pr-1"
      >
        <label>
          {{ $t('payment') }}:
        </label>
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

      <div
        v-else
        class="w-100 mb-1 pl-1 pr-1"
      >
        <label>
          {{ $t('status') }}:
        </label>
        <multiselect
          v-model="status"
          :options="mappingStatuses"
          :placeholder="$t('status')"
          :searchable="true"
          :allow-empty="false"
          :label="labelName"
          track-by="id"
        />
      </div>

      <b-overlay
        :show="buttonLoader"
        spinner-variant="primary"
        opacity="0.65"
        blur="2px"
        variant="white"
        class="w-100 text-center"
        spinner-small
      >
        <b-button
          @click="updateApplicationStatus"
          variant="success"
        >
          {{ $t('save') }}
        </b-button>
      </b-overlay>
    </div>
  </b-card>

</template>

<script src="./SailorEducationStatementEditStatus.js" />
