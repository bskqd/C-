<template>
  <b-card header-tag="header">
    <div class="text-left">
      <div class="w-100 mb-1 pl-1 pr-1">
        <Rating
          v-if="showSetRating"
          :visible="showSetRating"
          :statementId="sailorDocument.id"
          :viewEditOnly="true"
          :readonly="true"
        />
      </div>

      <div
        v-if="!this.sailorDocument.is_payed && sailorDocument.rank"
        class="w-100 mb-1 pl-1 pr-1"
      >
        <label>
          {{ $t('model-SailorPassport') }}
        </label>
        <multiselect
          v-model="seafarerPassport"
          :options="processingOptionsList"
          :allow-empty="false"
          :searchable="true"
          :placeholder="$t('model-SailorPassport')"
          :label="labelName"
          track-by="id"
        />
      </div>

      <div class="w-100 mb-1 pl-1 pr-1">
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

      <div>
        <FileDropZone ref="mediaContent" class="w-100 p-0" />
      </div>

      <b-overlay
        :show="buttonLoader"
        spinner-variant="primary"
        opacity="0.65"
        blur="2px"
        variant="white"
        class="w-100 text-center mt-1"
        spinner-small
      >
        <b-button
          @click="updatePositionApplication"
          variant="success"
        >
          {{ $t('save') }}
        </b-button>
      </b-overlay>
    </div>
  </b-card>
</template>

<script src="./SailorPositionStatementEdit.js" />

<style scoped>

</style>
