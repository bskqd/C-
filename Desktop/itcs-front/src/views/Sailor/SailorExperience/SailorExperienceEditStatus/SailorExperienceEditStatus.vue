<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList">
      <div
        v-if="checkAccess('experience', 'preVerification', sailorDocument)"
        class="p-0 col-12"
      >
        <label class="text-bold-600">
          {{ $t('status') }}:
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
            @click="checkAccess('experience', 'preVerification', sailorDocument) ? saveNewStatus() : checkSave()"
            variant="success"
          >
            {{ checkAccess('experience', 'preVerification', sailorDocument) ? $t('save') : $t('setVerify') }}
          </b-button>
        </b-overlay>
      </div>
    </div>
  </b-card>
</template>

<script src="./SailorExperienceEditStatus.js"/>
