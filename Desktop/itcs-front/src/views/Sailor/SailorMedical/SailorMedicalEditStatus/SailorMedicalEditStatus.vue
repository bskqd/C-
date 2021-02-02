<template>
  <b-card header-tag="header">
    <div
      v-if="checkAccess('sailorMedical', 'preVerification', sailorDocument)"
      class="col-12 text-left"
    >
      <b>{{ $t('status') }}:</b>
      <multiselect
        v-model="status"
        :options="mappingStatuses"
        :searchable="true"
        :placeholder="$t('status')"
        :allow-empty="false"
        :label="labelName"
        track-by="id"
      />
    </div>
    <div class="text-center">
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
          @click="checkAccess('sailorMedical', 'preVerification', sailorDocument) ? saveNewStatus() : checkSave()"
          class="mt-1"
          variant="success"
        >
          {{ checkAccess('sailorMedical', 'preVerification', sailorDocument) ? $t('save') : $t('setVerify') }}
        </b-button>
      </b-overlay>
    </div>
  </b-card>
</template>

<script src="./SailorMedicalEditStatus.js" />
