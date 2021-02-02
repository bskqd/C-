<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList text-left">
      <div class="w-100 pl-1 pr-1 mb-1 position-relative">
        <label>
          {{ $t('position') }}
          <span class="required-field-star">*</span>
        </label>
        <multiselect
          v-model="position"
          @close="$v.position.$touch()"
          :options="mappingPositions"
          :allow-empty="false"
          :searchable="true"
          :placeholder="$t('position')"
          :label="labelName"
          track-by="id"
        />
        <ValidationAlert
          v-if="$v.position.$dirty && !$v.position.required"
          :text="$t('emptyField')"
        />
      </div>

      <div class="w-100 p-0">
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
          @click="checkFields"
          variant="success"
        >
          {{ $t('save') }}
        </b-button>
      </b-overlay>
    </div>
  </b-card>
</template>

<script src="./SailorMedicalStatementEdit.js" />
