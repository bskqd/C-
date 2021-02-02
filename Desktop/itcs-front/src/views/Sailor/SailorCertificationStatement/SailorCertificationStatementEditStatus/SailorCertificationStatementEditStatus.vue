<template>
  <b-card header-tag="header">
    <div class="text-left">
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
        class="w-100 pl-1 pr-1"
      >
        <label>
          {{ $t('status') }}
        </label>
        <multiselect
          v-model="status"
          :searchable="true"
          :allow-empty="false"
          :placeholder="$t('status')"
          :options="mappingStatuses"
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
        class="w-100 text-center mt-2"
        spinner-small
      >
        <b-button
          @click="saveEditedStatus"
          variant="success"
        >
          {{ $t('save') }}
        </b-button>
      </b-overlay>
    </div>
  </b-card>
</template>

<script src="./SailorCertificationStatementEditStatus.js" />
