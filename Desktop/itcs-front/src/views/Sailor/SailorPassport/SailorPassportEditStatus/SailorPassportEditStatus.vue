<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList">
      <div v-if="checkAccess('sailorPassport', 'preVerification', sailorDocument)">
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
            @click="checkAccess('sailorPassport', 'preVerification', sailorDocument) ? saveNewStatus() : checkSave()"
            variant="success"
          >
            {{ checkAccess('sailorPassport', 'preVerification', sailorDocument) ? $t('save') : $t('setVerify') }}
          </b-button>
        </b-overlay>
      </div>
    </div>
  </b-card>
</template>

<script src="./SailorPassportEditStatus.js"/>
