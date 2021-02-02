<template>
  <b-card header-tag="header">
    <div
      v-if="checkAccess('serviceRecordBook', 'preVerification', sailorDocument)"
      class="flex-row-sb text-left mt-2"
    >
      <div class="col-12">
        <label class="text-bold-600">
          {{ $t('status') }}:
        </label>
        <multiselect
          v-model="status"
          :options="mappingStatuses"
          :searchable="true"
          :allow-empty="false"
          :label="labelName"
          track-by="id"
        />
      </div>
    </div>
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
        @click="checkAccess('serviceRecordBook', 'preVerification', sailorDocument) ? saveNewStatus() : checkSave()"
        variant="success"
        class="mt-2"
      >
        {{ checkAccess('serviceRecordBook', 'preVerification', sailorDocument) ? $t('save') : $t('setVerify') }}
      </b-button>
    </b-overlay>
  </b-card>
</template>

<script src="./SailorRecordBookEditStatus.js"/>
