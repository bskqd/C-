<template>
  <b-card header-tag="header">
    <div v-if="checkAccess('education', 'preVerification', sailorDocument)"
      class="col-12 text-left">
      <b>{{ $t('status') }}:</b>
      <multiselect
        v-model="status"
        :options="mappingStatuses"
        :searchable="true"
        :allow-empty="false"
        :label="langFields"
        track-by="id"
      />
    </div>
    <div>
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
          @click="checkAccess('education', 'preVerification', sailorDocument) ? saveNewStatus() : checkSave() "
          variant="success"
          class="mt-1"
        >
          {{ checkAccess('education', 'preVerification', sailorDocument) ? $t('save') : $t('setVerify') }}
        </b-button>
      </b-overlay>
    </div>
  </b-card>
</template>

<script src="./SailorEducationEditStatus.js"/>
