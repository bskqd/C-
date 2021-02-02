<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList text-left">
      <div class="w-100 mb-1 position-relative">
        <label>
          {{ $t('qualification') }}
          <span class="required-field-star">*</span>
        </label>
        <multiselect
          v-model="qualification"
          :options="mappingQualification"
          :allow-empty="false"
          :searchable="true"
          :placeholder="$t('qualification')"
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
          @click="editAdvanceTrainingApplication"
          variant="success"
        >
          {{ $t('save') }}
        </b-button>
      </b-overlay>
    </div>
  </b-card>
</template>

<script src="./SailorEducationStatementEdit.js" />
