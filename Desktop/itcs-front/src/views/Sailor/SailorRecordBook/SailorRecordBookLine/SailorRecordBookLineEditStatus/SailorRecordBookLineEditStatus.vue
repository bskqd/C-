<template>
  <b-card header-tag="header">
    <div v-if="checkAccess('serviceRecordBookLine', 'preVerification', sailorDocument)"
      class="col-12 text-left" >
      <label>
        {{ $t('status') }}
      </label>
      <multiselect
        v-model="status"
        :options="mappingStatusLine"
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
      class="w-100"
      spinner-small
    >
      <b-button
        @click="checkAccess('serviceRecordBookLine', 'preVerification', sailorDocument) ? saveNewStatus() : checkSave()"
        variant="success"
        class="mt-2"
      >
        {{ checkAccess('serviceRecordBookLine', 'preVerification', sailorDocument) ? $t('save') : $t('setVerify') }}
      </b-button>
    </b-overlay>
  </b-card>
</template>

<script src="./SailorRecordBookLineEditStatus.js"/>
